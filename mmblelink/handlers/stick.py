
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
    # self.link.write(payload)
    # self.link.triggerTX( )
  def send_params (self):
    command = self.command
    params = self.command.params
    payload = bytearray([len(params)]) + bytearray(params)
    missing = [ ]
    missing = bytearray([0x00]) * (64 - len(params))
    payload = payload + missing
    pkt = Packet.fromCommand(command, payload=payload, serial=command.serial)
    pkt = pkt.update(payload)
    buf = pkt.assemble( )
    print "sending PARAMS", str(buf).encode('hex')
    encoded =  FourBySix.encode(buf)
    self.link.write(encoded)
    self.link.triggerTX( )
    # self.link.write(encoded)
    # self.link.triggerTX( )
    self.sent_params = True
  def ack (self):
    null = bytearray([0x00])
    pkt = Packet.fromCommand(self.command, payload=null, serial=self.command.serial)
    pkt = pkt._replace(payload=null, op=0x06)
    buf = pkt.assemble( )
    print "ACK tx", str(buf).encode('hex')
    encoded =  FourBySix.encode(buf)
    self.link.write(encoded)
    self.link.triggerTX( )
    # self.link.write(encoded)
    # self.link.triggerTX( )
    
  def unframe (self, resp):
    payload = resp.payload
    if self.expected > 64 or True:
      num, payload = payload[0], payload[1:]
      self.frames.append((num, payload))
      self.ack( )
    print "len", len(payload)
    self.command.respond(payload)
  def done (self):
    needs_params = self.command.params and len(self.command.params) > 0 or False
    if needs_params and not self.sent_params:
      return False
    return  self.command.done( )
  def respond (self, resp):
    if resp.valid and resp.serial == self.command.serial:
      if resp.op == 0x06:
        # if not self.command.done( ) or (self.command.params and not self.sent_params):
        print "done?", self.command, self.done( )
        if not self.done( ):
          print "got ack but not done"
          return self.command
        else:
          return self.command
      if resp.op == self.command.code:
        # self.command.respond(resp.payload)
        self.unframe(resp)
        # print "len", len(resp.payload)
        if self.done( ):
          return self.command
        else:
          print "not done", len(self.frames)
          # self.ack( )
          pass
  def wait_for_ack (self):
    link = self.link
    # while not self.done( ):
    for buf in link.dump_rx_buffer( ):
      print "wait_for_ack"
      resp = Packet.fromBuffer(buf)
      if self.responds_to(resp):
        print lib.hexdump(buf)
        if resp.op == 0x06:
          # self.unframe(resp)
          print "found valid ACK"
          return resp
  def responds_to (self, resp):
    return resp.valid and resp.serial == self.command.serial
  def wait_response (self):
    link = self.link
    for buf in link.dump_rx_buffer( ):
      resp = Packet.fromBuffer(buf)
      if self.responds_to(resp):
        print "READ"
        print lib.hexdump(buf)
        return resp
  def prelude (self, command):
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

  def upload (self):
    params = self.command.params
    should_send = len(params) > 0
    if should_send:
      print "has params to send"
      self.wait_for_ack( )
      print "have ack"
      self.send_params( )
      # self.wait_for_ack( )
  def __call__ (self, command):
    link = self.link
    # empty buffer
    link.dump_rx_buffer( )
    self.prelude(command)
    self.upload( )
    while not self.done( ):
      resp = self.wait_response( )
      if resp:
        self.respond(resp)
      """
      for buf in link.dump_rx_buffer( ):
        print lib.hexdump(buf)
        resp = Packet.fromBuffer(buf)
        print "pkt resp", resp
        if resp.valid and resp.serial == self.command.serial:
          self.respond(resp)
      """
    print 'frames',  len(self.frames)
    return command

class Repeater (Sender):
  timeout = 24
  def send (self, payload):
    # while self.link.received( ) < 1 and not self.timedout( ):
    self.link.write(payload)
    for x in xrange(25):
    # if True:
      self.link.triggerTX( )
      time.sleep(.250)
      # self.link.sleep( )
      # self.link.sleep( )
      self.link.triggerTX( )
      time.sleep(.250)
      # self.link.sleep( )
      # self.link.sleep( )
  def timedout (self):
    now = time.time( )
    return now - self.start > self.timeout
  def __call__ (self, command):
    link = self.link
    self.start = time.time( )
    # empty buffer
    link.dump_rx_buffer( )
    self.prelude(command)
    # while not self.done( ) and not self.timedout( ):
    while not self.done( ):
      # self.prelude(command)
    # if True:
      time.sleep(3)
      self.start = time.time( )
      resp = self.wait_for_ack( )
      print 'acked?', resp
      # resp = self.wait_response( )
      if resp:
      # for buf in link.dump_rx_buffer( ):
        # print lib.hexdump(buf)
        # resp = Packet.fromBuffer(buf)
        # print "pkt resp", resp
        if resp.valid and resp.serial == self.command.serial:
          self.upload( )
          ack = self.wait_for_ack( )
          print "got ACK", ack
          # self.respond(resp)
          return command
        else:
          self.prelude(command)
          # self.send( )
    print 'frames',  len(self.frames)
    return command


class Pump (session.Pump):
  def __init__ (self, link, serial):
    self.link = link
    self.serial = serial
  def power_control (self, minutes=None):
    log.info('BEGIN POWER CONTROL %s' % self.serial)
    # print "PowerControl SERIAL", self.serial
    command = commands.PowerControl(**dict(minutes=minutes, serial=self.serial))
    transfer = Repeater(self.link)
    response = transfer(command)
    # response = self.query(commands.PowerControl, minutes=minutes)
    power = response
    log.info('manually download PowerControl serial %s' % self.serial)
    data = dict(raw=str(power.data).encode('hex'), ok=power.done( ), minutes=minutes)
    return data

  def execute (self, command):
    command.serial = self.serial
    transfer = Sender(self.link)
    response = transfer(command)
    return response


