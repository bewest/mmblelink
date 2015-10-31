
from decocare import session, lib, commands
from mmblelink.packets.rf import Packet
from mmblelink.fourbysix import FourBySix
import logging
import time
from decocare import lib
io  = logging.getLogger( )
log = io.getChild(__name__)

class Sender (object):
  sent_params = False
  expected = 64
  def __init__ (self, link):
    self.link = link
    self.frames = [ ]

  def send (self, payload):
    self.link.write(payload)
    self.link.triggerTX( )
    self.link.write(payload)
    self.link.triggerTX( )
  def send_params (self):
    command = self.command
    params = self.command.params
    missing = [ ]
    missing = bytearray([0x00]) * (65 - len(payload))
    payload = bytearray([len(params)]) + bytearray(params) + missing
    pkt = Packet.fromCommand(command, payload=payload, serial=command.serial)
    pkt = pkt.update(payload)
    buf = self.pkt.assemble( )
    print "sending PARAMS", str(buf).encode('hex')
    encoded =  FourBySix.encode(buf)
    self.link.write(encoded)
    self.link.triggerTX( )
    self.sent_params = True
  def unframe (self, resp):
    payload = resp.payload
    if self.expected > 64:
      num, payload = payload[0], payload[1:]
      self.frames.append((num, payload))
    print "len", len(payload)
    self.command.respond(payload)
  def done (self):
    needs_params = self.command.params and True or False
    if needs_params and not self.sent_params:
      return False
    return  self.command.done( )
  def respond (self, resp):
    if resp.valid and resp.serial == self.command.serial:
      if resp.op == 0x06:
        if not self.command.done( ) or (self.command.params and not self.sent_params):
          self.send_params( )
        else:
          return self.command
      if resp.op == self.command.code:
        # self.command.respond(resp.payload)
        self.unframe(resp.payload)
        # print "len", len(resp.payload)
        if self.done( ):
          return self.command
  def __call__ (self, command):
    link = self.link
    self.expected = command.bytesPerRecord * command.maxRecords
    self.command = command
    # payload = bytearray([len(command.params)]) + bytearray(command.params)
    payload = bytearray([0])
    self.pkt = Packet.fromCommand(command, payload=payload, serial=command.serial)
    self.pkt = self.pkt.update(payload)
    buf = self.pkt.assemble( )
    print "sending", str(buf).encode('hex')
    encoded =  FourBySix.encode(buf)
    self.send(encoded)
    print "searching response for ", command, 'done? ', self.done( )
    while not self.done( ):
      for buf in link.dump_rx_buffer( ):
        print lib.hexdump(buf)
        resp = Packet.fromBuffer(buf)
        print "pkt resp", resp
        if resp.valid and resp.serial == self.command.serial:
          self.respond(resp)
          """
          if resp.op == self.command.code:
            self.command.respond(resp.payload)
            print "len", len(resp.payload)
            if self.command.done( ):
              return command
          """
    print 'frames',  len(self.frames)
    return command

class WakeUp (Sender):
  timeout = 10
  def send (self, payload):
    while self.received( ) > 0:
      self.link.write(payload)
      self.link.triggerTX( )
      self.link.write(payload)
      self.link.triggerTX( )

class Pump (session.Pump):
  def __init__ (self, link, serial):
    self.link = link
    self.serial = serial
  def power_control (self, minutes=None):
    log.info('BEGIN POWER CONTROL %s' % self.serial)
    # print "PowerControl SERIAL", self.serial
    response = self.query(commands.PowerControl, minutes=minutes)
    power = response
    log.info('manually download PowerControl serial %s' % self.serial)
    data = dict(raw=str(power.data).encode('hex'), ok=power.done( ), minutes=minutes)
    return data

  def execute (self, command):
    command.serial = self.serial
    transfer = Sender(self.link)
    response = transfer(command)
    return response


