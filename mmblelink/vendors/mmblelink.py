
"""
mmblelink - openaps driver for mmblelink
This emulates the stick from decocare, using the RileyLink.
"""
from openaps.uses.use import Use
from openaps.uses.registry import Registry
from openaps.configurable import Configurable
import decocare
import argparse
import json
from openaps.vendors import medtronic
# from decocare import stick, session, link, commands, history
from datetime import datetime
from dateutil import relativedelta
from dateutil.parser import parse

from .. cli import messages
from .. import link
from .. handlers.stick import Pump


def configure_use_app (app, parser):
  pass
  # parser.add_argument('foobar', help="LOOK AT ME")

def configure_add_app (app, parser):
  scanned = link.scanner( )
  mac = None
  if scanned and len(scanned) > 0:
    mac = scanned.items( ).pop( )
  parser.add_argument('mac', help="MAC address", default=mac)
  medtronic.configure_add_app(app, parser)

def configure_app (app, parser):
  if app.parent.name == 'add':
    """
    print "CONFIG INNER", app, app.parent.name, app.name
    """
def configure_parser (parser):
  pass
def main (args, app):
  """
  print "MEDTRONIC", args, app
  print "app commands", app.selected.name
  """


use = Registry( )

@use( )
class scan (Use):
  """ scan for usb stick """
  def configure_app (self, app, parser):
    pass
    # print "hahaha"
  def scanner (self):
    scanned = link.scanner( )
    mac = None
    if scanned and len(scanned) > 0:
      mac = scanned.items( ).pop( )
    return mac
  def main (self, args, app):
    return self.scanner( )


def setup_medtronic_uart (self):
  log = logging.getLogger(decocare.__name__)
  level = getattr(logging, self.device.get('logLevel', 'WARN'))
  address = self.device.get('logAddress', '/dev/log')
  log.setLevel(level)
  for previous in log.handlers[:]:
    log.removeHandler(previous)
  log.addHandler(logging.handlers.SysLogHandler(address=address))
  serial = self.device.get('serial')
  mac = self.device.get('mac', None)
  if mac is None:
    mac = self.scanner( )
  sleep_interval = float(self.device.get('sleep_interval', .020))
  self.uart = link.Link(mac or self.scanner( ), sleep_interval)
  self.uart.open( )
  self.uart.channel.setTX(messages.choose_channel(self.device.get('tx', '2')))
  self.uart.channel.setRX(messages.choose_channel(self.device.get('rx', '0')))
  self.pump = Pump(self.uart, serial)
  # stats = self.uart.interface_stats( )


import logging
import logging.handlers
class MedtronicTask (scan, medtronic.MedtronicTask):
  def setup_medtronic (self):
    setup_medtronic_uart(self)
    return

def make (usage, Master=MedtronicTask, setup_func=setup_medtronic_uart):
  class EmulatedUsage (usage, Master):
    __doc__ = usage.__doc__
    __name__ = usage.__name__
    def setup_medtronic (self):
      setup_func(self)

  # EmulatedUsage.__doc__ = usage.__doc__
  EmulatedUsage.__name__ = usage.__name__
  return EmulatedUsage
def substitute (name, usage, Master=MedtronicTask, Original=medtronic.MedtronicTask, setup_func=setup_medtronic_uart):
  if issubclass(usage, Original):
    adapted = make(usage, Master=Master, setup_func=setup_func)
    adapted.__name__ = name
    if name not in use.__USES__:
      use.__USES__[name] = adapted
      return use

def set_config (args, device):
  device.add_option('tx', '2')
  device.add_option('rx', '0')
  device.add_option('serial', args.serial)

def display_device (device):
  return ''
known_uses = [
  # Session,
]
# ] + 
# ] + filter(lambda x: x, [ substitute(name, usage) for name, usage in medtronic.use.__USES__.items( ) ])
replaced = [ substitute(name, usage) for name, usage in medtronic.use.__USES__.items( ) ]

def get_uses (device, config):
  known = use.get_uses(device, config)
  all_uses = known_uses[:] + use.get_uses(device, config)
  all_uses.sort(key=lambda usage: getattr(usage, 'sortOrder', usage.__name__))
  return all_uses
