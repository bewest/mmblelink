
#
# TODO: move all constants to config module.
#

import bluetooth
from bluetooth.ble import DiscoveryService
import gattlib
from gattlib import GATTRequester, GATTResponse
from exceptions import RuntimeError


import time
import logging
from decocare import lib
io  = logging.getLogger( )
log = io.getChild(__name__)

class AlreadyInUseException (Exception):
  pass

def scanner ( ):
  service = DiscoveryService( )
  devices = service.discover(2)
  return devices

class Characteristics (GATTResponse):
  def on_notification(self, handle, data):
    print "ok ...", handle
    print lib.hexdump(data)


class GATT:
  Battery = "2a19"
  Name = "2a00"
  class Radio:
    class Settings:
      Name = "d93b2af0-1e28-11e4-8c21-0800200c9a66"
      class Channels:
        RX = "d93b2af0-1ea8-11e4-8c21-0800200c9a66"
        TX = "d93b2af0-1458-11e4-8c21-0800200c9a66"
    class Stats:
      Received = '41825a20-7402-11e4-8c21-0800200c9a66'

    class Packet:
      Read  = "2fb1a490-1940-11e4-8c21-0800200c9a66"
      Write = "2fb1a490-1941-11e4-8c21-0800200c9a66"
      Send  = "2fb1a490-1942-11e4-8c21-0800200c9a66"
      Count = '41825a20-7402-11e4-8c21-0800200c9a66'

class FetchName (GATTResponse):
  handle = GATT.Name
  sleep_interval = 0.150
  data = None
  def __init__ (self, link):
    self.link = link
    super(GATTResponse, self).__init__( )
  def on_response (self, name):
    print "fetched name is ", name
    self.data = name
    self.link.setName(name)
  def operate (self):
    self.link.requestor.read_by_uuid_async(self.handle, self)
    while not self.received( ):
      time.sleep(self.sleep_interval)


class GetName (object):
  handle = GATT.Name
  sleep_interval = 0.150
  def __init__ (self, link):
    self.link = link
    self.resp = GATTResponse( )
    # super(GATTResponse, self).__init__(self)
  def done (self):
    return self.resp.received( ) or False
  def sleep (self):
    time.sleep(self.sleep_interval)
  def step (self):
    self.sleep( )
  def prolog (self):
    self.received = self.resp.received( )
    self.on_response(self.resp.received( )[0])
  def operate (self):
    self.link.requestor.read_by_uuid_async(self.handle, self.resp)
    while not self.done( ):
      self.step( )
    self.prolog( )

  def on_response (self, name):
    print "name is ", name
    self.link.setName(name)

class ReadOnce (GetName):
  handle = GATT.Radio.Packet.Read
  def on_response (self, data):
    print "read once is {}".format(len(data))
    print lib.hexdump(bytearray(data))
  

class DrainRXBuffer (GetName):
  handle = GATT.Radio.Packet.Read
  def done (self):
    return False
  def step (self):
    print self.resp, self.resp.received( )
    if self.resp.received( ):
      self.on_response(self.resp.received( )[0])
    self.sleep( )

  def on_response (self, name):
    print "data is ", lib.hexdump(bytearray(self.resp.received( )[0]))

class CountPackets (GetName):
  handle = GATT.Radio.Packet.Count
  def on_response (self, data):
    # print "count:", ord(self.resp.received( )[0])
    pass

class WatchPackets (DrainRXBuffer):
  handle = GATT.Radio.Packet.Count
  def on_response (self, name):
    print "count:", ord(self.resp.received( )[0])


class IterReader (WatchPackets):
  def on_response (self, name):
    count = ord(self.resp.received( )[0])
    print "count:", count
    # ReadOnce(self.link).operate( )
    # DrainRXBuffer(self.link).operate( )
    

class Channels:
  class Pump:
    RX = 0
    TX = 2
  class Stick:
    RX = 2
    TX = 0

class Requester (GATTRequester):
  def on_notification (self, handle, data):
    print "notification", handle, data
  def on_indication (self, handle, data):
    print "indication", handle, data

class Channel (object):
  RX = Channels.Stick.RX
  TX = Channels.Stick.TX
  def __init__ (self, ble):
    self.ble = ble

  def __repr__ (self):
    return """Channels:
      RX: {RX}
      TX: {TX}
      """.format(RX=self.RX, TX=self.TX)
  def set_handles (self, rx=None, tx=None):
    self.rx_handle = rx
    self.tx_handle = tx
  def setRX (self, channel):
    print "setting rx to ", channel
    result = self.ble.write_by_handle(self.rx_handle, str(bytearray([channel])))
    self.RX = channel
    return result
  def setTX (self, channel):
    print "setting rx to ", channel
    result = self.ble.write_by_handle(self.tx_handle, str(bytearray([channel])))
    self.TX = channel
    return result

