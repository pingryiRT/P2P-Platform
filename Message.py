from xml.etree import ElementTree as ET

class Message:
    """
    A message ton be sent on the network.
    """

    def __init__(self, sender):
        """
        Every Message must have a sender but recipient is optional. Typically a
        message will be sent to everyone given the P2P nature of Network, but it
        is good to at least indicate who the intended recipient is.

        For now sender is just an arbitrary string that the sender should choose
        to be fairly unique among his peers. It should eventually evolve into a
        private key, or perhaps a Peer object that encapsulates said key.

        Recipient should be a Peer object.
        """

        self.sender = sender
        self.recipient = None
        self.peers = []    # No peers given by default.
        self.contents = ""  # No contents by default.

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
        sendElem.text = self.sender

        # Recipient
        recipElem = root.subElement('recipient')
        recipElem.text = self.recipient.id

        # Peer list
        peersElem = root.subElement('peers')
        for peer in self.peers:
            currentPeerElem = peersElem.subElement('peer')
            currentPeerElem.text = repr(peer)


        # contents
        #TODO Consider appending a given element (rather than just a plain string)
        # Can be done according to https://stackoverflow.com/a/4789163/4184410
        contentElem = root.subelement('contents')
        contentElem.text = self.contents

        return ET.dump(root)

def message_from_xml(xml):
    """
    Builds a message object from the supplied XML. The XML string likely came
    from a another Peer on the network.
    """

    root = ET.fromstring(xml)

    m = Message(root.)

    #TODO finish writing this
