"""Utility functions to handle olimex mod-io from python."""

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

  # Bit value to use to enable/disable each relay.
  RELAYS = [1<<0, 1<<1, 1<<2, 1<<3]

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
    """Set the relay status."""
    if value < 0 or value > 0xf:
      raise ValueError("Invalid relay value: can be between 0 and 0xF")
    self.communicator.Write(self.RELAY_COMMAND, value)
    self.relay_status = value

  def GetRelay(self, relay):
    """Returns the status of a relay.

    Args:
      relay: int, 0 - 3, the relay to enable. Note that olimex
        mod-io has exactly 4 relays.

    Raises:
      ValueError if an invalid relay number is passed.

    Returns:
      False if the releay is disable, True if enabled.
    """
    try:
      relay = self.RELAYS[relay]
    except IndexError:
      raise ValueError(
          "Invalid relay: must be between 0 and %d", len(self.RELAYS) - 1)
    if self.relay_status & relay:
      return True
    return False

  def CloseContactRelay(self, relay):
    """CloseContact a specific relay.

    Args:
      relay: int, 0 - 3, the relay to enable. Note that olimex
        mod-io has exactly 4 relays.

    Raises:
      ValueError if an invalid relay number is passed.
    """
    try:
      self.SetRelays(self.GetRelays() | self.RELAYS[relay])
    except IndexError:
      raise ValueError(
          "Invalid relay: must be between 0 and %d", len(self.RELAYS) - 1)

  def OpenContactRelay(self, relay):
    """OpenContact a specific relay.

    Args:
      relay: int, 0 - 3, the relay to enable. Note that olimex
        mod-io has exactly 4 relays.

    Raises:
      ValueError if an invalid relay number is passed.
    """
    try:
      self.SetRelays(self.GetRelays() & ((~self.RELAYS[relay]) & 0xf))
    except IndexError:
      raise ValueError(
          "Invalid relay: must be between 0 and %d", len(self.RELAYS) - 1)

class Relay(object):
  """Represents a single relay, convenience wrapper around the device class."""
  def __init__(self, device, number):
    self.device = device
    self.number = number

  def Get(self):
    """Get status of this relay."""
    self.device.GetRelay(self.number)

  def OpenContact(self):
    """Disables this relay, by opening the contact."""
    self.device.OpenContactRelay(self.number)

  def CloseContact(self):
    """Enables this relay, by closing the contact."""
    self.device.CloseContactRelay(self.number)
