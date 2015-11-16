
class FourBySix (object):
  SYMBOLS = {
    "010101" : "0",
    "110001" : "1",
    "110010" : "2",
    "100011" : "3",
    "110100" : "4",
    "100101" : "5",
    "100110" : "6",
    "010110" : "7",
    "011010" : "8",
    "011001" : "9",
    "101010" : "a",
    "001011" : "b",
    "101100" : "c",
    "001101" : "d",
    "001110" : "e",
    "011100" : "f"
  }

  CODES = [
    0b010101,
    0b110001,
    0b110010,
    0b100011,
    0b110100,
    0b100101,
    0b100110,
    0b010110,
    0b011010,
    0b011001,
    0b101010,
    0b001011,
    0b101100,
    0b001101,
    0b001110,
    0b011100
  ]
  @classmethod
  def encode (klass, buf):
    codes = [ ]
    for b in list(buf):
      codes.append(klass.CODES[( b >> 4 )])
      codes.append(klass.CODES[( b & 0xf )])
    bits = [ ]
    for code in codes:
      bits.append("{:06b}".format(code))
    bits = ''.join(bits) + "000000000000"
    remaining = bits[:]
    out = [ ]
    while len(remaining) > 7:
      byte_bits, remaining = remaining[0:8], remaining[8:]
      out.append(int(byte_bits, 2))
    return bytearray(out)

  @classmethod
  def decode (klass, buf):
    errors = [ ]
    symbols = [ ]
    data = bytearray( )
    bits = [ ]
    for byte in buf:
      bits.append("{:08b}".format(byte))
    # bits is now a long string of 1s and 0s '10010100101...000000'
    bits = ''.join(bits)
    while bits:
      # iterate 6 bits at a time
      word, bits = bits[:6], bits[6:]
      if word == '000000':
        break
      symbol = klass.SYMBOLS.get(word, None)
      if symbol is None:
        errors.append(dict(remaining=bits, word=word))
      else:
        symbols.append(symbol)

    decoded_hex = ''.join(symbols)
    data = bytearray(str(decoded_hex).decode('hex'))
    return data
