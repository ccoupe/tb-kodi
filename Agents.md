# Agent Definition - Distributed Kodi Player (kodi)

## Description
A distributed network node that listens for doorbell camera stream triggers and commands a local Kodi instance to display near real-time video or play audio assets.

## Role & Responsibilities
- **Media Playback Bridge:** Interacts with a Kodi JSON-RPC API endpoint to start video stream playback or other media assets upon external request.
- **Doorbell Display Integration:** Automatically plays a specified camera MJPEG stream URL on the TV screen via Kodi when the doorbell is triggered.
- **Heartbeat & Status Responder:** Listens for ping commands and responds with a status message indicating the script is running and connected.

## Key Files
- [tbkodi.py](file:///home/ccoupe/Projects/iot/kodi/tbkodi.py) - Main MQTT subscriber loop and Kodi JSON-RPC integration script.
- [kodi-track.service](file:///home/ccoupe/Projects/iot/kodi/kodi-track.service) - Systemd service definition to run the agent in the background.
- [launch.sh](file:///home/ccoupe/Projects/iot/kodi/launch.sh) - Service launch shell script that activates the virtual environment and executes the python script.

## Integration Points
- **Subscribed MQTT Topics:**
  - `homie/whodo/doorbell/cmd/set` (Trigger doorbell actions: play media via `uri` or `ping` check)
- **Published MQTT Topics:**
  - `homie/whodo/doorbell/cmd` (Respond to heartbeat `ping` events)
- **External API Integrations:**
  - **Kodi JSON-RPC API:** Connects to `http://asahi.local:8080/jsonrpc` (credentials: `ccoupe`/`tssgnu`) to control the media player.

## Context & Memory
- Designed to run persistently as a background systemd service (`kodi-track.service`).
- Keeps connection active by automatically reconnecting to the MQTT broker (`stoic.local`) using random backoff intervals (between 30 and 90 seconds) if disconnected.
