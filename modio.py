"""Utility functions and classes to handle olimex mod-io from python.

SETUP
=====

Before using this code, you need to make sure mod-io is configured and working
on your system. Assuming you have a debian based system (like ubuntu or
raspbian):

1) edit /etc/modules, by running 'sudo -s' and opening the file with your
   favourite editor. Make sure it has the lines:

     # ... random comments ...
     i2c-dev
     i2c_bcm2708 baudrate=50000

2) once /etc/modules has been edited, run:
  
     $ sudo service kmod start

   to load all the modules. Alternatively, you can reboot your system.

3) make sure debugging tools and libraries are installed:

     $ sudo apt-get install i2c-tools python-smbus 

3) verify that mod-io is accessible, and to which bus it is
   connected. You need to run

     $ sudo i2cdetect -y X

   with X being 0 or 1. X is the bus number. If you see a 58 (assuming you did
   not change the default address of mod-io) in the output, you found the right
   bus. Remember this number for later!
   
   If you don't see 58 anywhere, do you see some other number? Did you change
   mod-io address or firmware? Is it plugged correctly?  Is there a flashing
   orange led? If not, you may have problems with the firmware, power supply or
   connection of mod-io.

   Example:
   
   Check status of bus 0. There are all dashesh, mod-io is not here.

     $ sudo i2cdetect -y 0

            0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
       00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
       10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
       20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
       30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
       40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
       50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
       60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
       70: -- -- -- -- -- -- -- --                         

   Check status of bus 1. You can see mod-io on address 58! Good!

     $ sudo i2cdetect -y 1

            0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
       00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
       10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
       20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
       30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
       40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
       50: -- -- -- -- -- -- -- -- 58 -- -- -- -- -- -- -- 
       60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
       70: -- -- -- -- -- -- -- --         


HOW TO USE THE LIBRARY
======================

1) Copy the modio.py file or the whole directory next to
   your .py script, or somewhere in PYTHONPATH.

2) Import it with 'import modio' or 'from modio import modio'
   if you left the whole directory.

3) Use it! Examples:

    from modio import modio
    
    # BUS Number is the bus you found during setup, see instructions above!
    board = modio.Device(bus=1)
    
    # Take control of the first relay (number 1 on board)
    relay = modio.Relay(board, 1)
    
    # Turn it on!
    relay.CloseContact()
    
    # Check relay status.
    if relay.IsClosed():
      print "Relay is on"
    else:
      print "Relay is off"
    
    # Turn it off!
    relay.OpenContact()


PROBLEMS, ISSUES, or QUESTIONS?
===============================

Check out the wiki here:
  https://github.com/ccontavalli/python-olimex-modio/wiki

File problems, issues or other requests here:
  https://github.com/ccontavalli/python-olimex-modio/issues

Newer versions of the code are available here:
  https://github.com/ccontavalli/python-olimex-modio
"""

import smbus
import logging

class DeviceNotFoundException(IOError):
  """Raised if we cannot communicate with the device."""

class SMBBusNotConfiguredProperly(IOError):
  """Raised if we can't find the propber smbbus setup."""


class SmbBus(object):
  """Represent an SMB bus to read / write from modio."""

  def __init__(self, bus, address):
    """Instantiates a SmbBus.

    Args:
      bus: integer, bus number, generally 0 or 1.
      address: integer, generally 0x58, the address where
        mod-io can be found.
    """
    self.address = address
    try:
      self.smb = smbus.SMBus(bus)
    except IOError:
      raise SMBBusNotConfiguredProperly(
          "could not find files for access to SMB bus, you need to load "
          "the proper modules")

  def Write(self, key, value):
    """Sends a request to olimex mod-io."""
    try:
      self.smb.write_byte_data(self.address, key, value)
    except IOError:
      raise DeviceNotFoundException("Could not communicate with device")


class FakeBus(object):
  """Emulates a SmbBus for testing purposes."""

  def __init__(self, bus, address):
    logging.warning("using fake SMB bus instead of real one")

    self.bus = bus
    self.address = address

  def Write(self, key, value):
    logging.debug("writing on bus %s, address %s, key %s, value %s",
                  self.bus, self.address, key, value)


class Device(object):
  """Represents a mod-io device, allows to perform common operations."""

  # Default address where mod-io can be found on the SMB bus.
  DEFAULT_ADDRESS = 0x58
  # Bus number, you can use i2c tools to find it.
  DEFAULT_BUS = 1

  # Command to use to pilot relays.
  RELAY_COMMAND = 0x10

  def __init__(self, address=DEFAULT_ADDRESS, bus=DEFAULT_BUS, communicator=SmbBus):
    """Constructs a device object.

    Args:
      address: integer, mod-io address.
      bus: integer, SMB bus to use to communicate with mod-io.
      communicator: SmbBus or FakeBus, for testing purposes.
    """
    self.communicator = communicator(bus, address)
    self.SetRelays(0)

  def GetRelays(self):
    """Returns the relay status as a bitmask."""
    return self.relay_status

  def SetRelays(self, value):
    """Set and return the relay status."""
    if value < 0 or value > 0xf:
      raise ValueError("Invalid relay value: can be between 0 and 0xF")
    self.communicator.Write(self.RELAY_COMMAND, value)
    self.relay_status = value
    return self.relay_status

  def GetRelayBit(self, relay):
    """Returns the bit that represents the status of the specified relay.

    The status of the relays is represented as a bit mask that can be
    written to mod-io to change the status of the relay (0 open, 1 closed).

    Args:
      relay: int, 1 - 4, the relay to . Note that olimex
        mod-io has exactly 4 relays.

    Returns:
      int, the bit of the relay. For relay 0, 1, for relay 1, 2, and
      so on. Mostly useful as this function validates the number.

    Raises:
      ValueError, if the relay number is invalid.
    """
    if relay < 1 or relay > 4:
      raise ValueError("Invalid relay: must be between 1 and %d", 4)
    return 1 << (relay - 1)

  def IsRelayClosed(self, relay):
    """Returns the status of a relay.

    Args:
      relay: int, 1 - 4, the relay to enable. Note that olimex
        mod-io has exactly 4 relays.

    Raises:
      ValueError if an invalid relay number is passed.

    Returns:
      False if the releay is opened, True if closed.
    """
    relay = self.GetRelayBit(relay)
    if self.relay_status & relay:
      return True
    return False

  def CloseContactRelay(self, relay):
    """CloseContact a specific relay.

    Args:
      relay: int, 1 - 4, the relay to enable. Note that olimex
        mod-io has exactly 4 relays.

    Raises:
      ValueError if an invalid relay number is passed.
    """
    self.SetRelays(self.GetRelays() | self.GetRelayBit(relay))

  def OpenContactRelay(self, relay):
    """OpenContact a specific relay.

    Args:
      relay: int, 1 - 4, the relay to enable. Note that olimex
        mod-io has exactly 4 relays.

    Raises:
      ValueError if an invalid relay number is passed.
    """
    self.SetRelays(self.GetRelays() & ((~self.GetRelayBit(relay)) & 0xf))

class Relay(object):
  """Represents a single relay, convenience wrapper around the device class."""
  def __init__(self, device, number):
    self.device = device
    self.number = number

  def IsClosed(self):
    """Get status of this relay."""
    return self.device.IsRelayClosed(self.number)

  def Get(self):
    """Deprecated, use IsClosed instead."""
    return self.IsClosed()

  def OpenContact(self):
    """Disables this relay, by opening the contact."""
    self.device.OpenContactRelay(self.number)

  def CloseContact(self):
    """Enables this relay, by closing the contact."""
    self.device.CloseContactRelay(self.number)
