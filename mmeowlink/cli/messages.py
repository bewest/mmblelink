from decocare.helpers import messages
from mmeowlink.handlers.stick import Pump
from mmeowlink.link_builder import LinkBuilder

class SendMsgApp (messages.SendMsgApp):
  """
  mmeowlink adapter to decocare's SendMsgApp
  """
  def customize_parser (self, parser):
    parser = super(SendMsgApp, self).customize_parser(parser)
    return parser

  def prelude (self, args):
    self.link = link = LinkBuilder().build()
    link.open()
    # get link
    # drain rx buffer
    self.pump = Pump(self.link, args.serial)
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
