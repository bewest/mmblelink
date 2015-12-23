class CommsException(Exception):
  pass

class InvalidPacketReceived(Exception):
  pass

class MMCommanderNotWriteable(Exception):
  pass

class PortNotFound(Exception):
  pass

class UnknownLinkType (Exception):
  pass
