
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

  def setup (self, RX=Channels.Stick.RX, timeout=None, sleep_interval=.150, verbosity=0, **kwds):
     self.RX = RX
     self.timeout = timeout
     self.verbosity = verbosity
     self.sleep_interval = sleep_interval
     self.link.channel.setRX(self.RX)
  def start (self):
    self.start = time.time( )
  def done (self):
    if self.timeout and self.timeout > 0:
      delta = time.time( ) - self.start
      return delta > self.timeout
    return False
  def sleep (self):
    time.sleep(self.sleep_interval)
  def listen (self, formatter, **kwds):
    self.start( )
    link = self.link
    while not self.done( ):
      count = link.received( )
      if count < 1:
        # print "sleeping"
        log.info('sleeping {}'.format(.150))
        self.sleep( )
      else:
        if self.verbosity > 0:
          print datetime.now( ).isoformat( ), "count:", count
        for buf in link.dump_rx_buffer( ):
          formatter(buf)
          # print lib.hexdump(buf)

def choose_rx_channel (value):
  keys = dict(PumpTX=Channels.Pump.TX, PumpRX=Channels.Pump.RX)
  return keys.get(value, Channels.Pump.TX)

def setup_argparser (parser=None):
  import argparse
  import argcomplete
  from dateutil.tz import gettz
  parser = parser or argparse.ArgumentParser( )
  parser.add_argument('--verbosity', '-v', action='count')
  parser.add_argument('--rx', '-r', default='PumpTX', choices=['PumpTX', 'PumpRX'])
  parser.add_argument('--timeout', '-t', type=int, default=0)
  parser.add_argument('--sleep_interval', '-s', help="Amount to sleep between polling.", type=float, default=.150)
  parser.add_argument('--buffer', '-b', dest='stream', action='store_false', default=True)
  parser.add_argument('--format', '-f', default='text', choices=Formatter.formats)
  parser.add_argument('mac', help='MAC address of rileylink')
  parser.add_argument('--timezone', '-Z', type=gettz, default=gettz( ))
  parser.add_argument('--out', '-o', type=argparse.FileType('w'), default='-')

  argcomplete.autocomplete(parser)
  return parser

import json
class Formatter (object):
  formats = ['text', 'hexdump', 'json', 'markdown' ]
  def __init__ (self, args):
    self.args = args
    self.formatter = getattr(self, 'format_' + args.format)
    if not self.args.stream:
      self.data = [ ]
  def format_text (self, record):
    return """{dateString} {head} {rfpacket}
""".format(**record)

  def format_hexdump (self, record):
    return """{dateString}
{decocare_hex}
""".format(**record)

  def format_json (self, record):
    return "{}\n".format(json.dumps(record, indent=2, separators=(',', ': ')))

  def format_markdown (self, record):
    return """### {dateString} {op} {serial}

```
{payload_hex}
```

""".format(payload_hex=lib.hexdump(bytearray(record.get('payload').decode('hex'))), **record)

  def __call__ (self, buf):
    stamp = time.time( )
    dt = datetime.fromtimestamp(stamp).replace(tzinfo=self.args.timezone)
    msg = lib.hexdump(buf)
    rssi = buf[0:2]
    rfpacket = buf[2:]
    record = dict(date=stamp
           , dateString=dt.isoformat( )
           , rfpacket=str(rfpacket).encode('hex')
           , head=str(rssi).encode('hex')
           , serial=str(rfpacket[1:4]).encode('hex')
           , op=str(rfpacket[0:1]).encode('hex')
           , payload=str(rfpacket[4:]).encode('hex')
           , decocare_hex=msg )
    # print 
    if self.args.stream:
      self.args.out.write(self.formatter(record))
      self.args.out.flush( )
    else:
      self.data.append(record)
  def finish_concat (self):
    self.args.out.write(self.formatter(self.data))


if __name__ == '__main__':
  import sys
  parser = setup_argparser( )
  args = parser.parse_args( )
  # args = sys.argv[:]
  # mac = (args[1:2] or [None]).pop( )
  mac = args.mac
  channel = choose_rx_channel(args.rx)
  format_record = Formatter(args)
  if args.verbosity > 0:
    print args
  if args.mac:
    link = Link(mac, sleep_interval=args.sleep_interval)
    link.open( )
    monitor = Monitor(link, RX=channel, sleep_interval=args.sleep_interval, timeout=args.timeout, verbosity=args.verbosity)
    try:
      monitor.listen(format_record)
    except (KeyboardInterrupt), e:
      if args.verbosity > 0:
        print "Quitting"
    finally:
      if not args.stream:
        format_record.finish_concat( )
    link.close( )
