#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

from mmblelink.cli import messages
# from decocare.helpers import messages

if __name__ == '__main__':
  app = messages.SendMsgApp( )
  app.run(None)

