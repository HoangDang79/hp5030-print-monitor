#!/usr/bin/env bash
set -euo pipefail

echo "Installing HP 5030 Print Monitor for macOS..."
mkdir -p "$HOME/.local/bin" "$HOME/Library/LaunchAgents"

DETECTED_PRINTER=$(lpstat -p 2>/dev/null | awk '{print $2}' | head -n 1 || true)
cp print_monitor.py "$HOME/.local/bin/print_monitor.py"

if [ -n "$DETECTED_PRINTER" ]; then
    sed -i '' "s/HP_ENVY_5000_series/$DETECTED_PRINTER/g" "$HOME/.local/bin/print_monitor.py"
    echo "Configured printer: $DETECTED_PRINTER"
fi

chmod +x "$HOME/.local/bin/print_monitor.py"

rm -rf "$HOME/.local/bin/HP5030Notifier.app"
osacompile -o "$HOME/.local/bin/HP5030Notifier.app" hp5030_notifier.applescript
PLIST_PATH="$HOME/.local/bin/HP5030Notifier.app/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :CFBundleIdentifier string com.user.hp5030notifier" "$PLIST_PATH" 2>/dev/null || /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier string com.user.hp5030notifier" "$PLIST_PATH"
/usr/libexec/PlistBuddy -c "Add :LSUIElement bool true" "$PLIST_PATH" 2>/dev/null || /usr/libexec/PlistBuddy -c "Set :LSUIElement true" "$PLIST_PATH"
codesign --force --deep --sign - "$HOME/.local/bin/HP5030Notifier.app"

TARGET_PLIST="$HOME/Library/LaunchAgents/com.user.printmonitor.plist"
sed "s|YOUR_USERNAME|$USER|g" com.user.printmonitor.plist > "$TARGET_PLIST"
launchctl bootout "gui/$(id -u)" "$TARGET_PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$TARGET_PLIST"

echo "Done! Enable banners under System Settings -> Notifications -> HP5030Notifier."
