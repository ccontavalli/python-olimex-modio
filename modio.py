"""Utility functions to handle olimex mod-io from python."""

import smbus

class DeviceNotFoundException(Exception):
  """Raised if we cannot communicate with the device."""

class Device(object):
  DEFAULT_ADDRESS = 0x58
  DEFAULT_BUS = 1

  # Command to use to pilot relays.
  RELAY_COMMAND = 0x10

  # Bit value to use to enable/disable each relay.
  RELAYS = [1<<0, 1<<1, 1<<2, 1<<3]

  def __init__(self, address=DEFAULT_ADDRESS, bus=DEFAULT_BUS):
    self.address = address
    self.bus = bus

    self.smb = smbus.SMBus(bus)

    self.SetRelays(0)

  def GetRelays(self):
    """Returns the relay status as a bitmask."""
    return self.relay_status

  def SetRelays(self, value):
    """Set the relay status."""
    if value < 0 or value > 0xf:
      raise ValueError("Invalid relay value: can be between 0 and 0xF")
    self.Write(self.RELAY_COMMAND, value)
    self.relay_status = value

  def Write(self, key, value):
    """Sends a request to olimex mod-io."""
    try:
      self.smb.write_byte_data(self.address, key, value)
    except IOError:
      raise DeviceNotFoundException("Could not communicate with device")

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

  def EnableRelay(self, relay):
    """Enable a specific relay.

    Args:
      relay: int, 0 - 3, the relay to enable. Note that olimex
        mod-io has exactly 4 relays.

    Raises:
      ValueError if an invalid relay number is passed.
    """
    try:
      self.SetRelay(self.GetRelays() | self.RELAYS[relay])
    except IndexError:
      raise ValueError(
          "Invalid relay: must be between 0 and %d", len(self.RELAYS) - 1)

  def DisableRelay(self, relay):
    """Disable a specific relay.

    Args:
      relay: int, 0 - 3, the relay to enable. Note that olimex
        mod-io has exactly 4 relays.

    Raises:
      ValueError if an invalid relay number is passed.
    """
    try:
      self.SetRelay(self.GetRelays() & ((~self.RELAYS[relay]) & 0xf))
    except IndexError:
      raise ValueError(
          "Invalid relay: must be between 0 and %d", len(self.RELAYS) - 1)

class Relay(object):
  """Represents a single relay, convenience wrapper around the device class."""
  def __init__(self, device, number):
    self.device = device
    self.relay = number

  def Get(self):
    """Get status of this relay."""
    self.device.GetRelay(self.number)

  def Disable(self):
    """Disables this relay."""
    self.device.DisableRelay(self.number)

  def Enable(self):
    """Enables this relay."""
    self.device.EnableRelay(self.number)
