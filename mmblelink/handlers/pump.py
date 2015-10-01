import dateutil
from decocare import commands
from decocare import lib
import collections
import types
import time
from mmblelink.packets.rf import Packet

class PumpEmulate (object):
  def __init__ (self, monitor, serial='909090', name="mmblelink"):
    self.monitor = monitor
    self.link = monitor.link
    self.name = name
    self.serial = serial
    self.setup( )
  def setup (self):
    self.link.channel.setRX(0)
    self.link.channel.setTX(2)
  def run (self, timeout=None):
    pass
  def start (self):
    self.start = time.time( )
  def done (self):
    if self.timeout and self.timeout > 0:
      delta = time.time( ) - self.start
      return delta > self.timeout
    return False
  def sleep (self):
    time.sleep(self.sleep_interval)
  def listen (self, states, strict=False, **kwds):
    self.start( )
    self.states = states
    link = self.link
    for packet in self.monitor.generate(strict=strict):
      states.receive(packet)
      states.respond(link)
      if packet.serial == self.serial and packet.type == 0xA7:
        print "RECEIVED REQUEST", packet

class States (object):
  responders = dict( )
  queue = [ ]
  def __init__ (self, serial=None, model=None):
    self.serial = serial
    self.model = model
    self.queue = collections.deque( ) 
    self.responders = dict( )
    self._setup_commands( )
  def _setup_commands (self):
    for com in commands.__all__:
      command = getattr(commands, com)
      if not isinstance(command, types.FunctionType):
        response = Responder(command, self)
        self.responders[command.code] = response
  def receive (self, packet):
    if packet.serial == self.serial and packet.type == 0xA7:
      # TODO: increment counters
      print "RECEIVING ", packet, packet.op in self.responders
      if packet.op in self.responders:
        name = 'on%s' % self.responders[packet.op].name
        func = getattr(self, name, None)
        print name, func
        if func:
          self.queue.append((func, packet, self.responders[packet.op]))


  def respond (self, link):
    print "RESPONDING ", self.queue
    while self.queue:
      func, packet, resp = self.queue.pop( )


      payload = func(packet)
      buf = resp.respond(payload)
      print "SENDING", str(buf).encode('hex')
      print lib.hexdump(buf)
      link.write(buf)
      
  def onReadPumpModel (self, packet):
    body = bytearray(self.model) + bytearray([0x00]) 
    payload = bytearray([len(body) + 3, len(self.model)]) + body
    missing = bytearray([0x00]) * (65 - len(payload))
    return payload + bytearray(missing)
    

class Responder (object):
  def __init__ (self, com, state):
    # print com, com.__name__
    self.name = com.__name__.split('.').pop( )
    #print com
    self.com = com
    self.code = com.code
    self.state = state
    self.resp = Packet.fromCommand(com, serial=state.serial, crc=0x00)
  def __call__ (self, packet):
    if packet.valid and packet.serial == self.serial:
      print "do something", packet
  def respond (self, payload):
    self.resp = self.resp.update(payload)
    return self.resp.assemble( )
    # resp = Packet(type=0xA7)

def setup_argparser (parser=None):
  import argparse
  import argcomplete
  from dateutil.tz import gettz
  parser = parser or argparse.ArgumentParser( )
  parser.add_argument('--verbosity', '-v', action='count')
  parser.add_argument('--rx', '-R', default='PumpRX', choices=['0', '1', '2', 'PumpTX', 'PumpRX'])
  parser.add_argument('--tx', '-T', default='PumpTX', choices=['0', '1', '2', 'PumpTX', 'PumpRX'])
  parser.add_argument('--timeout', '-t', type=int, default=0)
  parser.add_argument('--sleep_interval', '-s', help="Amount to sleep between polling.", type=float, default=.150)
  # parser.add_argument('--buffer', '-b', dest='stream', action='store_false', default=True)
  # parser.add_argument('--format', '-f', default='text', choices=Formatter.formats)
  parser.add_argument('--strict', '-S', action='store_false', default=True)
  parser.add_argument('--model', '-M', default='mmblelink', help="Name to send")
  parser.add_argument('mac', help='MAC address of rileylink')
  parser.add_argument('serial', help='Serial of fake pump to emulate.')
  parser.add_argument('--timezone', '-Z', type=gettz, default=gettz( ))
  parser.add_argument('--out', '-o', type=argparse.FileType('w'), default='-')

  argcomplete.autocomplete(parser)
  return parser

if __name__ == '__main__':
  from mmblelink.monitor import Monitor, choose_rx_channel as choose_channel
  from mmblelink.link import Link
  parser = setup_argparser( )
  args = parser.parse_args( )
  if args.verbosity > 0:
    print args
  if args.mac and args.serial:
    mac = args.mac
    link = Link(mac, sleep_interval=args.sleep_interval)
    link.open( )
    monitor = Monitor(link, RX=choose_channel(args.rx), sleep_interval=args.sleep_interval, timeout=args.timeout, verbosity=args.verbosity)
    state = States(args.serial, args.model)
    emulate = PumpEmulate(monitor, args.serial, args.model)
    try:
      emulate.listen(state, strict=args.strict)
    except (KeyboardInterrupt), e:
      if args.verbosity > 0:
        print "Quitting"
    finally:
      pass
    link.close( )
