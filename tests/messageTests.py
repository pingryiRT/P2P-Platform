from unittest import TestCase
from Message import Message, message_from_xml
from Peer import Peer

class MessageTests(TestCase):

  def setUp(self):

    sndr = Peer("2.2.2.2")
    sndr.name = "Alice"
    sndr.id = "AliceID"

    recip = Peer("1.1.1.1")
    recip.name = "Bob"
    recip.id = "BobID"

    self.m = Message(sndr)
    self.m.recipient = recip


  def testEmptyContents(self):
    self.assertEqual(self.m.contents, "")

  def testNoPeers(self):
    self.assertEqual(self.m.peers, set())

  def testToXml(self):
    xml = self.m.to_xml()
    correct = b"<message><sender>AliceID</sender><recipient>BobID</recipient><peers /><contents /></message>"
    self.assertEqual(xml, correct)

  def testXmlAndBack(self):
    n = message_from_xml(self.m.to_xml())
    self.assertEqual(self.m, n)

    #TODO These should probably be separate tests with separate asserts
    '''
    print(self.m.sender       == n.sender)
    print(self.m.recipient    == n.recipient)
    print(self.m.shuttingDown == n.shuttingDown)
    print(self.m.requestPeers == n.requestPeers)
    print(self.m.peers        == n.peers)
    print(self.m.contents     == n.contents)
    '''

  def testShutdownDeserialized(self):
      m = message_from_xml("<message><sender>AliceID</sender><recipient>BobID</recipient><shuttingdown /><peers /><contents /></message>")
      self.assertTrue(m.shuttingDown)

  def testShutdownSerialized(self):
      self.m.shuttingDown = True
      self.assertIn(b"<shuttingdown />", self.m.to_xml())
