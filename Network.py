import socket
import pickle
import select


from Peer import Peer

class Network(object):
	""" A connection to a P2P network.
	
	A single instance of this class is sufficient for typical usage, although 
	multiple instances may be useful if you want to connect to multiple networks
	and keep them separate in the future, or simultaneously connect as multiple identities.
	"""
	
	def __init__(self, ip, port, alerter):
		"""
		peerList -- a list of all the current Peer objects, which are used to send and receive 
		messages
		Stopper -- used to stop everything
		printStopper -- used as a poor-man's lock object to control printing output 
		ip -- This hosts own IP address as seen by peers on the network
		port -- The port on which this host is running a server
		server -- the server socket object of the network (for other nodes to connect to)
		A name object can be added to peers as a means of providing a unique id
		unconfirmedList -- contains peers that have not been manually accepted by the user
		and are not yet used to send and receive messages
		alerter -- method from interface that is called to transfer messages to the interface
		class
		box -- used to store messages when alerter is none
		"""
		
		self.unconfirmedList = []
		self.peerList = []
		self.printStopper = False
		self.ip = ip
		self.port = port
		self.alerter = alerter
		self.box = []
		
		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serverSocket.bind((self.ip, self.port))
		serverSocket.listen(0)
		self.server = serverSocket
	
	
	def alertOrStore(self,message, peer = None):
		""" Would be easier if we had a full xml setup, but currently just going to pass
		it as message and peers, when we get the xml finished I'll update it.
		
		alertOrStore is a wrapper that either sends the message to an interface, or if an
		interface is not available stores the message contents in box
		"""
		if self.alerter is None:
			if peer is None:
				box.append(message)
			else:
				box.append((message,peer))
		self.alerter(message,peer)
	
	
	def sender(self, sendMessage):
		"""
		Sends message to all peers with a socket
		"""
		for peers in list(self.peerList):
			if peers.hasSock == True: # To me: don't you dare change this to if peers.hasSock: actually this one should work but still...
				peers.send(sendMessage)

	
	def connect(self, ip, port):
		""" Initializes a connection with a socket to a given ip and port, and then creates a 
		new peer object, appends it to the peerList, and adds that socket to the new peer """
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			sock.connect((ip, port))
			
		except socket.error:
			self.alertOrStore("Alert: could not connect to peer: ({0}, {1!s}".format(ip,port))
		
		finally:
			newPeer = Peer(ip, port)
			self.peerList.append(newPeer)
			newPeer.addSock(sock)
			self.alertOrStore(str(newPeer) + " connected.")
			newPeer.send(self.port)
	
	
	def acceptor(self):
		"""
		Automatically accepts incoming peer conncections, but leaves them in the unconfirmedList
		where messages they attempt to send are not deserialized, and any messages sent by the 
		user will not be forwarded to them
		"""
		clientSocket, clientAddress = self.server.accept() 
		thisPeer = Peer(clientAddress[0],Socket = clientSocket)
		if thisPeer not in self.unconfirmedList:
			self.unconfirmedList.append(thisPeer)
		
		#print("Accepted connection from {}".format(clientAddress))
	
	def approve(self, peer):
		"""
		Moves a peer that has attempted to connect to this network instance from the 
		unconfirmedList to peerList, where messages can be sent and received
		"""
		
		self.unconfirmedList.remove(peer)
		self.peerList.append(peer)
	
	def receiver(self):
		""" Goes through all of the peers, and attempts to receive messages from all of the ones
		with a socket
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
				self.alertOrStore("received peerlist: " + str(messageStr),peer = peers)
			###########################################################
			
			else:
				for peers in list(self.peerList):
					if peers.Sock == sockets:
						if str(message) == "/exit":
							peers.Sock = None
							peers.hasSock = None
							self.alertOrStore(str(peers) + " exited.")
						else:
							self.alertOrStore(str(message),peer = peers)
				
	def shutdown(self):
		""" Gracefully closes down all sockets for this peer"""
		for peer in self.peerList:
			if peer.hasSock:
				peer.hasSock = False # Doing this before to try to prevent an error
				# peers.send() need to send something to initiate shutdown
				peer.Sock.shutdown(socket.SHUT_RDWR)
				peer.Sock.close()

