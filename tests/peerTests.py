from unittest import TestCase
from unittest.mock import create_autospec

from Peer import Peer
from Message import Message
from socket import socket

class peerTests(TestCase):

    def setUp(self):
        self.p = Peer('1', '10.10.10.10', 7676)
        self.mess = create_autospec(Message)
        self.sock = create_autospec(socket)

    # Tests for __init__
    def test_no_initial_socket(self):
        self.assertIsNone(self.p.socket)

    def test_no_initial_name(self):
        self.assertIsNone(self.p.name)

    # Tests for __repr__
    def test_normal_repr(self):
        self.assertEqual(repr(self.p), "Peer('1', '10.10.10.10', 7676)")

    # Tests for __eq__ (Not doing tests for __neq__)
    def test_peers_equal_same_ids(self):
        q = Peer('1', 'bogus IP', 0)
        self.assertEqual(self.p, q)

    def test_peers_unequal_different_ids(self):
        q = Peer('10', '10.10.10.10', 7676)
        self.assertNotEqual(self.p, q)

    def test_peers_equal_no_ids(self):
        q = Peer(None, '10.10.10.10', 7676)
        self.p.id = None
        self.assertEqual(self.p, q)

    def test_peers_unequal_no_ids(self):
        q = Peer(None, '10.10.10.9', 7676)
        self.p.id = None
        self.assertNotEqual(self.p, q)

    def test_peers_unequal_no_ids2(self):
        q = Peer(None, '10.10.10.10', 7677)
        self.p.id = None
        self.assertNotEqual(self.p, q)

    def test_peers_equal_one_id(self):
        q = Peer(None, '10.10.10.10', 7676)
        self.assertEqual(self.p, q)

    def test_peers_unequal_one_id(self):
        q = Peer(None, '10.10.10.9', 7676)
        self.assertNotEqual(self.p, q)

    # Tests for send
    def test_send_without_socket(self):
        with self.assertRaises(Exception):
            self.p.send(self.mess)

    def test_send_with_socket(self):
        self.p.socket = self.sock
        self.p.send(self.mess)
        #TODO Everyone says one assert per test. What should I do differently here.
        self.mess.toXML.assert_called_once_with()
        self.sock.send.assert_called_once_with(self.mess.toXML())

    # Tests for receive
    def test_receive_without_socket(self):
        with self.assertRaises(Exception):
            self.p.receive()

    def test_receive_with_socket(self):
        self.p.socket = self.sock
        self.p.receive()
        self.sock.recv.assert_called_once_with(1024)
