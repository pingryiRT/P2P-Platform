# Pingry P2P Platform
A python-based platform for creating P2P networks. This code does not do anything useful on its own but serves as a backend for developing P2P applications.

## Examples
To create a new Network on your localhost, port 4444, that uses autoPolling

```
myNetwork = Network("localhost", 4444, autoPolling=True)
```

## API Reference
###The Network class

#### Attributes
peerList -- a list of all the current Peer objects, which are used to send and receive
messages
autoPoll -- Whether the Network should run regular checks for incoming messages or connections
ip -- This hosts own IP address as seen by peers on the network
port -- The port on which this host is running a server
server -- the server socket object of the network (for other nodes to connect to)
unconfirmedList -- a list of peers that have not been approved and are not yet used to send and receive messages
alerters -- List of methods to call upon message receipt. Used for notifying an application
box -- used to queue messages as they come in

#### Methods

### The Peer class

TODO

## Goals

Here are some goals for the project

1. Get chat client to run with this backend
2. Implement a queue for messages
3. Develop a standard XML (or otherwise) message passing scheme.
   1. Perhaps a message class?
4. Allow encryption and authentication among connected nodes.
