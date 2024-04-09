import signal
import sys
import Ice
import IceStorm

Ice.loadSlice('SOUP.ice')
import SOUP


class SOUPI(SOUP.LibraryUpdates):
    def libraryUpdated(self, action, data, current=None):
        print(f"Notification reçue: {action} - {data}")

def run(communicator):
    topicName = "ping"

    manager = IceStorm.TopicManagerPrx.checkedCast(communicator.propertyToProxy('TopicManager.Proxy'))
    if not manager:
        print("invalid proxy")
        sys.exit(1)

    #
    # Retrieve the topic.
    #
    try:
        topic = manager.retrieve(topicName)
    except IceStorm.NoSuchTopic as e:
        try:
            topic = manager.create(topicName)
        except IceStorm.TopicExists as ex:
            print(sys.argv[0] + ": temporary error. try again")
            sys.exit(1)

    adapter = communicator.createObjectAdapter("Clock.Subscriber")

    id = ""
    subId = Ice.Identity()
    subId.name = id

    if len(subId.name) == 0:
        subId.name = Ice.generateUUID()
    subscriber = adapter.add(SOUPI(), subId)

    #
    # Activate the object adapter before subscribing.
    #
    adapter.activate()

    qos = {}

    #
    # Set up the proxy.
    #
    subscriber = subscriber.ice_oneway()

    try:
        topic.subscribeAndGetPublisher(qos, subscriber)
    except IceStorm.AlreadySubscribed:
        # This should never occur when subscribing with an UUID
        assert(id)
        print("reactivating persistent subscriber")

    communicator.waitForShutdown()

    #
    # Unsubscribe all subscribed objects.
    #
    topic.unsubscribe(subscriber)


#
# Ice.initialize returns an initialized Ice communicator,
# the communicator is destroyed once it goes out of scope.
#
with Ice.initialize(sys.argv, "config.sub") as communicator:
    #
    # Install a signal handler to shutdown the communicator on Ctrl-C
    #
    signal.signal(signal.SIGINT, lambda signum, frame: communicator.shutdown())
    if hasattr(signal, 'SIGBREAK'):
        signal.signal(signal.SIGBREAK, lambda signum, frame: communicator.shutdown())
    status = run(communicator)