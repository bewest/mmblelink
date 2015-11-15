
# Based on decoding-carelink/decocare/link.py

import logging
import decocare.lib as lib
import decocare.fuser as fuser
import time
io  = logging.getLogger( )
log = io.getChild(__name__)

from rflib import *

class NotImplementedException (Exception):
  pass

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
      self.rfcat.setup_medtronic_mmcommander_eu()
      self.rfcat.setMaxPower()

    log.info( '{agent} started RfCat library'
      .format(agent=self.__class__.__name__ ))

  def close( self ):
    io.info( 'deallocating rfcat' )
    self.rfcat = None
    return True

  def write( self, string ):
    # import pdb; pdb.set_trace()

    self.rfcat.RFxmit(string)
    self.reset_rfcat()
    io.info( 'usb.write.len: %s\n%s' % ( len( string ),
                                         lib.hexdump( bytearray( string ) ) ) )
    return len(string)

  def read( self ):
    # import pdb; pdb.set_trace()

    r = self.rfcat.RFrecv(timeout=self.__timeout__ * 1000)
    self.reset_rfcat()
    io.info( 'usb.read.len: %s'   % ( len( r ) ) )
    # import pdb; pdb.set_trace()

    # io.info( 'usb.read.raw:\n%s' % ( lib.hexdump( bytearray( r[0] ) ) ) )
    return r[0]

  def readline( self ):
    raise NotImplementedException("readline currently not implemented")

  def readlines( self ):
    raise NotImplementedException("readlines currently not implemented")

  # Workaround for https://bitbucket.org/atlas0fd00m/rfcat/issues/8/first-packet-receive-ok-but-cannot-receive - FIXME
  def reset_rfcat( self ):
    self.rfcat.makePktFLEN(255)
