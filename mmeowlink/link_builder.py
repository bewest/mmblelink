import os

from mmeowlink.exceptions import UnknownLinkType

from mmeowlink.vendors import mmeowlink_scan

from mmeowlink.vendors.mmcommander_link import MMCommanderLink
from mmeowlink.vendors.subg_rfspy_link import SubgRfspyLink

class LinkBuilder():
  def build(self):
    impl_name = os.environ.get('MMEOWLINK_TYPE')

    port = mmeowlink_scan.scan()

    if impl_name  == 'mmcommander':
      return MMCommanderLink(port)
    elif impl_name == 'subg_rfspy':
      return SubgRfspyLink(port)
    else:
      raise UnknownLinkType("Unknown link type - set MMEOWLINK_TYPE environment variable")
