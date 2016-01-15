from mmeowlink.exceptions import UnknownLinkType

from mmeowlink.vendors.mmcommander_link import MMCommanderLink
from mmeowlink.vendors.subg_rfspy_link import SubgRfspyLink

class LinkBuilder():
  def build(self, radio_type, port, **kwds):
    if radio_type == 'mmcommander':
      return MMCommanderLink(port)
    elif radio_type == 'subg_rfspy':
      return SubgRfspyLink(port, **kwds)
    else:
      raise UnknownLinkType("Unknown radio type '%s' - check parameters" % radio_type)
