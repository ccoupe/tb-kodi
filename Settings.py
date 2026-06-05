import json
import socket
import os 
import sys

class Settings:

  def __init__(self, log, etcf):
    self.etcfname = etcf
    self.log = log
    self.mqtt_server = "192.168.1.2" 
    self.mqtt_port = 1883
    self.mqtt_client_name = "tbkodi_1"
    self.homie_device = None
    self.homie_name = None
    self.cmd_topic = None
    self.video_cmd = None
    self.sligger = None
    self.pause_for = 0
    self.load_settings(self.etcfname)
    self.log.info("Settings from %s" % self.etcfname)


  def load_settings(self, fn):
    conf = json.load(open(fn))
    if conf["mqtt_server_ip"]:
      self.mqtt_server = conf["mqtt_server_ip"]
    if conf["mqtt_port"]:
      self.mqtt_port = conf["mqtt_port"]
    if conf["mqtt_client_name"]:
      self.mqtt_client_name = conf["mqtt_client_name"]
    if conf['homie_device']:
      self.homie_device = conf['homie_device']
    if conf['homie_name']:
      self.homie_name = conf['homie_name']
    self.cmd_topic = conf.get('cmd_topic','homie/whodo/doorbell/cmd/set')
    self.video_cmd = conf.get('video_cmd', "mpv")
    self.sligger = conf.get('sligger', '/usr/local/bin/sligger')
    self.pause_for = conf.get('pause_for', 5)

  def print(self):
    self.log.info("==== Settings ====")
    self.log.info(self.settings_serialize())
  
  def settings_serialize(self):
    st = {}
    st['mqtt_server_ip'] = self.mqtt_server
    st['mqtt_port'] = self.mqtt_port
    st['mqtt_client_name'] = self.mqtt_client_name
    st['homie_device'] = self.homie_device 
    st['homie_name'] = self.homie_name
    st['cmd_topic'] = self.cmd_topic
    st['video_cmd'] = self.video_cmd
    st['pause_for'] = self.pause_for
    st['sligger'] = self.sligger
    return st
    
  def settings_deserialize(self, jsonstr):
    st = json.loads(jsonstr)
