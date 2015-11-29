
# Based on decoding-carelink/decocare/link.py

import logging
import decocare.lib as lib
import decocare.fuser as fuser
import signal
import time
io  = logging.getLogger( )
log = io.getChild(__name__)
from fourbysix import FourBySix

from rflib import *

class NotImplementedException (Exception):
  pass


def setup_medtronic_mmcommander(self, locale='US'):
    self.getRadioConfig()
    rc = self.radiocfg
    rc.sync1          = 0xff
    rc.sync0          = 0x00
    rc.pktlen         = 0xff
    rc.pktctrl1       = 0x00
    rc.pktctrl0       = 0x00
    rc.addr           = 0x00
    rc.fsctrl1        = 0x06
    rc.fsctrl0        = 0x00

    # EU:
    rc.freq2          = 0x24
    rc.freq1          = 0x2e
    rc.freq0          = 0x38
    rc.channr         = 0x00
    rc.pa_table1      = 0x50 # 52 in USA?

    # US
    if locale == 'US':
      rc.freq2        = 0x26
      rc.freq1        = 0x30
      rc.freq0        = 0x00
      rc.channr       = 0x02
      rc.pa_table1    = 0x50 # 52 in USA?

    rc.mdmcfg4        = 0xb9
    rc.mdmcfg3        = 0x66
    rc.mdmcfg2        = 0x33
    rc.mdmcfg1        = 0x61
    rc.mdmcfg0        = 0xe6
    rc.deviatn        = 0x15
    rc.mcsm2          = 0x07
    rc.mcsm1          = 0x30
    rc.mcsm0          = 0x18
    rc.foccfg         = 0x17
    rc.bscfg          = 0x6c
    rc.agcctrl2       = 0x03
    rc.agcctrl1       = 0x40
    rc.agcctrl0       = 0x91
    rc.frend1         = 0x56
    rc.frend0         = 0x11
    rc.fscal3         = 0xe9
    rc.fscal2         = 0x2a
    rc.fscal1         = 0x00
    rc.fscal0         = 0x1f
    rc.test2          = 0x88
    rc.test1          = 0x31
    rc.test0          = 0x09
    rc.pa_table7      = 0x00
    rc.pa_table6      = 0x00
    rc.pa_table5      = 0x00
    rc.pa_table4      = 0x00
    rc.pa_table3      = 0x00
    rc.pa_table2      = 0x00
    rc.pa_table0      = 0x00
    self.setRadioConfig()

class Link( object ):
  port = None
  __rfcat__ = None

  # Try and get only a single RfCat instance. In certain cases the hardware
  # will loop forever, so instead we set a timeout handler

  def build_rfcat_instance(self):
    print "Bulding rfcat instance"
    if self.__rfcat__:
      return

    def timeout_handler(signum, frame):
      raise Exception("Could not instantiate RfCat object")

    signal.alarm(10)
    signal.signal(signal.SIGALRM, timeout_handler)

    rfcat = RfCat()
    setup_medtronic_mmcommander(rfcat, self.locale)
    rfcat.setMaxPower()
    rfcat.makePktFLEN(255)

    signal.alarm(0)

    # Only set this if we've successfully built an object, so that the __del__
    # handler doesn't try and reset a nonfunctional object
    self.__rfcat__ = rfcat

  def __init__( self, port=None, timeout=None, locale='US' ):
    self.locale = locale
    self.build_rfcat_instance()

    self.rfcat = self.__rfcat__

  def __del__( self ):
    try:
      log.info( 'Stopping using rfcat'.format(agent=self.__class__.__name__ ) )
      print "Closing... resetting rfcat"
      self.reset_rfcat()
    except:
      pass

  def open( self, newPort=None, **kwds ):
    log.info( '{agent} started RfCat library'
      .format(agent=self.__class__.__name__ ))
    return True

  def close( self ):
    log.info( '{agent} stopped using RfCat library'
      .format(agent=self.__class__.__name__ ))
    return True

  # Workaround for https://bitbucket.org/atlas0fd00m/rfcat/issues/8/first-packet-receive-ok-but-cannot-receive - FIXME
  def reset_rfcat( self ):
    print "Resetting rfcat..."
    self.rfcat.makePktFLEN(255)

  def debug( self ):
    self.rfcat._debug = 2

  def write( self, string, reset_after_send=True ):
    io.info( 'usb.write.len: %s\n%s' % ( len( string ),
                                         lib.hexdump( bytearray( string ) ) ) )
    self.rfcat.RFxmit(string)
    if reset_after_send:
      self.reset_rfcat()
    return len(string)

  def read( self, timeout=5000):
    rfcat_response = self.rfcat.RFrecv(timeout=timeout)
    self.reset_rfcat()

    r = rfcat_response[0].split('\x00')[0]
    io.info('read encoded %r' % r)
    io.info('read decoded %s' % FourBySix.decode(bytearray(r)))

    return FourBySix.decode(bytearray(r))

  def readline( self ):
    raise NotImplementedException("readline currently not implemented")

  def readlines( self ):
    raise NotImplementedException("readlines currently not implemented")
