set msgFile to (POSIX path of (path to home folder)) & ".printer_keepalive_notify.txt"
try
    set rawText to read POSIX file msgFile as «class utf8»
    set oldDelims to AppleScript's text item delimiters
    set AppleScript's text item delimiters to "|||"
    set parts to text items of rawText
    set AppleScript's text item delimiters to oldDelims
    set nTitle to item 1 of parts
    set nBody to item 2 of parts
    set nSound to item 3 of parts
    if nSound is "sound" then
        display notification nBody with title nTitle sound name "Submarine"
    else
        display notification nBody with title nTitle
    end if
    delay 1.5
end try
