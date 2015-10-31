

from decocare.helpers import messages
from mmblelink.link import Link
from mmblelink.handlers.stick import Pump
from mmblelink.monitor import choose_rx_channel as choose_channel

class SendMsgApp (messages.SendMsgApp):
  """
  mmblelink adapter to decocare's SendMsgApp
  """
  def customize_parser (self, parser):
    parser.add_argument('--rx', '-R', default='PumpTX', type=choose_channel, choices=[0, 1, 2, '0', '1', '2', 'PumpTX', 'PumpRX'])
    parser.add_argument('--tx', '-T', default='PumpRX', type=choose_channel, choices=[0, 1, 2, '0', '1', '2', 'PumpTX', 'PumpRX'])
    parser.add_argument('MAC', help="RileyLink address")
    parser.add_argument('--sleep_interval', '-s', help="Amount to sleep between polling.", type=float, default=.150)
    parser = super(SendMsgApp, self).customize_parser(parser)
    return parser
  def prelude (self, args):
    mac = args.MAC
    self.link = link = Link(mac, sleep_interval=args.sleep_interval)
    link.open( )
    # get link
    # drain rx buffer
    self.link.dump_rx_buffer( )
    self.link.channel.setTX(args.tx)
    self.link.channel.setRX(args.rx)
    self.pump = Pump(self.link, args.serial)
    print args
    print args.command
    if args.no_rf_prelude:
      return
    if not args.autoinit:
      if args.init:
        self.pump.power_control(minutes=args.session_life)
    else:
      self.autoinit(args)
    self.sniff_model( )

  def postlude (self, args):
    # self.link.close( )
    return

