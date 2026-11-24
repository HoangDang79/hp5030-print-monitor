#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import os
import re
import ssl
import subprocess
from urllib.parse import urlparse
import urllib.request

PRINTER_NAME = "HP_ENVY_5000_series"
INTERVAL_DAYS = 21
REMINDER_COOLDOWN_HOURS = 24

HOME = Path.home()
STATE_FILE = HOME / ".printer_keepalive_last_run"
PAGECOUNT_FILE = HOME / ".printer_keepalive_pagecount"
REMINDER_FILE = HOME / ".printer_keepalive_last_fail_notify"
NOTIFY_MSG_FILE = HOME / ".printer_keepalive_notify.txt"
NOTIFIER_APP = HOME / ".local/bin/HP5030Notifier.app"
LOG_FILE = HOME / ".printer_keepalive.log"
CUPS_PAGE_LOG = Path("/var/log/cups/page_log")
MAX_LOG_LINES = 500


def log(status: str, message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{status}] {message}\n"
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines(keepends=True) if LOG_FILE.exists() else []
    lines.append(entry)
    LOG_FILE.write_text("".join(lines[-MAX_LOG_LINES:]), encoding="utf-8")


def notify(title: str, message: str, with_sound: bool = True) -> None:
    sound_flag = "sound" if with_sound else "silent"
    NOTIFY_MSG_FILE.write_text(f"{title}|||{message}|||{sound_flag}", encoding="utf-8")
    if NOTIFIER_APP.exists():
        subprocess.run(["/usr/bin/open", "-W", "-a", str(NOTIFIER_APP)], check=False)


def send_reminder_if_due(now: datetime, days_since: int) -> None:
    last_rem: datetime | None = None
    if REMINDER_FILE.exists():
        try:
            last_rem = datetime.fromisoformat(REMINDER_FILE.read_text(encoding="utf-8").strip())
        except (ValueError, OSError):
            last_rem = None

    if last_rem is None or (now - last_rem) >= timedelta(hours=REMINDER_COOLDOWN_HOURS):
        notify(
            "HP 5030 Druckkopf-Erinnerung",
            f"Seit {days_since} Tagen nicht gedruckt – bitte kurz eine Farbseite drucken.",
            with_sound=True,
        )
        tmp = REMINDER_FILE.with_suffix(".tmp")
        tmp.write_text(now.isoformat() + "\n", encoding="utf-8")
        tmp.replace(REMINDER_FILE)
        log("ERINNERUNG_GESENDET", f"Benachrichtigung gesendet ({days_since} Tage ohne Druck).")


def clear_reminder_state() -> None:
    if REMINDER_FILE.exists():
        try:
            REMINDER_FILE.unlink()
        except OSError:
            pass


