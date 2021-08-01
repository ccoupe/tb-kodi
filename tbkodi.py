import logging
import os
import os.path
import json
import sys
import time, threading, sched
import paho.mqtt.client as mqtt
from kodijson import Kodi, PLAYER_VIDEO

#Login with my credentials
kodi = Kodi("http://kodi.local:8080/jsonrpc","kodi","tssgnu")
#print(kodi.JSONRPC.Ping())

listen_on = 'homie/kodi_tracker/track/control/set'

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
  except:
    traceback.print_exc()
    
def on_disconnect():
  global log
  log.info('disconnected')

def main():
  # logging setup
  global log, listen_on
  logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')
  log = logging.getLogger('TB_Kodi')
  client = mqtt.Client('TB_Kodi', False)
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

