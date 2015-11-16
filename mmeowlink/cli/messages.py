

from decocare.helpers import messages
from mmeowlink.rfcat_link import Link
from mmeowlink.handlers.stick import Pump

class SendMsgApp (messages.SendMsgApp):
  """
  mmeowlink adapter to decocare's SendMsgApp
  """
  def customize_parser (self, parser):
    parser.add_argument('--locale', default='US', choices=['EU', 'US'])
    parser = super(SendMsgApp, self).customize_parser(parser)
    return parser

  def prelude (self, args):
    self.link = link = Link(locale=args.locale)
    link.open()
    # get link
    # drain rx buffer
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