def get_last_run() -> datetime | None:
    if not STATE_FILE.exists():
        return None
    try:
        return datetime.fromisoformat(STATE_FILE.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return None


def save_last_run(dt: datetime) -> None:
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(dt.isoformat() + "\n", encoding="utf-8")
    tmp.replace(STATE_FILE)


def get_saved_pagecount() -> int | None:
    if not PAGECOUNT_FILE.exists():
        return None
    try:
        return int(PAGECOUNT_FILE.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return None


def save_pagecount(count: int) -> None:
    tmp = PAGECOUNT_FILE.with_suffix(".tmp")
    tmp.write_text(f"{count}\n", encoding="utf-8")
    tmp.replace(PAGECOUNT_FILE)


def discover_ipp_uri(printer: str) -> str | None:
    res_v = subprocess.run(["/usr/bin/lpstat", "-v", printer], capture_output=True, text=True, check=False)
    if res_v.returncode == 0:
        for line in res_v.stdout.splitlines():
            if ":" in line:
                uri = line.split(":", 1)[1].strip()
                if uri.startswith(("ipp://", "ipps://")):
                    return uri

    res_find = subprocess.run(["/usr/bin/ippfind", "-T", "6"], capture_output=True, text=True, check=False)
    if res_find.returncode == 0 and res_find.stdout.strip():
        uris = [u.strip() for u in res_find.stdout.splitlines() if u.strip()]
        for u in uris:
            if any(k in u.lower() for k in ("5000", "5030", "hp")):
                return u
        return uris[0]
    return None


def query_hp_ledm_xml_count(hostname: str) -> int | None:
    clean_host = hostname.rstrip(".")
    ssl_ctx = ssl._create_unverified_context()
    for scheme in ("http", "https"):
        url = f"{scheme}://{clean_host}/DevMgmt/ProductUsageDyn.xml"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            opener = urllib.request.urlopen(req, timeout=4, context=ssl_ctx) if scheme == "https" else urllib.request.urlopen(req, timeout=4)
            with opener as resp:
                xml_text = resp.read().decode("utf-8", errors="ignore")
                for tag in ("TotalImpressions", "PagesPrinted"):
                    match = re.search(rf"<(?:\w+:)?{tag}[^>]*>(\d+)</(?:\w+:)?{tag}>", xml_text)
                    if match:
                        return int(match.group(1))
        except Exception:
            continue
    return None


def get_printer_hardware_pagecount(printer: str) -> int | None:
    ipp_uri = discover_ipp_uri(printer)
    if not ipp_uri:
        return None

    ipp_request = (
        "{\n"
        "  OPERATION Get-Printer-Attributes\n"
        "  GROUP operation-attributes-tag\n"
        "  ATTR charset attributes-charset utf-8\n"
        "  ATTR language attributes-natural-language en\n"
        "  ATTR uri printer-uri $uri\n"
        "  ATTR keyword requested-attributes printer-impressions-completed,pages-completed,job-impressions-completed\n"
        "}\n"
    )
    res = subprocess.run(
        ["/usr/bin/ipptool", "-T", "6", "-tv", ipp_uri, "-"],
        input=ipp_request,
        capture_output=True,
        text=True,
        check=False,
    )
    if res.stdout:
        for attr in ("printer-impressions-completed", "pages-completed", "job-impressions-completed"):
            match = re.search(rf"{attr}\s*\([^)]+\)\s*=\s*(\d+)", res.stdout)
            if match:
                return int(match.group(1))

    parsed = urlparse(ipp_uri)
    if parsed.hostname:
        return query_hp_ledm_xml_count(parsed.hostname)
    return None


def get_latest_cups_print_time(printer: str) -> datetime | None:
    latest: datetime | None = None
    env = os.environ.copy()
    env["LC_ALL"] = "C"
    res = subprocess.run(["/usr/bin/lpstat", "-W", "completed", "-o", printer], capture_output=True, text=True, env=env, check=False)
    if res.returncode == 0 and res.stdout.strip():
        for line in res.stdout.splitlines():
            parts = line.split()
            if len(parts) < 8:
                continue
            date_str = " ".join(parts[3:])
            tokens = date_str.split()
            for strip_tz in (True, False):
                candidate = " ".join(tokens[:-1]) if (strip_tz and len(tokens) > 4) else date_str
                for fmt in ("%a %d %b %Y %I:%M:%S %p", "%a %d %b %Y %H:%M:%S", "%a %b %d %H:%M:%S %Y", "%a %b %d %I:%M:%S %p %Y"):
                    try:
                        parsed = datetime.strptime(candidate, fmt)
                        if latest is None or parsed > latest:
                            latest = parsed
                        break
                    except ValueError:
                        continue

    if CUPS_PAGE_LOG.exists():
        try:
            for line in CUPS_PAGE_LOG.read_text(encoding="utf-8", errors="ignore").splitlines():
                if not line.startswith(printer + " "):
                    continue
                match = re.search(r"\[(\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2})\s+[+-]\d{4}\]", line)
                if match:
                    parsed = datetime.strptime(match.group(1), "%d/%b/%Y:%H:%M:%S")
                    if latest is None or parsed > latest:
                        latest = parsed
        except OSError:
            pass

    return latest


def main() -> None:
    now = datetime.now()
    last_run = get_last_run()
    if last_run is None:
        save_last_run(now)
        last_run = now

    hw_count = get_printer_hardware_pagecount(PRINTER_NAME)
    if hw_count is not None and hw_count > 0:
        saved_count = get_saved_pagecount()
        if saved_count is None:
            save_pagecount(hw_count)
        elif hw_count > saved_count:
            save_pagecount(hw_count)
            save_last_run(now)
            clear_reminder_state()
            last_run = now
            log("TIMER_AKTUALISIERT", f"Drucker-Seitenzähler gestiegen ({saved_count} -> {hw_count}, z. B. Handy/Kopie) – Timer neu gestartet.")

    latest_cups = get_latest_cups_print_time(PRINTER_NAME)
    if latest_cups is not None and latest_cups <= now and latest_cups > (last_run + timedelta(seconds=5)):
        save_last_run(latest_cups)
        clear_reminder_state()
        last_run = latest_cups
        log("TIMER_AKTUALISIERT", f"Regulärer Mac-Druck am {latest_cups:%Y-%m-%d %H:%M} erkannt – Timer neu gestartet.")

    elapsed = now - last_run
    if elapsed < timedelta(days=INTERVAL_DAYS):
        rem = timedelta(days=INTERVAL_DAYS) - elapsed
        log("NOCH_NICHT_FAELLIG", f"Letzter Druck am {last_run:%Y-%m-%d %H:%M}. Verbleibend: {rem.days}d {rem.seconds // 3600}h.")
        return

    send_reminder_if_due(now, elapsed.days)


if __name__ == "__main__":
    main()
