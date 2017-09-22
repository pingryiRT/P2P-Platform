from unittest import TestCase
from Message import Message
from Peer import Peer

class MessageTests(TestCase):

  def setUp(self):
    recip = Peer("1.1.1.1")
    recip.name = "Bob"
    self.m = Message("me", recip)

  def testEmptyContents(self):
    self.assertEqual(self.m.contents, "")

  def testNoPeers(self):
    self.assertEqual(self.m.peers, [])
