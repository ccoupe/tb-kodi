import logging
import os
import os.path
import json
import sys
import argparse
import time, threading, sched
import paho.mqtt.client as mqtt
from Settings import Settings
#from kodijson import Kodi, PLAYER_VIDEO
import random
import subprocess
import glob

#Login with my credentials
#kodi = Kodi("http://asahi.local:8080/jsonrpc","ccoupe","tssgnu")
#print(kodi.JSONRPC.Ping())

# Globals
settings = None

def on_message(client, userdata, message):
  global settings, log, play_obj
  topic = message.topic
  payload = str(message.payload.decode("utf-8"))
  log.debug(f'on_message {topic} => {payload}')
  try:
    if topic == settings.cmd_topic:
      log.debug(f'have {topic} => {payload}')
      args = json.loads(payload)
      if args.get('uri', None):
        # tell kodi to play it
        # kodi.Player.Open(item={"file": args['uri']})
        uri = args.get('uri', None)
        # Possible to override the settings with the json sent with mqtt
        # Serious security threats if you allow someone to specify the command
        # to run remotely
        pause_for = args.get('pause_for', settings.pause_for)
        sligger = args.get('sligger', settings.sligger)
        video_cmd = args.get('video_cmd', settings.video_cmd)
        # first, wake up the system and display (sligger moves the mouse)
        #slig_obj = Popen('exec ' + sligger, shell=True)
        # second, wait for a few seconds (so it is visible, hopefully)
        time.sleep(pause_for)
        # lastly call for the url to be played
        play_obj = wake_and_show_rtsp(uri)
      elif args.get("off") == "off":
        play_obj.terminate()
      elif args.get('ping', None):
        client.publish(respond_on, "kodi alive")
      else:
        log.warning("Unknown payload")
    else:
      log.warning(f"unknown topic: {topic}")
  except Exception as e:
    print(e)
    log.warning("Ignore error. continuing")
    pass

