
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

class Link( object ):
  __timeout__ = .500
  port = None
  def __init__( self, mac, timeout=None ):
    if timeout is not None:
      self.__timeout__ = timeout
    self.mac = mac


  def open( self, mac=False, **kwds ):
    if mac:
      self.mac = mac
    if 'timeout' not in kwds:
      kwds['timeout'] = self.__timeout__

    self.requestor = GATTRequester(self.mac)
    time.sleep(.250)
    if not self.requestor.is_connected( ):
      try:
        self.requestor.connect( )
      except (RuntimeError ), e:
        pass
    self.setup_handles( )

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
    return ord(self.requestor.read_by_handle(self.packet_count)[0])

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
    while link.received( ) > 0:
      print lib.hexdump(link.read( ))
    link.close( )


#####
# EOF
