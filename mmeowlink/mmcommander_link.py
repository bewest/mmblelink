
# Based on decoding-carelink/decocare/link.py

import array
import logging
import signal
import time
import serial

import decocare.lib as lib
import decocare.fuser as fuser

from mmeowlink.exceptions import InvalidPacketReceived, TimeoutException, MMCommanderNotWriteable

io  = logging.getLogger( )
log = io.getChild(__name__)

class NotImplementedException (Exception):
  pass

class Link( object ):
  # How many repetitions can be sent by the underlying code in one go.
  # It seems that the mmcommander firmware can crash if this is too high
  MAX_REPETITION_BATCHSIZE = 255
  VERSION_FETCH_COMMAND = 0x00

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

    self.mmcommander_version()

    return True

  def mmcommander_version(self):
    # Check it's a mmcommander device:
    self.serial.write(chr(self.VERSION_FETCH_COMMAND))
    version = self.serial.read(1)
    log.info( 'MMCommander Firmare version: %s' % ord(version))

  def close( self ):
    log.info( '{agent} stopped using serial port'
      .format(agent=self.__class__.__name__ ))

    self.serial.close( )
    return True

  def write( self, string, repetitions=1, timeout=None ):
    if timeout is None:
      timeout = self.__timeout__

    message = bytearray( string )
    message_length = len(message)

    # Format of transmission is as follows. Note that the content is
    # automatically converted to radio (FourBySix) format
    #
    # Command | Length of Message | Repetititons | Message ...
    #
    # Command is:
    #  0x1  Send - CRC already included
    #  0x81 Send - Add CRC-8 at the end
    #  0xC1 Send - Add CRC-16 at the end
    #
    # Repetitions must be <= 255 as it's a byte. So we loop according to the
    # maximum batch size
    remaining_messages = repetitions
    while remaining_messages > 0:
      if remaining_messages < self.MAX_REPETITION_BATCHSIZE:
        transmissions = remaining_messages
      else:
        transmissions = self.MAX_REPETITION_BATCHSIZE
      remaining_messages = remaining_messages - transmissions

      arr = array.array('B', bytearray([0x1, message_length, transmissions]) + message)

      r = self.serial.write( arr.tostring() )
      io.info( 'usb.write.len: %s\n%s' % ( len( string ),
                                           lib.hexdump( bytearray( string ) ) ) )

      # If the batch is large, the hardware can take a while to respond to us.
      # Based on testing, this seems about right:
      self.serial.timeout = timeout + (0.03 * transmissions)
      confirmation = self.serial.read(3)
      if bytearray( confirmation ) != bytearray([ 0x01, message_length, transmissions]):
        import pdb; pdb.set_trace()
        raise MMCommanderNotWriteable("Could not get confirmation from mmcommander that it is writeable. Has it been flashed correctly? Response was %s %s %s" % (confirmation[0], confirmation[1], confirmation[2]))

    return r

  def read( self, timeout=None ):
    if timeout is None:
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
