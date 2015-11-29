
# Based on decoding-carelink/decocare/link.py

import array
import logging
import signal
import time
import serial

import decocare.lib as lib
import decocare.fuser as fuser

from mmeowlink.exceptions import InvalidPacketReceived, TimeoutException

# from fourbysix import FourBySix

io  = logging.getLogger( )
log = io.getChild(__name__)

class NotImplementedException (Exception):
  pass

class Link( object ):
  __timeout__ = 1.000   # 1 second

  port = None

  def __init__( self, port=None, timeout=None):
    if timeout is not None:
      self.__timeout__ = timeout

    self.port = port
    self.open()

  def open( self, newPort=None, **kwds ):
    log.info( '{agent} opening serial port'
      .format(agent=self.__class__.__name__ ))

    if 'timeout' not in kwds:
      kwds['timeout'] = self.__timeout__

    self.serial = serial.Serial( self.port, 57600, **kwds )

    return True

  def close( self ):
    log.info( '{agent} stopped using serial port'
      .format(agent=self.__class__.__name__ ))

    self.serial.close( )
    return True

  def write( self, string, reset_after_send=True ):
    message = bytearray( string )

    # Format of transmission is as follows. Note that the content is
    # automatically converted to FourBySix
    #
    # Command | Length of Message | Repetititons | Message ...
    #
    # Command is:
    #  0x1  Send - CRC already included
    #  0x81 Send - Add CRC-8 at the end
    #  0xC1 Send - Add CRC-16 at the end
    arr = array.array('B', bytearray([0x1, len(message), 1]) + message)

    r = self.serial.write( arr.tostring() )
    io.info( 'usb.write.len: %s\n%s' % ( len( string ),
                                         lib.hexdump( bytearray( string ) ) ) )
    return r

  def read( self, timeout=None ):
    if not timeout:
      timeout = self.__timeout__

    self.serial.timeout = timeout

    # Result format:
    # State | Length | Message
    #
    # State is:
    #   - 2:  CRC ok
    #   - 4:  Repeated Message (we have this disabled)
    #   - 82: CRC not ok
    # Anything else is unknown, or part of a previous receive that we
    # didn't expect. We ignore those.
    #
    # We also ignore messages where the CRC doesn't match our expectation
    #

    # Wait until we've received a message we can understand.
    while True:
      state = self.serial.read(1)
      if (state is None) or len(state) == 0:
        raise TimeoutException("Timeout reading message result")

      if ord(state) == 2:
        body_len = self.serial.read(1)

        if (body_len is None) or (len(body_len) == 0):
          raise TimeoutException("Timeout reading length of response")

        # This is raised as a concern in the mmcommander code, so I
        # currently treat this as an error case
        if ord(body_len) > 74:
          raise InvalidPacketReceived("Warning - received message > 74 chars")

        message = self.serial.read(ord(body_len))
        if (message is None) or (len(message) == 0):
          raise TimeoutException("Timeout reading message body")

        return bytearray( message )
      else:
        io.info( 'usb.read error: state message received. Ignoring value %i' % ord(state) )

  def readline( self ):
    raise NotImplementedException("readline currently not implemented")

  def readlines( self ):
    raise NotImplementedException("readlines currently not implemented")
