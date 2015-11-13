# NB

Please note that this is not yet in a working state! I'm running this project
with the [Release Early, Release Often](https://en.wikipedia.org/wiki/Release_early,_release_often)
methodology.

# MMeowlink

Use OpenAPS with a USB controller other than the Minimed-Supplied CareLink
adapter. These controllers have longer range than the CareLink.

This is based on the hard work done for the [https://github.com/bewest/mmblelink](mmblelink)
project by Ben West for the [https://github.com/ps2/rileylink(RileyLink) project.

Additionally, it uses the python [https://bitbucket.org/atlas0fd00m/rfcat](RfCat)
driver for communicating with the USB dongle.

# Hardware

You will need one of the supported RfCat wireless dongles to interface with the
The easiest to order is the [http://www.ti.com/tool/cc1111emk868-915](cc1111emk868-915).

Note that to install the RfCat firmware onto the device, you will either need
the [TI Debugger](http://www.ti.com/tool/cc-debugger), a
[http://goodfet.sourceforge.net](GoodFET), or a similar JTAG adapter.

This code has been tested with the RfCatDons-150225.hex file from
rfcat_150225.tgz on the [RfCat Download page](https://bitbucket.org/atlas0fd00m/rfcat/downloads)

# Not Currently Available in the USA

Currently this only works with non-USA pumps. Getting it to work with
other devices should be as simple as changing the Radio Frequencies to
match the [https://github.com/ps2/rileylink](RileyLink) project. However,
I've not any way to test this. Please submit a change if you can confirm
it works.

# LICENSE

MMeowlink Copyright (C) 2015 Oskar Pearson and Ben West.
This program comes with ABSOLUTELY NO WARRANTY. See the LICENSE file
for more details.
