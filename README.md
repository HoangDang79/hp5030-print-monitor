# HP ENVY 5030 Print Monitor (macOS)

**[English](#english) | [Deutsch](#deutsch)**

---

## English

A lightweight macOS background service (`launchd` + Python 3 + AppleScript) that monitors printing activity on an **HP ENVY 5030** over Wi-Fi and triggers a native macOS notification after 21 days of inactivity—helping prevent inkjet printhead clogging without wasting ink on automated test prints.

### How It Works
- **Hybrid Activity Tracking:** Combines local macOS CUPS job history (`lpstat` / `/var/log/cups/page_log`) with direct hardware page-counter queries via **IPP (`ipptool`)** and **HP LEDM XML (`/DevMgmt/ProductUsageDyn.xml`)**. This ensures mobile prints (e.g., Android/iOS) and direct copies on the printer also reset the inactivity timer.
- **21-Day Inactivity Threshold:** Runs hourly via `launchd` and sends a reminder notification once 21 days pass without any print or copy activity (with a 24-hour cooldown between reminders).
- **macOS Focus / Do Not Disturb Support:** Uses a minimal, ad-hoc signed AppleScript helper (`HP5030Notifier.app` with `LSUIElement=true`) so notifications integrate cleanly into macOS Notification Center without cluttering the Dock.

### Quick Start (macOS)
1. Clone this repository and run the setup script:
~~~bash
git clone https://github.com/HoangDang79/hp5030-print-monitor.git
cd hp5030-print-monitor
./install.sh
~~~
2. Open **System Settings → Notifications → HP5030Notifier** and set the alert style to **Banners**.

### Uninstall
~~~bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.user.printmonitor.plist 2>/dev/null || true
rm -rf ~/Library/LaunchAgents/com.user.printmonitor.plist ~/.local/bin/print_monitor.py ~/.local/bin/HP5030Notifier.app ~/.printer_keepalive* /tmp/com.user.printmonitor.*
~~~

---

## Deutsch

Ein schlanker macOS-Hintergrunddienst (`launchd` + Python 3 + AppleScript), der die Druckaktivität eines **HP ENVY 5030** im WLAN überwacht und nach 21 Tagen ohne Druck eine native macOS-Mitteilung auslöst – so trocknet der Tintenstrahldruckkopf nicht ein, ohne unnötig Tinte für automatische Testseiten zu verbrauchen.

### Funktionsweise
- **Kombinierte Aktivitätserkennung:** Verbindet die lokale macOS-Druckhistorie (CUPS via `lpstat` / `/var/log/cups/page_log`) mit direkten Abfragen des Hardware-Seitenzählers über **IPP (`ipptool`)** und **HP LEDM XML (`/DevMgmt/ProductUsageDyn.xml`)**. Dadurch setzen auch Handy-Drucke und Kopien direkt am Gerät den Timer zurück.
- **21-Tage-Erinnerung:** Prüft stündlich im Hintergrund über `launchd` und erinnert erst nach 21 Tagen Inaktivität (maximal einmal alle 24 Stunden).
- **Kompatibel mit „Nicht stören“ / Fokus:** Nutzt eine schlanke, signierte AppleScript-Helfer-App (`HP5030Notifier.app` mit `LSUIElement=true`), sodass Mitteilungen ohne Dock-Symbol erscheinen und aktive Fokus-Modi respektieren.

### Schnellstart (macOS)
1. Repository klonen und das Installationsskript ausführen:
~~~bash
git clone https://github.com/HoangDang79/hp5030-print-monitor.git
cd hp5030-print-monitor
./install.sh
~~~
2. Unter **Systemeinstellungen → Mitteilungen → HP5030Notifier** den Hinweisstil auf **Banner** stellen.

### Deinstallation
~~~bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.user.printmonitor.plist 2>/dev/null || true
rm -rf ~/Library/LaunchAgents/com.user.printmonitor.plist ~/.local/bin/print_monitor.py ~/.local/bin/HP5030Notifier.app ~/.printer_keepalive* /tmp/com.user.printmonitor.*
~~~