def wake_and_show_rtsp(rtsp_url):
    print("[Mqtt Listener] Initiating wake sequence...")

    # 1. Detect active Wayland session
    wayland_sockets = glob.glob("/run/user/*/wayland-*")
    is_wayland = len(wayland_sockets) > 0

    if is_wayland:
        socket_path = wayland_sockets[0] # e.g. /run/user/1000/wayland-0
        parts = socket_path.split('/')
        user_id = parts[3] # "1000"
        wayland_display = parts[4] # "wayland-0"
        
        import pwd
        try:
            user_name = pwd.getpwuid(int(user_id)).pw_name
        except Exception:
            user_name = "ccoupe"
            
        print(f"[Mqtt Listener] Wayland session detected for user {user_name} (UID {user_id}), display {wayland_display}")
        
        # Configure environment variables for Wayland/DBus
        os.environ["XDG_RUNTIME_DIR"] = f"/run/user/{user_id}"
        os.environ["WAYLAND_DISPLAY"] = wayland_display
        os.environ["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path=/run/user/{user_id}/bus"
        
        # Wake command sequence run as the logged-in user
        wake_cmd = (
            f"sudo -u {user_name} env "
            f"XDG_RUNTIME_DIR=/run/user/{user_id} "
            f"WAYLAND_DISPLAY={wayland_display} "
            f"DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{user_id}/bus "
            "bash -c '"
            "kscreen-doctor --dpms on 2>/dev/null; "
            "dbus-send --session --type=method_call --dest=org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement org.kde.Solid.PowerManagement.wakeup 2>/dev/null; "
            "dbus-send --session --type=method_call --dest=org.freedesktop.ScreenSaver /ScreenSaver org.freedesktop.ScreenSaver.SimulateUserActivity 2>/dev/null"
            "'"
        )
        subprocess.run(wake_cmd, shell=True, capture_output=True)
        
        # Fail-safe VT toggle if we are root
        if os.geteuid() == 0:
            print("[Mqtt Listener] Running as root. Triggering Virtual Terminal toggle fallback...")
            subprocess.run("chvt 1 && sleep 0.2 && chvt 7", shell=True, capture_output=True)
            
    else:
        print("[Mqtt Listener] Locating randomized SDDM X11 cookies...")
        # 1. Look for SDDM's dynamic authentication files
        sddm_cookie = None
        tmp_cookies = glob.glob("/tmp/xauth_*")
        if tmp_cookies:
            sddm_cookie = tmp_cookies[0]
        else:
            run_cookies = glob.glob("/run/user/1000/xauth_*")
            if run_cookies:
                sddm_cookie = run_cookies[0]

        # 2. Configure the environment variables for X11
        os.environ["DISPLAY"] = ":0"
        if sddm_cookie:
            print(f"[Mqtt Listener] Successfully matched cookie file: {sddm_cookie}")
            os.environ["XAUTHORITY"] = sddm_cookie
        else:
            print("[Warning] No SDDM xauth file found, proceeding with raw commands.")

        # 3. Use KDE's built-in DBus session interface to fake user presence
        dbus_cmd = (
            "dbus-send --session --type=method_call --dest=org.freedesktop.ScreenSaver "
            "/ScreenSaver org.freedesktop.ScreenSaver.SimulateUserActivity"
        )
        subprocess.run(f"machinectl shell 1000@ /bin/bash -c '{dbus_cmd}'", shell=True, capture_output=True)

        # 4. Strip software dimming states via xset
        subprocess.run("xset s off", shell=True, env=os.environ, capture_output=True)
        subprocess.run("xset dpms force on", shell=True, env=os.environ, capture_output=True)

    print("[Mqtt Listener] Display layer forced ON. Spawning player layer...")

    # 5. Open up the RTSP camera stream in full screen using mpv
    stream_cmd = f"mpv --fs --ontop --geometry=100%x100% {rtsp_url}"
    play_proc = subprocess.Popen(stream_cmd, shell=True, env=os.environ)
    return play_proc


'''
Gemini also provide this - just add the url , stream_cmd and call
import subprocess

def wake_via_loginctl():
    print("[Mqtt Listener] Sending systemd unlock signal to session...")
    
    # 1. Force loginctl to wake/unlock all graphical sessions
    # This directly triggers the kernel's display manager to revive video outputs
    subprocess.run("loginctl unlock-sessions", shell=True, capture_output=True)
    
    # 2. Tell the underlying system terminal manager to refresh
    # Toggling to VT 1 and instantly back to VT 7 forces X11 to redraw 
    # its display layout, which forces a live wake signal down the HDMI line.
    subprocess.run("chvt 1 && sleep 0.2 && chvt 7", shell=True, capture_output=True)
'''

def play_uri(cmd, furi):
  global play_obj
  cmd = cmd + ' ' + furi
  log.info(f"Running {cmd}")
  play_obj = Popen('exec ' + cmd, shell=True)
  play_obj.wait()
 
    
def on_disconnect(self, client, userdata, rc):
  global log
  if rc != 0:
    while True:
      tm = random.randint(30,90)
      log.warning(f"mqtt disconnect: {rc}, attempting reconnect in {tm} seconds")
      time.sleep(tm)
      try:
        client.reconnect()
        # if success, break out of the loop
        break
      except OSError as e:
        continue
 
def main():
  # logging setup
  global log, settings, client
  # Argparse
  ap = argparse.ArgumentParser()
  ap.add_argument("-c", "--conf", required=True, type=str,
                  help="path and name of the json configuration file")
  args = vars(ap.parse_args())

  # Logging
  logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')
  log = logging.getLogger('TB_Kodi')
  # Settings
  setfn = args['conf']
  settings = Settings(log, setfn)
  settings.print()
  # 
  # Setup mqtt and wait
  client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, settings.mqtt_client_name, False)
  client.on_message = on_message
  client.on_disconnect = on_disconnect
  rc = client.connect(settings.mqtt_server, settings.mqtt_port)
  if rc != mqtt.MQTT_ERR_SUCCESS:
    log.warn("network missing?")
    exit()
  client.loop_start()
  rc,_ = client.subscribe(settings.cmd_topic)
  if rc != mqtt.MQTT_ERR_SUCCESS:
    log.warn("Subscribe failed: %d" %rc)
  else:
    log.debug("Init() Subscribed to %s" % settings.cmd_topic)
  log.info(f'waiting for mqtt on {settings.cmd_topic}')
  
  while True:
    time.sleep(5*60)

if __name__ == '__main__':
  #kodi.Player.Open(item={"file": "rtsp://ccoupe:tssgnu@192.168.1.28/live"})
  sys.exit(main())

