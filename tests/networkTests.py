from unittest import TestCase
from Network import Network #TODO don't know how to do this in python2

class BasicNetworkTest(TestCase):

  def test_starts(self):
    """ Simple test to make sure I can build a Network without errors. """

    #TODO fix this Hack to choose a random port number.
    from random import randint

    port =randint(2000, 6000)
    myNet = Network("localhost", port, False)
    myNet.shutdown()

    # Not sure what to assert yet.
    self.assertTrue(True)
