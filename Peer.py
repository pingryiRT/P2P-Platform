import socket
import pickle

class Peer(object):
	"""
	The Peer object, represents a peer on the network, and has fields:

	id -- A unique identifier supplied in the sender field of every message
	ip -- The IP address of the peer's server socket
	port -- The port on which the peer's server socket runs
	socket -- defaults to None, but can (and should) be added for the socket of the peer
	name -- initialized as None, but can be added to give a peer a human-readable name

	Peers are identified by their id and in future versions that ID will be a public key.
	For purposes of connecting to new peers who are known only by server port and ip,
	id is initialized to None. A Peer's id should generally not change except from None.
	"""

	def __init__(self, id = None, ip = None, port = None):
		self.id = id
		self.ip = ip
		self.port = port
		self.socket = None
		self.name = None


	def __repr__(self):
		"""
		Returns a string that evaluates to this Peer.
		"""

		text = "Peer('{}', '{}', {})".format(self.id, self.ip, self.port)
		return text


	def __str__(self):
		""" Attempts to return a relatively human-readable representation of the
		peer the user-provided name. If the peer is unnamed by the user,
		returns the representation given by __repr__
		"""
		if self.name is not None:
			return self.name
		else:
			return repr(self)


	def __eq__(self, other):
		"""
		Compares this Peer to another for equality. (for == operator)

		Other can be either the other peer object or the string representation
		of that peer object.
		#TODO Do we use this repr comparison anywhere?
		# See https://github.com/pingryiRT/P2PPlatform/issues/9

		Comparison happens first by id, but if no id is provided, falls back to
		server port and ip.
		"""

		if isinstance(other, Peer):

			if self.id is not None and other.id is not None:
				return self.id == other.id

			# If either peer doesn't have an ID, fall back to port and ip
			return self.ip == other.ip and self.port == other.port

		# repr support
		else:
			return repr(self) == other


	def __neq__(self, other):
	  """ Compares the peer to another peer for inequality. (for != operator) """
	  return not self == other


	def send(self, message):
		"""
		Send (including forwards) the given message this Peer.
		"""

		if self.socket is None:
			raise Exception("Cannot send to peer without socket.")

		self.socket.send(message.to_xml())


	def receive(self):
		"""
		Receive a message from this peer and return it.
		"""

		#TODO Should this return a Message object?

		if self.socket is None:
			raise Exception("Cannot receive from peer without socket")

		try:
			message = self.socket.recv(1024)
		except socket.error:
			raise Exception("error receiving message from " + str((self.IP,self.port)))

		return message
