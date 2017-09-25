from xml.etree import ElementTree as ET

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



    def toXML(self):
        """
        Generate an XML representation of the Message.

        Returns a plain string representation of the XML.
        (Could be easily modified to return an ETree.Element if useful.)
        """

        # Generate a The root element for the message
        root = ET.Element('Message')

        # Sender
        sendElem = root.subElement('sender')
        sendElem.text = self.sender.id

        # Recipient
        recipElem = root.subElement('recipient')
        recipElem.text = self.recipient.id

        # Peer list
        peersElem = root.subElement('peers')
        for peer in self.peers:
            currentPeerElem = peersElem.subElement('peer')
            currentPeerElem.text = repr(peer)

        # Contents
        #TODO Consider appending a given element (rather than just a plain string)
        # Can be done according to https://stackoverflow.com/a/4789163/4184410
        contentElem = root.subelement('contents')
        contentElem.text = self.contents

        return ET.dump(root)



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
    for peerElem in root.peersElem.findall('peer'):
        #TODO This is very bad and unsafe code. The Peer string needs to be sanitized first.
        # This might be a starting place: http://lybniz2.sourceforge.net/safeeval.html
        newPeer = eval(peerElem.text)
        self.peers.add(newPeer)

    # Fetch the primary contents
    m.contents = root.find('contents').text

    return m
