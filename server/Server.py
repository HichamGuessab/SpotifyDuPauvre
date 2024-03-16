import Ice
import sys

# Importation du module
Ice.loadSlice('SOUP.ice')
import SOUP
import vlc
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Environment variables
load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
DATABASE = os.getenv('DATABASE')
COLLECTION = os.getenv('COLLECTION')


class HelloI(SOUP.Hello):
    def helloWorld(self, current=None):
        print(f"Hello World!")


class SoupI(SOUP.SpotifyDuPauvre):
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DATABASE]
        self.collection = self.db[COLLECTION]

    def addMusic(self, filename, title, artist, album, genre, data, current):
        self.collection.insert_one(
            {
                "filename": filename,
                "metadata": {
                    "title": title,
                    "artist": artist,
                    "album": album,
                    "genre": genre
                },
                "data": data
            }
        )
        print("The song " + title + " from " + artist + " has been added.")


if __name__ == '__main__':
    properties = Ice.createProperties()
    properties.setProperty("Ice.MessageSizeMax", "102400")  # Set the maximum message size to 100 MB
    properties.setProperty("Ice.Override.ConnectTimeout", "5000")  # Set the connection timeout to 5 seconds

    initialization_data = Ice.InitializationData()
    initialization_data.properties = properties

    with Ice.initialize(sys.argv, initialization_data) as communicator:
        # Création d'un objet de type "ObjectAdapter" avec pour nom "HelloAdapter" et pour endpoint "default -h localhost -p 10000"
        adapter = communicator.createObjectAdapterWithEndpoints("SOUP", "default -h localhost -p 10000")

        soup = SoupI()
        hello = HelloI()

        # Ajout de l'objet "soup" à l'adapter
        adapter.add(soup, communicator.stringToIdentity("soup"))
        adapter.add(hello, communicator.stringToIdentity("hello"))
        adapter.activate()
        print("Server is ready to accept requests.")

        communicator.waitForShutdown()