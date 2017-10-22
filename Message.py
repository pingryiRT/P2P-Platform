from xml.etree import ElementTree as ET
from P2PPlatform.Peer import Peer

class Message:
    """
    A message ton be sent on the network.
    """

    def __init__(self, sender = None):
        """
        Every Message must have a sender but recipient is optional. Typically a
        message will be sent to everyone given the P2P nature of Network, but it
        is good to at least indicate who the intended recipient is.

        Sender and Recipient should be Peer objects.
        """

        self.sender = sender
        self.recipient = None
        self.shuttingDown = False
        self.requestPeers = False
        self.peers = set()
        self.contents = ""


    def __eq__(self, other):
        return self.sender       == other.sender and \
               self.recipient    == other.recipient and \
               self.shuttingDown == other.shuttingDown and \
               self.requestPeers == other.requestPeers and \
               self.peers        == other.peers and \
               self.contents     == other.contents

    def to_xml(self):
        """
        Generate an XML representation of the Message.

        Returns a plain string representation of the XML.
        (Could be easily modified to return an ETree.Element if useful.)
        """

        # Generate a The root element for the message
        root = ET.Element('message')

        # Sender
        sendElem = ET.SubElement(root, 'sender')
        if self.sender is not None:
            sendElem.text = self.sender.id
            #TODO Include return address info (eg. server ip and port)

        # Recipient
        recipElem = ET.SubElement(root, 'recipient')
        if self.recipient is not None:
            recipElem.text = self.recipient.id

        # Peer list
        peersElem = ET.SubElement(root, 'peers')
        for peer in self.peers:
            currentPeerElem = ET.SubElement(peersElem, 'peer')
            currentPeerElem.text = repr(peer)

        # Contents
        #TODO Consider appending a given element (rather than just a plain string)
        # Can be done according to https://stackoverflow.com/a/4789163/4184410
        contentElem = ET.SubElement(root, 'contents')
        contentElem.text = self.contents

        return ET.tostring(root)



def message_from_xml(xml):
    """
    Builds a Message object from the supplied XML. The XML string likely came
    from a another Peer on the network.
    """

    #TODO Sanitize the XML string before constructing the Message

    # Create the ETree and the Message
    root = ET.fromstring(xml)
    m = Message()

    # Parse the sender (a Peer object)
    sendElem = root.find('sender')
    senderID = sendElem.text
    senderIP = sendElem.get('ip')
    senderPort = sendElem.get('port')
    m.sender = Peer(senderID, senderIP, senderPort)

    #TODO Validate signature once public key stuff is implemented

    # Parse the recipient (a Peer object)
    recipElem = root.find('recipient')
    recipientID = recipElem.text
    m.recipient = Peer(recipientID)

    # Shutting down or requesting peers?
    m.shuttingdown = root.find('shuttingdown') is not None
    m.requestPeers = root.find('requestpeers') is not None

    # Parse the attached list of peers
    peersElem = root.find('peers')
    for peerElem in peersElem.findall('peer'):
        #TODO This is very bad and unsafe code. The Peer string needs to be sanitized first.
        # This might be a starting place: http://lybniz2.sourceforge.net/safeeval.html
        newPeer = eval(peerElem.text)
        self.peers.add(newPeer)

    # Fetch the primary contents
    m.contents = root.find('contents').text
    if m.contents is None:
      m.contents = ""

    return m
