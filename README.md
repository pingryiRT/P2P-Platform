# Pingry P2P Platform
A python-based platform for creating P2P networks. This code does not do anything useful on its own but serves as a backend for developing P2P applications.

## Examples
To create a new Network on your localhost, port 4444, that uses autoPolling

```
myNetwork = Network("localhost", 4444, autoPolling=True)
```

## Tests
This project intends to include good unittest coverage. At the moment, the tests are sparse and some classes are covered better than others. To run tests:
```
python -m unittest tests.networkTests
python -m unittest tests.messageTests
python -m unittest tests.peerTests
```


## API Reference

### Network Class

#### Attributes
* peerList -- a list of all the current Peer objects, which are used to send and receive messages
* autoPoll -- Whether the Network should run regular checks for incoming messages or connections
* ip -- This hosts own IP address as seen by peers on the network
* port -- The port on which this host is running a server
* server -- the server socket object of the network (for other nodes to connect to)
* unconfirmedList -- a list of peers that have not been approved and are not yet used to send and receive messages
* alerters -- List of methods to call upon message receipt. Used for notifying an application. Generally the alerter should be short-running
* box -- used to queue messages as they come in

#### Methods


### Peer Class

TODO

### Message Class

TODO

## Todo list
1. Allow encryption and authentication among connected nodes.
2. Establish a way for the network to provide informational status updates to an application.

## Authors
Mitchell Pavlak and Josh Orndorff
