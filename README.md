# HP ENVY 5030 Print Monitor (`hp5030-print-monitor`)

---

## Deutsch

Hintergrund-Ueberwachung fuer den **HP ENVY 5030** (`HP_ENVY_5000_series`) unter macOS, damit der Druckkopf mindestens alle **21 Tage** genutzt wird und nicht eintrocknet.

### Funktionsweise
- Ein `launchd`-Dienst (`com.user.printmonitor`) prueft stuendlich im Hintergrund lokale macOS-Druckauftraege (`lpstat` / CUPS) sowie den Hardware-Seitenzaehler des Druckers (IPP / XML).
- Sobald ein Druck- oder Kopiervorgang erkannt wird, startet der 21-Tage-Countdown neu.
- Nach 21 Tagen ohne Druckaktivitaet loest das Skript ueber `~/.local/bin/HP5030Notifier.app` eine macOS-Benachrichtigung aus.

### 1. Benachrichtigungen ansehen & pruefen
- **Banner live testen:** `printf 'HP 5030 Druckkopf-Erinnerung|||Bitte kurz eine Farbseite drucken.|||sound' > ~/.printer_keepalive_notify.txt && open -W -a ~/.local/bin/HP5030Notifier.app`
- **Mitteilungszentrale oeffnen:** Oben rechts in der Menueleiste auf **Datum & Uhrzeit** klicken, um zugestellte Mitteilungen nachtraeglich zu sehen.
- **macOS-Einstellungen pruefen:** Unter **Systemeinstellungen -> Mitteilungen -> HP5030Notifier** sicherstellen, dass **Mitteilungen erlauben** aktiv ist und der Stil auf **Banner** steht (kein Fokus-Modus wie *Nicht stoeren* aktiv).

### 2. Status & erwartete Meldungen pruefen
- **Status, letzten Druck, Seitenzaehler und letzte Log-Zeilen anzeigen:**
  `launchctl list | grep printmonitor || true; echo "=== Letzter Druck ==="; cat ~/.printer_keepalive_last_run 2>/dev/null || echo "noch keiner"; echo "=== Seitenzaehler ==="; cat ~/.printer_keepalive_pagecount 2>/dev/null || echo "noch nicht erfasst"; echo "=== Letzte Pruefungen ==="; tail -n 10 ~/.printer_keepalive.log 2>/dev/null || echo "noch kein Log"`
- **Erwartete Meldungen im Log (`~/.printer_keepalive.log`):**
  - `[NOCH_NICHT_FAELLIG] ... Verbleibend: ...` – Das 21-Tage-Intervall ist noch nicht abgelaufen.
  - `[ERINNERUNG_GESENDET] ...` – 21 Tage ohne Druck sind erreicht; die Benachrichtigung wurde ausgeloest und der Intervall-Zaehler zurueckgesetzt.
  - `[DRUCK_ERKANNT] ...` / Aktualisierter Seitenzaehler – Es wurde ein Druck- oder Kopiervorgang registriert.

### 3. Loeschen / Deinstallieren
- **Dienst und installierte Dateien auf dem Mac entfernen (Projektordner bleibt erhalten):**
  `launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.user.printmonitor.plist 2>/dev/null || true; rm -f ~/Library/LaunchAgents/com.user.printmonitor.plist ~/.local/bin/print_monitor.py ~/.printer_keepalive.log ~/.printer_keepalive_last_run ~/.printer_keepalive_pagecount ~/.printer_keepalive_notify.txt; rm -rf ~/.local/bin/HP5030Notifier.app`
- **Optional – auch den lokalen Projektordner loeschen:**
  `rm -rf ~/hp5030-print-monitor`

### 4. Schritt-fuer-Schritt-Anleitung: Eigene Anpassungen & Erweiterungen hinzufuegen
Damit andere Nutzer (oder du selbst) das Projekt auf einen anderen Drucker, ein anderes Intervall oder eigene Funktionen anpassen und beitragen koennen:
1. **Repository forken & klonen:** Auf GitHub **Fork** klicken und den eigenen Fork lokal klonen: `git clone [https://github.com/](https://github.com/)<DEIN-NUTZERNAME>/hp5030-print-monitor.git && cd hp5030-print-monitor`
2. **Neuen Branch anlegen:** `git checkout -b feat/mein-drucker-oder-feature`
3. **Druckernamen & Intervall anpassen:** In `print_monitor.py` (und ggf. `install.sh`) den Ziel-Druckernamen (z. B. ueber `lpstat -p`) sowie das Tage-Intervall (Standard: `21` Tage) an das eigene Geraet anpassen.
4. **Eigene Logik / Checks hinzufuegen:** Neue Pruefungen (z. B. Tintenstand, anderer IPP-Endpunkt oder zusaetzliche Benachrichtigungstexte) sauber in `print_monitor.py` ergaenzen.
5. **Lokal testen:** Das Skript direkt ausfuehren und pruefen, ob Log-Ausgabe, Seitenzaehler und `HP5030Notifier.app` wie erwartet arbeiten.
6. **Commit, Push & Pull Request:** Aenderungen committen (`git add -A && git commit -m "Add custom printer support"`), in den eigenen Fork pushen (`git push -u origin feat/mein-drucker-oder-feature`) und auf GitHub einen **Pull Request** oeffnen.

