import glob

# Based on https://github.com/bewest/decoding-carelink/blob/master/decocare/scan.py

def scan ():
  results = glob.glob('/dev/RFCAT[0-9]*')
  return (results[0:1] or ['']).pop( )

if __name__ == '__main__':
  candidate = scan( )
  print candidate
