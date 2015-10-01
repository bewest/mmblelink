
from collections import namedtuple
import time
import struct
from datetime import datetime
from decocare import lib

_Packet = namedtuple('Packet', [
  'rssi', 'seq',
  'type', 'serial', 'op', 'payload', 'crc',
  'date', 'dateString', 'valid', 'chan',
  'payload_hex'
  ])


class Packet (_Packet):
  @classmethod
  def fromCommand (klass, command, payload=bytearray([0x00]), serial=None,
                          stamp=None, timezone=None, chan=None,
                          rssi=None, seq=None, crc=None, valid=None):
    stamp = stamp or time.time( )
    dt = datetime.fromtimestamp(stamp).replace(tzinfo=timezone)
    rftype = 0xA7
    record = dict(date=stamp * 1000
           , dateString=dt.isoformat( )
           , rssi = rssi
           , seq = seq
           , type = rftype
           , serial=serial
           , op = command.code
           , payload = payload
           , payload_hex = str(payload).encode('hex')
           , crc = crc
           , valid = valid
           , chan = chan
           # , rfpacket=str(rfpacket).encode('hex')
           # , head=str(head).encode('hex')
           # , op=str(rfpacket[0:1]).encode('hex')
           # , decocare_hex=msg
           )
    pkt = klass(**record)
    return pkt
  def update (self, payload=None, chan=None):
    pkt = self
    if payload:
      pkt = pkt._replace(payload=payload)
    pkt = pkt._replace(crc=pkt.genCRC( ))
    # self.crc =
    return pkt
  def assemble (self):
    pkt = self.update( )
    buf = bytearray([self.type])
    buf.extend(pkt.serial.decode('hex'))
    buf.extend(bytearray([pkt.op]))
    buf.extend(pkt.payload)
    buf.extend(bytearray([pkt.crc]))
    return buf

  def genCRC (self):
    buf = bytearray([self.type])
    buf.extend(self.serial.decode('hex'))
    buf.extend(bytearray([self.op]))
    buf.extend(self.payload)
    calculated = lib.CRC8.compute(buf)
    return calculated
  @classmethod
  def fromBuffer (klass, buf, stamp=None, timezone=None, chan=None):
    stamp = stamp or time.time( )
    # dt = datetime.fromtimestamp(stamp).replace(tzinfo=self.args.timezone)
    dt = datetime.fromtimestamp(stamp).replace(tzinfo=timezone)
    msg = lib.hexdump(buf)
    head = buf[0:2]
    rssi, seq = struct.unpack('bB', str(head))

    rfpacket = buf[2:]
    rftype   = buf[0]
    serial   = str(rfpacket[1:4]).encode('hex')
    command  = None
    payload  = None
    crc      = None
    valid    = False
    if serial and len(rfpacket) > 3:
      rftype   = rfpacket[0]
      command  = rfpacket[4]
      payload  = rfpacket[5:-1]
      crc = int(rfpacket[-1])
      calculated = lib.CRC8.compute(rfpacket[:-1])
      valid = calculated == crc
    record = dict(date=stamp * 1000
           , dateString=dt.isoformat( )
           , rssi = rssi
           , seq = seq
           , type = rftype
           , serial=serial
           , op = command
           , payload = payload
           , payload_hex = str(payload).encode('hex')
           , crc = crc
           , valid = valid
           , chan = chan
           # , rfpacket=str(rfpacket).encode('hex')
           # , head=str(head).encode('hex')
           # , op=str(rfpacket[0:1]).encode('hex')
           # , decocare_hex=msg
           )
    pkt = klass(**record)
    return pkt


