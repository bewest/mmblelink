import glob
import os

# Based on https://github.com/bewest/decoding-carelink/blob/master/decocare/scan.py

def scan ():
  if os.environ.get('MMEOWLINK_PORT'):
    return os.environ.get('MMEOWLINK_PORT')

  results = glob.glob('/dev/ttyACM[0-9]*')
  if not results:
    raise PortNotFound("Cannot find serial port - set MMEOWLINK_PORT environment variable to the appropriate device (eg: /dev/ttyACM0)")
  return results[0]

if __name__ == '__main__':
  candidate = scan( )
  print candidate
