import socket
import pickle #TODO get rid of this once we have a proper XML scheme
import select
from threading import Timer

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
		self.unconfirmedList = []
		self.peerList = []
		self.autoPoll = autoPoll
		self.ip = ip
		self.port = port
		self.alerters = []
		self.box = []

		# Setup the server socket for incoming connections
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.bind((self.ip, self.port))
		self.server.listen(0)

		# Start the autoPolling if appropriate
		if self.autoPoll:
			Timer(1, self.autoAcceptor).start()
			Timer(1, self.autoReceiver).start()


	def alert(self, message):
		"""
		Alerts all known alerters with the given incoming message.
		"""

		for alerter in self.alerters:
			alerter(message)


	def sender(self, sendMessage):
		"""
		Sends message to all peers with a socket
		"""
		for peers in list(self.peerList):
			if peers.hasSock == True: # To me: don't you dare change this to if peers.hasSock: actually this one should work but still...
				peers.send(sendMessage)


	def connect(self, ip, port):
		"""
		Initializes a connection with a socket to a given ip and port, and then creates a
		new peer object, appends it to the peerList, and adds that socket to the new peer
		"""

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			sock.connect((ip, port))

		except socket.error:
			pass
			#self.alertOrStore("Alert: could not connect to peer: ({0}, {1!s}".format(ip,port))

		finally:
			newPeer = Peer(ip, port)
			self.peerList.append(newPeer)
			newPeer.addSock(sock)
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
			Timer(1, self.autoAcceptor).start()

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
		sockList=[]
		for peers in self.peerList:
			if peers.hasSock == True:
				sockList.append(peers.Sock)
		receiveOpen,writeOpen,errorSocks = select.select(sockList,[],[],2)#kind of bad,
			# but I don't currently need to check for writable/errors... if I need to I will later
			# timeout is in 2 seconds
		for sockets in receiveOpen:
			message = pickle.loads(sockets.recv(1024)) #DO NOT BELIEVE THIS IS USED IN THIS MANUAL VERSION
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

		# Queue the next autoReceiver
		if self.autoPoll:
			Timer(1, self.autoReceiver).start()

	def shutdown(self):
		""" Gracefully closes down all sockets for this peer. """

		self.autoPoll = False

		for peer in self.peerList:
			if peer.hasSock:
				peer.hasSock = False # Doing this before to try to prevent an error
				# peers.send() need to send something to initiate shutdown
				peer.Sock.shutdown(socket.SHUT_RDWR)
				peer.Sock.close()
