import socket
import select
from threading import Thread, Timer
from random import randint

from Peer import Peer

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
		self.id = hash(randint(0,100000)) #TODO Use keys for this!

		# Keep track of other network users
		self.unconfirmedList = []
		self.peerList = []

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
					peer.send(message)
				except:
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
		connectTo(newPeer)

		# Give the caller a reference to the Peer we just created
		return newPeer


	def connectTo(self, peer):
		"""
		Initializes a socket connection to a Peer object.
		"""

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			sock.connect((ip, port)) ### Is this a blocking call?
		except socket.error:
			alert("Failed to connect to {}".format(peer))

		finally:
			self.peerList.append(newPeer)
			newPeer.socket = sock
			#self.alertOrStore(str(newPeer) + " connected.")
			newPeer.send(self.port)


	def autoAcceptor(self):
		"""
		Automatically accepts incoming peer conncections, but leaves them in the unconfirmedList
		where messages they attempt to send are not deserialized, and any messages sent by the
		user will not be forwarded to them
		"""

		clientSocket, clientAddress = self.server.accept()
		thisPeer = Peer(clientAddress[0],Socket = clientSocket)
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
		sockList = [p.socket for p in self.peerList]
		receiveOpen,writeOpen,errorSocks = select.select(sockList,[],[],2)#kind of bad,
			# but I don't currently need to check for writable/errors... if I need to I will later
			# timeout is in 2 seconds

		#TODO should we be moving peers with socket errors discovered here to the acquaintances list?

		for sockets in receiveOpen:
			rawXML = sockets.recv(4096) #DO NOT BELIEVE THIS IS USED IN THIS MANUAL VERSION
			m = message_from_xml(rawXML)

			#TODO If sender is shutting down, disconnect, say goodbye, etc

			#TODO If sender is requesting Peers, send some

			# If we want more peers, connect to some
			#TODO ATM we're connecting to every peer we know of. That will make a lot of connections.
			for peer in m.peers:
				if peer not in peerList and peer not in unconfirmedList:
					#TODO Add these peers to one of the lists
					pass

			# Alert the application to the new message
			alert(message)


			'''
			if type(message) is list:
				messageStr = []
				for peers in message:
					messageStr.append(str(peers))
				#self.alertOrStore("received peerlist: " + str(messageStr),peer = peers)
			###########################################################

			else:
				for peers in list(self.peerList):
					if peers.Sock == sockets:
						if str(message) == "/exit":
							peers.Sock = None
							peers.hasSock = None
							#self.alertOrStore(str(peers) + " exited.")
						else:
							self.alert(message)
							self.box.append(message)
			'''

		# Queue the next autoReceiver
		if self.autoPoll:
			self.receiverThread = Timer(1, self.autoReceiver)
			self.receiverThread.start()

	def shutdown(self):
		""" Gracefully closes down all sockets for this peer. """

		#TODO Inform peers that we're shutting down

		# Cancel all current and future autoPoll operations
		self.autoPoll = False
		if self.acceptorThread is not None:
				self.acceptorThread.cancel()
		if self.receiverThread is not None:
				self.receiverThread.cancel()

		# Colse our own server socket
		self.server.close()

		# Close all peer sockets
		for peer in self.peerList:
			if peer.hasSock:
				peer.hasSock = False # Doing this before to try to prevent an error
				# peers.send() need to send something to initiate shutdown
				peer.Sock.shutdown(socket.SHUT_RDWR)
				peer.Sock.close()
