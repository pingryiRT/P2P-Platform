import socket
import select
from threading import Thread, Timer
from random import randint

from .Peer import Peer
from .Message import Message, message_from_xml

class Network(object):
	"""
	A connection to a P2P network.

	A single instance of this class is sufficient for typical usage, although
	multiple instances may be useful if you want to connect to multiple networks
	and keep them separate in the future, or simultaneously connect as multiple identities.
	"""

	def __init__(self, ip, port, autoPoll = True):

		# Initialize attributes
		self.autoPoll = autoPoll
		self.ip = ip
		self.port = port
		self.id = str(hash(randint(0,100000))) #TODO Use keys for this!

		# Keep track of other network users
		self.unconfirmedList = []
		self.peerList = []
		self.acquaintances = []

		# Create infastructure for handling incoming messages
		self.alerters = []
		self.box = []

		# Setup the server socket for incoming connections
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.bind((self.ip, self.port))
		self.server.listen(2) # 2 simultaneous connections in backlog

		# Start the autoPolling if appropriate
		if self.autoPoll:
			self.acceptorThread = Timer(1, self.autoAcceptor)
			self.receiverThread = Thread(target = self.autoReceiver)
			self.acceptorThread.start()
			self.receiverThread.start()
		else:
			self.acceptorThread = None
			self.receiverThread = None



	def alert(self, news):
		"""
		Alerts all known alerters (single-argument callables) of something
		happening in the underlying Network.

		The argument will either be a Message object received from a Peer on the
		Network, or a string motifying the alerter of a Network status update.

		(In the future we may want better structure to the status alerts. #TODO)
		"""

		for alerter in self.alerters:
			# Start each alerter on its own thread in case a thread is long-running
			Thread(target = alerter, args = (news,)).start()



	def sender(self, contents, recipient = None):
		"""
		Constructs a message with the given contents (and recipient if specified)
		and broadcasts it to all peers with a socket.

		If recipient is specified, it should be a Peer object. If it is None,
		the message is considered a public broadcast.
		"""

		me = Peer(self.id, self.ip, self.port)
		m = Message(me)
		m.contents = contents
		m.recipient = recipient

		for peer in list(self.peerList): # Makes a copy
			if peer.socket is not None:
				try:
					peer.send(m)
				except socket.error as e:
					print("Error message is {}".format(e))
					peer.socket = None
					self.peerList.remove(peer)
					self.acquaintances.append(peer)


	def connect(self, ip, port):
		"""
		Initializes a socket connection to a server known only by ip and port.
		Primarily useful for connecting to the first known Peer.
		"""

		newPeer = Peer(None, ip, port)

		#TODO Check whether we're already connected to this Peer

		#TODO Check whether this peer is already trying to connect to us

		# Make the actual connection
		self.connectTo(newPeer)

		# Give the caller a reference to the Peer we just created
		return newPeer


	def connectTo(self, peer):
		"""
		Initializes a socket connection to a Peer object.
		"""

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			sock.connect((peer.ip, peer.port)) #TODO Is this a blocking call?
		except socket.error:
			pass
			#self.alertOrStore("Alert: could not connect to peer: ({0}, {1!s}".format(ip,port))

		finally:
			self.peerList.append(peer)
			peer.socket = sock
			#self.alertOrStore(str(newPeer) + " connected.")
			#newPeer.send(self.port)


	def autoAcceptor(self):
		"""
		Automatically accepts incoming peer conncections, but leaves them in the unconfirmedList
		where messages they attempt to send are not received, boxed, or passed along to applications,
		and any outgoing messages will not be sent to them.
		"""

		clientSocket, (clientIP, clientPort) = self.server.accept()
		thisPeer = Peer(clientIP, clientPort)
		thisPeer.socket = clientSocket

		if thisPeer not in self.unconfirmedList:
			self.unconfirmedList.append(thisPeer)

		# Queue the next autoAcceptor
		if self.autoPoll:
			self.acceptorThread = Thread(target = self.autoAcceptor)
			self.acceptorThread.start()

	def approve(self, peer):
		"""
		Moves a peer that has attempted to connect to this network from the
		unconfirmedList to peerList, where messages can be sent and received
		"""

		self.unconfirmedList.remove(peer)
		self.peerList.append(peer)

	def autoReceiver(self):
		"""
		Goes through all peers, attempting to receive messages when sockets exist.
		"""

		# Figure out who we're receiving from
		sockList=[]
		for peer in self.peerList:
			if peer.socket is not None:
				sockList.append(peer.socket)

		# Do the actual receiving
		receiveOpen,writeOpen,errorSocks = select.select(sockList,[],[],2)#kind of bad,
			# but I don't currently need to check for writable/errors... if I need to I will later
			# timeout is in 2 seconds

		#TODO should we be moving peers with socket errors discovered here to the acquaintances list?

		for sockets in receiveOpen:
			rawXML = sockets.recv(4096) #DO NOT BELIEVE THIS IS USED IN THIS MANUAL VERSION
			m = message_from_xml(rawXML)
			if m.contents == "/exit":
				for peer in self.peerList:
					if peer.socket == sockets:
						peer.socket = None
						self.peerList.remove(peer)
						self.acquaintances.append(peer)
			#TODO If sender is shutting down, disconnect, say goodbye, etc

			#TODO If sender is requesting Peers, send some

			# If we want more peers, connect to some
			#TODO ATM we're connecting to every peer we know of. That will make a lot of connections.
			for peer in m.peers:
				if peer not in peerList and peer not in unconfirmedList:
					self.acquaintances.append(peer)
			
				
			# Alert the application to the new message
			self.alert(m)

		# Queue the next autoReceiver
		if self.autoPoll:
			self.receiverThread = Timer(1, self.autoReceiver)
			self.receiverThread.start()

	def shutdown(self):
		""" Gracefully closes down all sockets for this peer. """

		#TODO Inform peers that we're shutting down

		# Cancel all current and future autoPoll operations
		self.autoPoll = False
		if self.receiverThread is not None:
				self.receiverThread.cancel()

		# Colse our own server socket
		self.server.close()

		# Close all peer sockets
		for peer in self.peerList:
			if peer.socket is not None:
				peer.socket.shutdown(socket.SHUT_RDWR)
				peer.socket.close()
