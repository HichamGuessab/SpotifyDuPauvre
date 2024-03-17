import Ice
import sys

# Importation du module
Ice.loadSlice('SOUP.ice')
import SOUP
import vlc
import os
import time
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
        self.vlc_instance = vlc.Instance("--no-audio")
        self.player = self.vlc_instance.media_player_new()
        self.streaming_url = "http://localhost:8080/stream"

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

    def playMusic(self, title, artist, current):
        song_data = self.collection.find_one({"metadata.title": title, "metadata.artist": artist}).get("data")
        if not song_data:
            return ""

        temp_filename = os.path.join("assets", f"{title}.mp3")
        with open(temp_filename, "wb") as f:
            f.write(song_data)

        output = 'sout=#transcode{vcodec=none,acodec=mp3,ab=128,channels=2,samplerate=44100}:http{mux=raw,dst=:8080/stream.mp3}'
        media = self.vlc_instance.media_new(temp_filename, output)

        self.player.set_media(media)
        self.player.play()

        return self.streaming_url


if __name__ == '__main__':
    properties = Ice.createProperties()
    properties.setProperty("Ice.MessageSizeMax", "102400")  # Set the maximum message size to 100 MB
    properties.setProperty("Ice.Override.ConnectTimeout", "5000")  # Set the connection timeout to 5 seconds

    initialization_data = Ice.InitializationData()
    initialization_data.properties = properties

    with Ice.initialize(sys.argv, initialization_data) as communicator:
        # Création d'un objet de type "ObjectAdapter" avec pour nom "HelloAdapter" et pour endpoint "default -h localhost -p 10000"
        adapter = communicator.createObjectAdapterWithEndpoints("SOUP", "default -h localhost -p 10000")

        hello = HelloI()
        soup = SoupI()

        # Ajout de l'objet "soup" à l'adapter
        adapter.add(hello, communicator.stringToIdentity("hello"))
        adapter.add(soup, communicator.stringToIdentity("soup"))

        adapter.activate()
        print("Server is ready to accept requests.")

        communicator.waitForShutdown()