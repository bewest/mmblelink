
# Based on decoding-carelink/decocare/link.py

import logging
import decocare.lib as lib
import decocare.fuser as fuser
io  = logging.getLogger( )
log = io.getChild(__name__)

from rflib import *

class NotImplementedException (Exception):
  pass


def setup_medtronic_mmcommander (self, locale='US'):
    self.getRadioConfig()
    rc = self.radiocfg
    rc.sync1 = 0xff
    rc.sync0 = 0x00
    rc.pktlen = 0xff
    rc.pktctrl1 = 0x00
    rc.pktctrl0 = 0x00
    rc.addr = 0x00
    rc.channr = 0x00
    rc.fsctrl1 = 0x06
    rc.fsctrl0 = 0x00
    # EU:
    rc.freq2      = 0x24
    rc.freq1      = 0x2e
    rc.freq0      = 0x38

    # US
    if locale == 'US':
      rc.freq2      = 0x26 # OK
      rc.freq1      = 0x30 # OK
      rc.freq0      = 0x00 # OK

    rc.mdmcfg4    = 0xb9 # OK
    rc.mdmcfg3    = 0x66 # OK
    rc.mdmcfg2    = 0x33 # OK
    rc.mdmcfg1    = 0x61 # OK
    rc.mdmcfg0    = 0xe6 # OK
    rc.deviatn    = 0x15 # OK
    rc.mcsm2      = 0x07
    rc.mcsm1      = 0x30
    rc.mcsm0      = 0x18
    rc.foccfg     = 0x17
    rc.bscfg      = 0x6c
    rc.agcctrl2   = 0x03
    rc.agcctrl1   = 0x40
    rc.agcctrl0   = 0x91
    rc.frend1     = 0x56
    rc.frend0     = 0x11 # OK                      Which pa_table item matches
    rc.fscal3     = 0xe9
    rc.fscal2     = 0x2a
    rc.fscal1     = 0x00
    rc.fscal0     = 0x1f
    rc.test2      = 0x88
    rc.test1      = 0x31
    rc.test0      = 0x09
    rc.pa_table7  = 0x00
    rc.pa_table6  = 0x00
    rc.pa_table5  = 0x00
    rc.pa_table4  = 0x00
    rc.pa_table3  = 0x00
    rc.pa_table2  = 0x00
    rc.pa_table1  = 0x50 # 52 in USA?
    rc.pa_table0  = 0x00
    self.setRadioConfig()

class Link( object ):
  __timeout__ = .500
  port = None
  rfcat = None

  def __init__( self, port=None, timeout=None ):
    if timeout is not None:
      self.__timeout__ = timeout

    self.open()

  def open( self, newPort=None, **kwds ):
    if 'timeout' not in kwds:
      kwds['timeout'] = self.__timeout__

    if not self.rfcat:
      print("Loading rfcat")
      self.rfcat = RfCat()
      self.rfcat
      setup_medtronic_mmcommander(self.rfcat)

    log.info( '{agent} started RfCat library'
      .format(agent=self.__class__.__name__ ))

  def close( self ):
    io.info( 'deallocating rfcat' )
    self.rfcat = None
    return True

  def write( self, string ):
    import pdb; pdb.set_trace()

    self.rfcat.RFxmit(string)
    io.info( 'usb.write.len: %s\n%s' % ( len( string ),
                                         lib.hexdump( bytearray( string ) ) ) )
    return len(string)

  def read( self, c ):
    import pdb; pdb.set_trace()

    r = self.rfcat.RFrecv(timeout=__timeout__)
    io.info( 'usb.read.len: %s'   % ( len( r ) ) )
    io.info( 'usb.read.raw:\n%s' % ( lib.hexdump( bytearray( r ) ) ) )
    return r

  def readline( self ):
    raise NotImplementedException("readline currently not implemented")

  def readlines( self ):
    raise NotImplementedException("readlines currently not implemented")
