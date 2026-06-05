#!/bin/bash

# 1. Identify the target user (defaulting to UID 1000)
USER_ID=1000
for uid in $(ls /run/user/ 2>/dev/null); do
    if [ "$uid" -ge 1000 ]; then
        USER_ID=$uid
        break
    fi
done

USER_NAME=$(id -un "$USER_ID")
echo "Targeting user: $USER_NAME (UID: $USER_ID)"

# 2. Find the active Wayland display socket
WAYLAND_DISPLAY=""
for socket in /run/user/$USER_ID/wayland-*; do
    if [ -S "$socket" ]; then
        WAYLAND_DISPLAY="${socket##*/}"
        break
    fi
done

if [ -z "$WAYLAND_DISPLAY" ]; then
    echo "Warning: No active Wayland socket found in /run/user/$USER_ID/"
    WAYLAND_DISPLAY="wayland-0" # fallback
else
    echo "Found active Wayland display: $WAYLAND_DISPLAY"
fi

# 3. Define the wake commands to run in the user's graphical context
# We use kscreen-doctor --dpms on (KDE Wayland standard)
# and also trigger PowerDevil / ScreenSaver DBus wake APIs
WAKE_COMMANDS=$(cat <<EOF
export XDG_RUNTIME_DIR="/run/user/$USER_ID"
export WAYLAND_DISPLAY="$WAYLAND_DISPLAY"
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$USER_ID/bus"

echo "Sending kscreen-doctor DPMS ON..."
kscreen-doctor --dpms on 2>/dev/null

echo "Sending Solid PowerManagement wakeup via DBus..."
dbus-send --session --type=method_call --dest=org.kde.Solid.PowerManagement \
  /org/kde/Solid/PowerManagement org.kde.Solid.PowerManagement.wakeup 2>/dev/null

echo "Sending ScreenSaver SimulateUserActivity via DBus..."
dbus-send --session --type=method_call --dest=org.freedesktop.ScreenSaver \
  /ScreenSaver org.freedesktop.ScreenSaver.SimulateUserActivity 2>/dev/null
EOF
)

# 4. Execute the commands
if [ "$EUID" -eq 0 ]; then
    # Running as root: execute as the logged-in user
    echo "Running as root. Switching context to $USER_NAME..."
    sudo -u "$USER_NAME" bash -c "$WAKE_COMMANDS"
    
    # Fail-safe: Switch virtual terminals (root only)
    echo "Triggering Virtual Terminal toggle fallback..."
    chvt 1 && sleep 0.2 && chvt 7
else
    # Running as the user
    eval "$WAKE_COMMANDS"
fi

echo "Wake commands completed."
