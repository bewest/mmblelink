# Meowlink

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

# Not Available in the USA

Currently this only works with non-USA pumps. Getting it to work with
other devices should be as simple as changing the Radio Frequencies to
match the [https://github.com/ps2/rileylink](RileyLink) project. However,
I've not any way to test this. Please submit a change if you can confirm
it works.

# LICENSE

Meowlink Copyright (C) 2015 Oskar Pearson
This program comes with ABSOLUTELY NO WARRANTY. See the LICENSE file
for more details.
