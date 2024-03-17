import logging
import os
import os.path
import json
import sys
import time, threading, sched
import paho.mqtt.client as mqtt
from kodijson import Kodi, PLAYER_VIDEO
import random

#Login with my credentials
kodi = Kodi("http://asahi.local:8080/jsonrpc","ccoupe","tssgnu")
#print(kodi.JSONRPC.Ping())

listen_on = 'homie/kodi_tracker/track/control/set'
respond_on = 'homie/kodi_tracker/track/control'

def on_message(client, userdata, message):
  global listen_on, log, kodi
  topic = message.topic
  payload = str(message.payload.decode("utf-8"))
  log.debug(f'on_message {topic} => {payload}')
  try:
    if topic == listen_on:
      log.debug(f'have {topic} => {payload}')
      args = json.loads(payload)
      if args['uri']:
        # tell kodi to play it
        kodi.Player.Open(item={"file": args['uri']})
      elif args['ping']:
        client.publish(respond_on, "kodi alive")
      else:
        log.warning("Unknown payload")
  except:
    traceback.print_exc()
    
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
  global log, listen_on
  logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')
  log = logging.getLogger('TB_Kodi')
  client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, 'TB_Kodi', False)
  client.on_message = on_message
  client.on_disconnect = on_disconnect
  rc = client.connect('stoic.local', 1883)
  if rc != mqtt.MQTT_ERR_SUCCESS:
    log.warn("network missing?")
    exit()
  client.loop_start()
  rc,_ = client.subscribe(listen_on)
  if rc != mqtt.MQTT_ERR_SUCCESS:
    log.warn("Subscribe failed: %d" %rc)
  else:
    log.debug("Init() Subscribed to %s" % listen_on)
  log.info(f'waiting for mqtt on {listen_on}')
  
  while True:
    time.sleep(5*60)

if __name__ == '__main__':
  #kodi.Player.Open(item={"file": "rtsp://ccoupe:tssgnu@192.168.1.28/live"})
  sys.exit(main())

