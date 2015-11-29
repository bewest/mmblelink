import glob
import os

# Based on https://github.com/bewest/decoding-carelink/blob/master/decocare/scan.py

def scan ():
  if os.environ.get('MMCOMMANDER_PORT'):
    return os.environ.get('MMCOMMANDER_PORT')

  results = glob.glob('/dev/ttyACM[0-9]*')
  return (results[0:1] or ['']).pop( )

if __name__ == '__main__':
  candidate = scan( )
  print candidate
