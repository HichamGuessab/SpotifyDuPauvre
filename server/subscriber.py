import time
import Ice
import sys

Ice.loadSlice('SOUP.ice')
import SOUP

class LibraryUpdatesI(SOUP.LibraryUpdates):
    def libraryUpdated(self, action, data, current=None):
        print(f"Notification reçue: {action} - {data}")

class NotificationsHandler:
    def __init__(self, communicator, service):
        self.communicator = communicator
        self.service = service

        updates = LibraryUpdatesI()
        self.subscriber = self.communicator.stringToIdentity("LibraryUpdates")
        self.adapter = self.communicator.createObjectAdapterWithEndpoints("LibraryUpdatesAdapter", "default -h localhost -p 10001")
        self.adapter.add(updates, self.subscriber)
        self.adapter.activate()
        self.service.subscribeUpdates(SOUP.LibraryUpdatesPrx.uncheckedCast(self.adapter.createProxy(self.subscriber)))

    def unSubscribe(self):
        self.service.unsubscribeUpdates(SOUP.LibraryUpdatesPrx.uncheckedCast(self.adapter.createProxy(self.subscriber)))

def main():
    with Ice.initialize(sys.argv) as communicator:
        base = communicator.stringToProxy("soup:default -p 10000")
        server = SOUP.SpotifyDuPauvrePrx.checkedCast(base)

        if not server:
            raise RuntimeError("Invalid proxy")

        notifications_handler = NotificationsHandler(communicator, server)

        print("NotificationsHandler is running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            notifications_handler.unSubscribe()
            print("Exiting...")


if __name__ == "__main__":
    main()