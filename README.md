# HP ENVY 5030 Print Monitor (`hp5030-print-monitor`)

Repository: [https://github.com/HoangDang79/hp5030-print-monitor.git](https://github.com/HoangDang79/hp5030-print-monitor.git)

Hintergrund-Überwachung für den **HP ENVY 5030** (`HP_ENVY_5000_series`) unter macOS, damit der Druckkopf mindestens alle **21 Tage** genutzt wird und nicht eintrocknet.

## Funktionsweise

- Ein `launchd`-Dienst (`com.user.printmonitor`) prüft stündlich im Hintergrund:
  1. Lokale macOS-Druckaufträge (`lpstat` / CUPS)
  2. Den Hardware-Seitenzähler des Druckers (IPP / XML)
- Sobald ein Druck oder Kopiervorgang erkannt wird, startet der 21-Tage-Countdown neu.
- Nach 21 Tagen ohne Druckaktivität löst das Skript über `~/.local/bin/HP5030Notifier.app` eine macOS-Benachrichtigung aus.

## 1. Benachrichtigungen ansehen & prüfen

- **Banner live testen (ohne auf 21 Tage zu warten):**
  `printf 'HP 5030 Druckkopf-Erinnerung|||Bitte kurz eine Farbseite drucken.|||sound' > ~/.printer_keepalive_notify.txt && open -W -a ~/.local/bin/HP5030Notifier.app`
- **Mitteilungszentrale öffnen:** Klicke oben rechts in der Menüleiste auf **Datum & Uhrzeit**, um zugestellte Mitteilungen nachträglich zu sehen.
- **macOS-Einstellungen für Benachrichtigungen prüfen:** Öffne **Systemeinstellungen -> Mitteilungen -> HP5030Notifier** und stelle sicher, dass **Mitteilungen erlauben** aktiviert und der Stil auf **Banner** gesetzt ist (außerdem darf kein Fokus-Modus wie *Nicht stören* aktiv sein).

## 2. Status & erwartete Meldungen prüfen

- **Aktuellen Status, letzten Druck, Seitenzähler und letzte Log-Zeilen anzeigen:**
  `launchctl list | grep printmonitor || true; echo "=== Letzter Druck ==="; cat ~/.printer_keepalive_last_run 2>/dev/null || echo "noch keiner"; echo "=== Seitenzähler ==="; cat ~/.printer_keepalive_pagecount 2>/dev/null || echo "noch nicht erfasst"; echo "=== Letzte Prüfungen ==="; tail -n 10 ~/.printer_keepalive.log 2>/dev/null || echo "noch kein Log"`
- **Erwartete Meldungen im Log (`~/.printer_keepalive.log`):**
  - `[NOCH_NICHT_FAELLIG] ... Verbleibend: ...` – Der 21-Tage-Intervall ist noch nicht abgelaufen; alles im grünen Bereich.
  - `[ERINNERUNG_GESENDET] ...` – 21 Tage ohne Druck sind erreicht; die Benachrichtigung wurde ausgelöst und der Intervall-Zähler zurückgesetzt.
  - `[DRUCK_ERKANNT] ...` / Aktualisierter Seitenzähler – Es wurde ein Druck- oder Kopiervorgang registriert.

## 3. Löschen / Deinstallieren

- **Nur den Hintergrunddienst und die installierten Dateien auf dem Mac entfernen (GitHub-Ordner bleibt erhalten):**
  `launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.user.printmonitor.plist 2>/dev/null || true; rm -f ~/Library/LaunchAgents/com.user.printmonitor.plist ~/.local/bin/print_monitor.py ~/.printer_keepalive.log ~/.printer_keepalive_last_run ~/.printer_keepalive_pagecount ~/.printer_keepalive_notify.txt; rm -rf ~/.local/bin/HP5030Notifier.app`
- **Optional – auch den lokalen Projektordner löschen:**
  `rm -rf ~/hp5030-print-monitor`

## Auf GitHub hochladen

`cd ~/hp5030-print-monitor && git add README.md && git commit -m "Update README with notifications, status checks, and uninstall guide" && git push`