---

## English

Background monitor for the **HP ENVY 5030** (`HP_ENVY_5000_series`) on macOS to ensure the printhead is used at least every **21 days** and does not dry out.

### How It Works
- A `launchd` service (`com.user.printmonitor`) runs hourly in the background to check local macOS print jobs (`lpstat` / CUPS) and the printer hardware page counter (IPP / XML).
- Whenever a print or copy job is detected, the 21-day countdown resets.
- After 21 days without print activity, the script triggers a macOS notification via `~/.local/bin/HP5030Notifier.app`.

### 1. View & Test Notifications
- **Test banner live:** `printf 'HP 5030 Printhead Reminder|||Please print a color page soon.|||sound' > ~/.printer_keepalive_notify.txt && open -W -a ~/.local/bin/HP5030Notifier.app`
- **Open Notification Center:** Click **Date & Time** in the top-right menu bar to review delivered notifications.
- **Check macOS notification settings:** Go to **System Settings -> Notifications -> HP5030Notifier**, make sure **Allow notifications** is enabled and the style is set to **Banners** (and no Focus mode such as *Do Not Disturb* is blocking alerts).

### 2. Check Status & Expected Messages
- **Show service status, last print, page count, and recent log lines:**
  `launchctl list | grep printmonitor || true; echo "=== Last Print ==="; cat ~/.printer_keepalive_last_run 2>/dev/null || echo "none yet"; echo "=== Page Count ==="; cat ~/.printer_keepalive_pagecount 2>/dev/null || echo "not recorded yet"; echo "=== Recent Checks ==="; tail -n 10 ~/.printer_keepalive.log 2>/dev/null || echo "no log yet"`
- **Expected messages in the log (`~/.printer_keepalive.log`):**
  - `[NOCH_NICHT_FAELLIG] ... Verbleibend: ...` – The 21-day interval has not expired yet.
  - `[ERINNERUNG_GESENDET] ...` – 21 days without printing reached; notification sent and interval counter reset.
  - `[DRUCK_ERKANNT] ...` / Updated page counter – A print or copy job was detected.

### 3. Delete / Uninstall
- **Remove the background service and installed files on macOS (keeps the project folder):**
  `launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.user.printmonitor.plist 2>/dev/null || true; rm -f ~/Library/LaunchAgents/com.user.printmonitor.plist ~/.local/bin/print_monitor.py ~/.printer_keepalive.log ~/.printer_keepalive_last_run ~/.printer_keepalive_pagecount ~/.printer_keepalive_notify.txt; rm -rf ~/.local/bin/HP5030Notifier.app`
- **Optional – also delete the local project folder:**
  `rm -rf ~/hp5030-print-monitor`

### 4. Step-by-Step Guide: How Others Can Customize & Contribute
To adapt this project to another printer, interval, or workflow and contribute changes:
1. **Fork & clone the repository:** Click **Fork** on GitHub and clone your fork locally: `git clone [https://github.com/](https://github.com/)<YOUR-USERNAME>/hp5030-print-monitor.git && cd hp5030-print-monitor`
2. **Create a feature branch:** `git checkout -b feat/custom-printer-support`
3. **Update printer name & interval:** Edit `print_monitor.py` (and `install.sh` if needed) to set your target printer name (check with `lpstat -p`) and desired day interval (default: `21` days).
4. **Add custom checks or features:** Implement additional logic (such as custom status checks, IPP queries, or notification text) inside `print_monitor.py`.
5. **Test locally:** Run the script directly and verify log entries, page counter tracking, and `HP5030Notifier.app` banner delivery.
6. **Commit, push & open a Pull Request:** Commit your changes (`git add -A && git commit -m "Add custom printer support"`), push to your fork (`git push -u origin feat/custom-printer-support`), and open a **Pull Request** on GitHub.
