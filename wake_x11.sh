#!/bin/bash

# 1. Set the target display
export DISPLAY=:0

# 2. Dynamically locate the correct Xauthority file for the logged-in user
USER_ID=$(id -u)
export XAUTHORITY="/run/user/$USER_ID/sddm/Xauthority"

# Fallback: Check if it's in a lightdm location if gdm fails
if [ ! -f "$XAUTHORITY" ]; then
    export XAUTHORITY="/var/run/sddm/root/$DISPLAY"
fi

echo "Using Xauthority at: $XAUTHORITY"

# 3. Wake the display using xset or xdotool
xset dpms force on 2>/dev/null || xdotool mousemove_relative 1 1
