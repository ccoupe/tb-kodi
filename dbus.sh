#! /bin/bash
export DISPLAY=:0
export XAUTHORITY=$(ps aux | grep -oP '(?<=-auth )[^ ]+' | head -n 1)
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus";
dbus-send --session --type=method_call --dest=org.freedesktop.ScreenSaver /ScreenSaver org.freedesktop.ScreenSaver.SimulateUserActivity
