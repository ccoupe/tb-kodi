#!/bin/bash

# 1. Target the local monitor
export DISPLAY=:0

# 2. Extract the exact Xauthority file path being used by the active Xorg process
export XAUTHORITY=$(ps aux | grep -oP '(?<=-auth )[^ ]+' | head -n 1)

echo "Found active Xauthority cookie at: $XAUTHORITY"

# 3. Wake up the screen using xset
if [ -f "$XAUTHORITY" ]; then
    xset dpms force on
    echo "Display wake signal sent successfully."
else
    echo "Error: Could not extract a valid Xauthority file."
    exit 1
fi
