import unittest
import modio

class ModioTest(unittest.TestCase):
  def testDeviceSMBBus(self):
    self.assertRaises(
        modio.SMBBusNotConfiguredProperly, modio.Device, bus=100)
    self.assertRaises(IOError, modio.Device, bus=100)

  def testSetRelaysErrors(self):
    board = modio.Device(communicator=modio.FakeBus)
    self.assertRaises(ValueError, board.SetRelays, -1)
    self.assertRaises(ValueError, board.SetRelays, 31)

  def testGetSetRelays(self):
    board = modio.Device(communicator=modio.FakeBus)
    self.assertEquals(0, board.GetRelays())
    for i in xrange(0, 15):
      self.assertEquals(i, board.SetRelays(i))
      self.assertEquals(i, board.GetRelays())

  def testInvalidRelayDetected(self):
    board = modio.Device(communicator=modio.FakeBus)
    self.assertRaises(ValueError, board.IsRelayClosed, 0)
    self.assertRaises(ValueError, board.IsRelayClosed, 5)
    self.assertRaises(ValueError, board.IsRelayClosed, -1)
    self.assertRaises(ValueError, board.IsRelayClosed, -5)
    self.assertRaises(ValueError, board.CloseContactRelay, 0)
    self.assertRaises(ValueError, board.CloseContactRelay, 5)
    self.assertRaises(ValueError, board.CloseContactRelay, -1)
    self.assertRaises(ValueError, board.CloseContactRelay, -5)
    self.assertRaises(ValueError, board.OpenContactRelay, 0)
    self.assertRaises(ValueError, board.OpenContactRelay, 5)
    self.assertRaises(ValueError, board.OpenContactRelay, -5)
    self.assertRaises(ValueError, board.OpenContactRelay, -1)

  def testOpenCloseOneRelay(self):
    board = modio.Device(communicator=modio.FakeBus)
    self.assertEquals(0, board.GetRelays())
    for i in xrange(1, 5):
      self.assertEquals(False, board.IsRelayClosed(i))
      board.CloseContactRelay(i)
      self.assertEquals(True, board.IsRelayClosed(i))
      board.OpenContactRelay(i)
      self.assertEquals(False, board.IsRelayClosed(i))

  def testOpenCloseMultipleRelays(self):
    board = modio.Device(communicator=modio.FakeBus)
    self.assertEquals(0, board.GetRelays())
    # Close one relay at a time.
    for i in xrange(1, 5):
      # Verify that all relays we closed before are still closed.
      for j in xrange(i - 1, 1, -1):
        self.assertEquals(True, board.IsRelayClosed(j))
      # While the rest are still opened.
      for j in xrange(i, 5):
        self.assertEquals(False, board.IsRelayClosed(j))

      # Check that closing relay has desired effect.
      board.CloseContactRelay(i)
      self.assertEquals(True, board.IsRelayClosed(i))

    # Now that they are all closed, open one relay at a time.
    self.assertEquals(0xf, board.GetRelays())
    for i in xrange(1, 5):
      # Verify that all relays we opened before are still opened.
      for j in xrange(i - 1, 1, -1):
        self.assertEquals(False, board.IsRelayClosed(j))
      # While the rest are still closed.
      for j in xrange(i, 5):
        self.assertEquals(True, board.IsRelayClosed(j))

      # Check that opening relay has desired effect.
      board.OpenContactRelay(i)
      self.assertEquals(False, board.IsRelayClosed(i))

  def testSingleRelayValidation(self):
    board = modio.Device(communicator=modio.FakeBus)
    self.assertRaises(ValueError, modio.Relay, board, -1)
    self.assertRaises(ValueError, modio.Relay, board, 0)
    self.assertRaises(ValueError, modio.Relay, board, 5)

if __name__ == '__main__':
  unittest.main()
