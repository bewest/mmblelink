
# LICENSE

[![Join the chat at https://gitter.im/oskarpearson/mmeowlink](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/oskarpearson/mmeowlink?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

MMeowlink Copyright (C) 2015 Oskar Pearson and Ben West.
This program comes with ABSOLUTELY NO WARRANTY. See the LICENSE file
for more details.

# NB

Please note that this is not yet in a stable state! I'm running this project
with the [Release Early, Release Often](https://en.wikipedia.org/wiki/Release_early,_release_often)
methodology.

* You must agree to the LICENSE terms
* It does not (yet) have tests, and the code quality is not anywhere where I
  would like it to be.

# MMeowlink

MMeowlink acts as an OpenAPS driver. It allows you to replace the CareLink
USB device with a [MMCommander](https://github.com/jberian/mmcommander) stick.

This is based on the hard work done by Ben West for the [mmblelink](https://github.com/bewest/mmblelink)
project for the [RileyLink](https://github.com/ps2/rileylink).

## So what's that get us?

1. This gives us better range than the CareLink can provide. Our experience is
  that the device can cover a reasonably sized room when placed centrally.
2. When placed a under a bed, there are no missing gaps in overnight OpenAPS
  coverage. You no longer need two CareLink sticks for coverage.
3. Unlike the CareLink stick, the MMCommander sticks can be used with the [Intel
  Edison](http://www.intel.com/content/www/us/en/do-it-yourself/edison.html).
  This allows us to replace the Raspberry Pi with the much smaller and lower
  power-consumption Edison.

# Hardware

You will need the following:

- [cc1111emk868-915](http://www.ti.com/tool/cc1111emk868-915)
- [TI Debugger](http://www.ti.com/tool/cc-debugger) or a
  [GoodFET](http://goodfet.sourceforge.net) or similar.
  (You only need this for the first installation. See if a local Hackspace
    or other user could help you)
- [Writeable MMCommander Firmware](https://github.com/jberian/mmcommander)
  See the instructions for how to set this up.

# Writing the Firmware

I still hope to release an RfCat version of this software,
which would remove the requirement to write custom firmware. At this stage,
this process is still very cumbersome.

The best instructions for this are on the MMCommander website. However,
the process is as follows.

1. Download the MMCommander source code.
2. Sign up for a trial license of the [EW8051 compiler](http://supp.iar.com/Download/SW/?item=EW8051-EVAL) / [Homepage](https://www.iar.com/iar-embedded-workbench/8051/)
3. Install the compiler with the license code emailed to you automatically.
4. Open the MMCommander project's src/MMCommander/MMCommander.eww file
5. Edit the configuration.h file, setting:
5.1 #define _TX_ENABLE_ 1
5.2 #define _REPEATED_COMMAND_ENABLED_ 0
5.3 #define _TX_FILTER_ENABLE_ 0
6. Build the project, which will generate you a .hex file.

Once built, you will need to write the firmware to the stick.
To do this, you will need to follow the instructions for the
[TI Flash Programmer Tool](http://www.ti.com/tool/flash-programmer).
Alternatively, [CC-Tool](http://sourceforge.net/projects/cctool/) works well too.

# Setup

As this is still a WIP, I don't have a Python package available yet. Install
it as follows:

    cd ~
    git clone https://github.com/oskarpearson/mmeowlink.git mmeowlink-source
    cd mmeowlink-source
    git checkout mmcommander
    pip install -e .

Then, add this to your openaps.ini. Note that you should have an existing
"pump" section that you'll need to change to match this:

    [vendor "mmeowlink.vendors.mmeowlink"]
    path = .
    module = mmeowlink.vendors.mmeowlink

    [device "pump"]
    vendor = mmeowlink.vendors.mmeowlink
    extra = pump.ini

You should then be able to run `openaps report invoke read_clock.json` or
similar.
