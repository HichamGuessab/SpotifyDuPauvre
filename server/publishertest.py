#!/usr/bin/env python
#
# Copyright (c) ZeroC, Inc. All rights reserved.
#

import signal
import sys
import time
import Ice
import IceStorm
import getopt

Ice.loadSlice('SOUP.ice')
import SOUP

def usage():
    print("Usage: " + sys.argv[0] + " [--datagram|--twoway|--oneway] [topic]")

def run(communicator):
    topicName = "LibraryUpdates"

    manager = IceStorm.TopicManagerPrx.checkedCast(communicator.propertyToProxy('TopicManager.Proxy'))
    if not manager:
        print("invalid proxy")
        sys.exit(1)

    try:
        topic = manager.retrieve(topicName)
    except IceStorm.NoSuchTopic:
        try:
            topic = manager.create(topicName)
        except IceStorm.TopicExists:
            print(sys.argv[0] + ": temporary error. try again")
            sys.exit(1)

    publisher = topic.getPublisher()
    publisher = publisher.ice_oneway()
    clock = SOUP.HelloPrx.uncheckedCast(publisher)
    print("publishing tick events. Press ^C to terminate the application.")
    try:
        while 1:
            clock.helloWorld()
            time.sleep(1)
    except IOError:
        # Ignore
        pass
    except Ice.CommunicatorDestroyedException:
        # Ignore
        pass


with Ice.initialize(sys.argv, "config.pub") as communicator:
    signal.signal(signal.SIGINT, lambda signum, frame: communicator.destroy())
    if hasattr(signal, 'SIGBREAK'):
        signal.signal(signal.SIGBREAK, lambda signum, frame: communicator.destroy())
    status = run(communicator)