class Link (object):
  __timeout__ = .500
  port = None
  channel = None
  requestor = None
  sleep_interval = 0.150
  _name = None
  def __init__ (self, mac, timeout=None, sleep_interval=None):
    if timeout is not None:
      self.__timeout__ = timeout
    if sleep_interval is not None:
      self.sleep_interval = sleep_interval
    self.mac = mac


  def open( self, mac=False, **kwds ):
    if mac:
      self.mac = mac
    if 'timeout' not in kwds:
      kwds['timeout'] = self.__timeout__

    # self.requestor = GATTRequester(self.mac)
    self.requestor = Requester(self.mac)
    self.channel = Channel(self.requestor)
    time.sleep(.250)
    if self._name is None:
      self.fetch_name( )
    if not self.requestor.is_connected( ):
      try:
        self.requestor.connect( )
      except (RuntimeError ), e:
        pass
    self.setup_handles( )
    handle = dict(rx=self.set_rx_channel_handle, tx=self.set_tx_channel_handle)
    self.channel.set_handles(**handle)

  def fetch_name (self):
    req = GetName(self)
    req.operate( )
    # req.operate( )

  def GetName (self):
    req = GetName(self)
    req.operate( )
  def getName (self):
    return self._name

  def setName (self, name):
    self._name = name

  def setup_handles (self):
    self.characteristics = self.get_characteristics( )
    for char in self.characteristics:
      if char['uuid'] == GATT.Radio.Packet.Read:
        self.read_handle = char['value_handle']
      if char['uuid'] == GATT.Radio.Packet.Write:
        self.write_handle = char['value_handle']
      if char['uuid'] == GATT.Radio.Packet.Send:
        self.send_handle = char['value_handle']
      if char['uuid'] == GATT.Radio.Packet.Count:
        self.packet_count = char['value_handle']
      if GATT.Name in char['uuid']:
        self.get_name_handle = char['value_handle']
      if char['uuid'] == GATT.Radio.Settings.Name:
        self.set_name_handle = char['value_handle']
      if GATT.Radio.Settings.Channels.TX == char['uuid']:
        self.set_tx_channel_handle = char['value_handle']
      if GATT.Radio.Settings.Channels.RX == char['uuid']:
        self.set_rx_channel_handle = char['value_handle']
  def set_name (self, name):
    return self.requestor.write_by_handle(self.set_name_handle, name)

  def get_name (self):
    return self.requestor.read_by_handle(self.get_name_handle)[0]

  def get_characteristics (self):
    return self.requestor.discover_characteristics( )

  def close( self ):
    io.info( 'disconnecting bluetooth' )
    self.requestor.disconnect( )
    
  def write( self, string ):
    r = self.requestor.write_by_handle(self.write_handle, string)
    io.info( 'usb.write.len: %s\n%s' % ( len( string ),
                                         lib.hexdump( bytearray( string ) ) ) )
    return r

  def received (self):
      op = CountPackets(self)
      op.sleep_interval = self.sleep_interval
      op.operate( )
      count = ord(op.resp.received( )[0])
      return count
  def get_packet_count (self):
    return ord(self.requestor.read_by_handle(self.packet_count)[0])

  def dump_rx_buffer (self):
    while self.received( ) > 0:
      yield self.read( )
      # print lib.hexdump(link.read( ))
  def read( self, c=64 ):
    r = self.requestor.read_by_handle(self.read_handle)
    io.info( 'usb.read.len: %s'   % ( len( r ) ) )
    io.info( 'usb.read.raw:\n%s' % ( lib.hexdump( bytearray( r[0] ) ) ) )
    return bytearray(r[0])
    
  def readline( self ):
    r = self.serial.readline( )
    io.info( 'usb.read.len: %s\n%s' % ( len( r ),
                                        lib.hexdump( bytearray( r ) ) ) )
    return r
      
  def readlines( self ):
    r = self.serial.readlines( )
    io.info( 'usb.read.len: %s\n%s' % ( len( r ),
                                        lib.hexdump( bytearray( ''.join( r ) ) ) ) )
    return r

# radio d39f1890-17eb-11e4-8c21-0800200c9a66
# rx-packet-count 41825a20-7402-11e4-8c21-0800200c9a66
if __name__ == '__main__':
  import doctest
  import sys
  # doctest.testmost( )
  args = sys.argv[:]
  mac = (args[1:2] or [None]).pop( )
  if mac is None:
    devices = scanner( )
    for addr, name in devices.items( ):
      print """{addr} {name}""".format(addr=addr, name=name)
  else:
    link = Link(mac)
    link.open( )
    while True:
      op = CountPackets(link)
      op.operate( )
      count = ord(op.resp.received( )[0])
      if count < 1:
        print "sleeping"
        time.sleep(.150)
      else:
        for buf in link.dump_rx_buffer( ):
          print lib.hexdump(buf)

    #while link.received( ) > 0:
    #  print lib.hexdump(link.read( ))
    #op = DrainRXBuffer(link)
    #op.operate( )
    op = CountPackets(link)
    op = IterReader(link)
    op.operate( )
    #while link.received( ) > 0:
    #  print lib.hexdump(link.read( ))
    link.close( )


#####
# EOF
