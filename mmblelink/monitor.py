
# PYTHON_ARGCOMPLETE_OK
from link import Link, GATT, Channels
import time
import logging
from decocare import lib
from datetime import datetime
io  = logging.getLogger( )
log = io.getChild(__name__)

class Monitor (object):
  def __init__ (self, link,  **kwds):
     self.link = link
     self.setup(**kwds)

  def setup (self, RX=Channels.Stick.RX, timeout=None, sleep=.150, **kwds):
     self.RX = RX
     self.timeout = timeout
     self.sleep_interval = sleep
     self.link.channel.setRX(self.RX)
  def start (self):
    self.start = time.time( )
  def done (self):
    if self.timeout:
      return time.time( ) - self.start > self.timeout
    return False
  def sleep (self):
    time.sleep(self.sleep_interval)
  def listen (self, **kwds):
    self.start( )
    link = self.link
    while not self.done( ):
      count = link.received( )
      if count < 1:
        # print "sleeping"
        log.info('sleeping {}'.format(.150))
        self.sleep( )
      else:
        print datetime.now( ).isoformat( ), "count:", count
        for buf in link.dump_rx_buffer( ):
          print lib.hexdump(buf)

def choose_rx_channel (value):
  keys = dict(PumpTX=Channels.Pump.TX, PumpRX=Channels.Pump.RX)
  return keys.get(value, Channels.Pump.TX)

def setup_argparser (parser=None):
  import argparse
  import argcomplete
  parser = parser or argparse.ArgumentParser( )
  parser.add_argument('--verbosity', '-v', action='count')
  parser.add_argument('--rx', '-r', default='PumpTX', choices=['PumpTX', 'PumpRX'])
  parser.add_argument('mac', help='MAC address of rileylink')

  argcomplete.autocomplete(parser)
  return parser

if __name__ == '__main__':
  import sys
  parser = setup_argparser( )
  args = parser.parse_args( )
  # args = sys.argv[:]
  # mac = (args[1:2] or [None]).pop( )
  mac = args.mac
  channel = choose_rx_channel(args.rx)
  print args
  if args.mac:
    link = Link(mac)
    link.open( )
    monitor = Monitor(link, RX=channel)
    monitor.listen( )
    link.close( )
