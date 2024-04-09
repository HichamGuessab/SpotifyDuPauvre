from time import sleep

import Ice
import IceStorm
import sys

Ice.loadSlice('SOUP.ice')
import SOUP
import vlc
import os
import re
from pymongo import MongoClient
from dotenv import load_dotenv

# Environment variables
load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
DATABASE = os.getenv('DATABASE')
COLLECTION = os.getenv('COLLECTION')

global MONPOTE
MONPOTE = None

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
        self.streaming_port = StreamingPortManager.allocate_streaming_port()
        self.streaming_url = f"http://localhost:{self.streaming_port}/stream"
        self.subscribers = set()
        self.libraryUpdate = None

    def __del__(self):
        StreamingPortManager.release_streaming_port(self.streaming_port)

    def researchMusicByTitle(self, title, current):
        global MONPOTE
        regex = re.compile(title, re.IGNORECASE)
        metadata = [
            {
                "title": song["metadata"]["title"],
                "artist": song["metadata"]["artist"],
                "album": song["metadata"]["album"],
                "genre": song["metadata"]["genre"]
            }
            for song in self.collection.find(
                {"metadata.title": {"$regex": regex}}
            ) if "metadata" in song
                 and "title" in song["metadata"]
                 and "artist" in song["metadata"]
                 and "album" in song["metadata"]
                 and "genre" in song["metadata"]
        ]
        print("C MON POTE", MONPOTE)
        MONPOTE.libraryUpdated('soup', 'The song has been found.')
        return [SOUP.MetaData(title=metadata["title"], artist=metadata["artist"]) for metadata in metadata]

    def researchMusicByArtist(self, artist, current):
        global MONPOTE
        regex = re.compile(artist, re.IGNORECASE)
        metadata = [
            {
                "title": song["metadata"]["title"],
                "artist": song["metadata"]["artist"],
                "album": song["metadata"]["album"],
                "genre": song["metadata"]["genre"]
            }
            for song in self.collection.find(
                {"metadata.artist": {"$regex": regex}}
            ) if "metadata" in song
                 and "title" in song["metadata"]
                 and "artist" in song["metadata"]
                 and "album" in song["metadata"]
                 and "genre" in song["metadata"]
        ]
        MONPOTE.libraryUpdated('soup', 'The song has been found.')
        return [SOUP.MetaData(title=metadata["title"], artist=metadata["artist"]) for metadata in metadata]

    def addMusic(self, title, artist, album, genre, data, current):
        if self.collection.find_one({"metadata.title": title, "metadata.artist": artist}):
            response = "The song " + title + " from " + artist + " already exists."
        else:
            self.collection.insert_one(
                {
                    "filename": artist + "_" + title,
                    "metadata": {
                        "title": title,
                        "artist": artist,
                        "album": album,
                        "genre": genre
                    },
                    "data": data
                }
            )
            response = "The song " + title + " from " + artist + " has been added."
        MONPOTE.libraryUpdated('soup', response)
        return response

    def deleteMusic(self, title, artist, current):
        if not self.collection.find_one({"metadata.title": title, "metadata.artist": artist}):
            response = "The song " + title + " from " + artist + " doesn't exists."
        else:
            self.collection.delete_one({"metadata.title": title, "metadata.artist": artist})
            response = "The song " + title + " from " + artist + " has been deleted."
        MONPOTE.libraryUpdated('soup', response)
        return response

    def editMusic(self, title, artist, newTitle, newAlbum, newGenre, current):
        song = self.collection.find_one({"metadata.title": title, "metadata.artist": artist})
        if not song:
            response = "The song " + title + " from " + artist + " does not exist."
        else:
            self.collection.update_one(
                {"metadata.title": title, "metadata.artist": artist},
                {
                    "$set": {
                        "filename": artist + "_" + newTitle,
                        "metadata.title": newTitle,
                        "metadata.album": newAlbum,
                        "metadata.genre": newGenre
                    }
                }
            )
            response = "The song " + title + " from " + artist + " has been updated : " + newTitle + " from album " + newAlbum + " in " + newGenre + " genre."
        MONPOTE.libraryUpdated('soup', response)
        return response

    def playMusic(self, title, artist, current):
        song = self.collection.find_one({"metadata.title": title, "metadata.artist": artist})
        if not song:
            return "The song does not exist."
        song_filename = song.get("filename")
        song_data = song.get("data")
        if not song_data:
            return "The song data does not exist."

        # Créer une nouvelle instance VLC pour chaque requête de client
        vlc_instance = vlc.Instance("--no-audio")
        # Allouer un nouveau port pour ce client spécifique
        streaming_port = StreamingPortManager.allocate_streaming_port()

        # Construire le chemin temporaire du fichier
        temp_filename = os.path.join("assets", f"{song_filename}.mp3")
        with open(temp_filename, "wb") as f:
            f.write(song_data)

        # Configurer le lecteur VLC pour diffuser sur le port alloué
        output = f'sout=#transcode{{vcodec=none,acodec=mp3,ab=128,channels=2,samplerate=44100}}:http{{mux=raw,dst=:{streaming_port}/stream.mp3}}'
        media = vlc_instance.media_new(temp_filename, output)
        self.player.set_media(media)
        self.player.play()

        streaming_url = f"http://localhost:{streaming_port}/stream"
        return f"The song {title} from {artist} is playing on {streaming_url}"

    def pauseMusic(self, current):
        self.player.pause()
        global MONPOTE
        MONPOTE.libraryUpdated('soup', 'The song has been paused.')
        return "The song has been paused."

    def resumeMusic(self, current):
        self.player.play()
        MONPOTE.libraryUpdated('soup', 'The song has been resumed.')
        return "The song has been resumed."

    def stopMusic(self, current):
        if self.player.is_playing():
            self.player.stop()
        StreamingPortManager.release_streaming_port(self.streaming_port)
        MONPOTE.libraryUpdated('soup', 'The song has been stopped.')
        return "The song has been stopped."


class StreamingPortManager:
    MIN_PORT = 9581
    MAX_PORT = 9600

    # Initialisation des ensembles de ports disponibles et alloués
    available_ports = set(range(MIN_PORT, MAX_PORT + 1))
    allocated_ports = set()

    @staticmethod
    def allocate_streaming_port():
        if not StreamingPortManager.available_ports:
            raise Exception("No available ports for streaming")

        # Sélectionne et retire un port de l'ensemble des ports disponibles
        port = StreamingPortManager.available_ports.pop()

        # Ajoute le port à l'ensemble des ports alloués
        StreamingPortManager.allocated_ports.add(port)

        return port

    @staticmethod
    def release_streaming_port(port):
        # Assurez-vous que le port était effectivement alloué
        if port in StreamingPortManager.allocated_ports:
            # Retire le port de l'ensemble des ports alloués
            StreamingPortManager.allocated_ports.remove(port)

            # Remet le port dans l'ensemble des ports disponibles
            StreamingPortManager.available_ports.add(port)
        else:
            raise Exception(f"Attempted to release a port ({port}) that was not allocated.")


if __name__ == '__main__':
    properties = Ice.createProperties()
    properties.setProperty("Ice.MessageSizeMax", "102400")  # Set the maximum message size to 100 MB
    properties.setProperty("Ice.Override.ConnectTimeout", "5000")  # Set the connection timeout to 5 seconds

    initialization_data = Ice.InitializationData()
    initialization_data.properties = properties

    with Ice.initialize(sys.argv, initialization_data) as communicator:
        topicName = "ping"

        with Ice.initialize(sys.argv, "config.pub") as communicator2:
            manager = IceStorm.TopicManagerPrx.checkedCast(communicator2.propertyToProxy('TopicManager.Proxy'))
            if not manager:
                print("invalid proxy")
                sys.exit(1)

            try:
                topic = manager.retrieve(topicName)
            except IceStorm.NoSuchTopic:
                try:
                    topic = manager.create(topicName)
                except IceStorm.TopicExists:
                    print("mes couilles au bord de l'eau")
                    sys.exit(1)

            publisher = topic.getPublisher()
            MONPOTE = SOUP.LibraryUpdatesPrx.uncheckedCast(publisher)

            MONPOTE.libraryUpdated('soup', 'Library has been updateeeeed.')

        # Création d'un objet de type "ObjectAdapter" avec pour nom "HelloAdapter" et pour endpoint "default -h localhost -p 10000"
        adapter = communicator.createObjectAdapterWithEndpoints("SOUP", "default -h localhost -p 10010")

        hello = HelloI()
        soup = SoupI()

        # Ajout de l'objet "soup" à l'adapter
        adapter.add(hello, communicator.stringToIdentity("hello"))
        adapter.add(soup, communicator.stringToIdentity("soup"))

        adapter.activate()
        print("Server is ready to accept requests.")

        # with Ice.initialize(sys.argv, "config.sub") as ice_storm_communicator:
        #     # IceStorm
        #     topicName = "LibraryUpdates"
        #     manager = IceStorm.TopicManagerPrx.checkedCast(ice_storm_communicator.propertyToProxy('TopicManager.Proxy'))
        #     if not manager:
        #         print("invalid proxy")
        #         sys.exit(1)
        #
        #     try:
        #         topic = manager.retrieve(topicName)
        #     except IceStorm.NoSuchTopic as e:
        #         try:
        #             topic = manager.create(topicName)
        #         except IceStorm.TopicExists as ex:
        #             print(sys.argv[0] + ": temporary error. try again")
        #             sys.exit(1)
        #
        #     adapter = ice_storm_communicator.createObjectAdapter("Clock.Subscriber")
        #
        #     subId = Ice.Identity()
        #     subId.name = ""
        #     if len(subId.name) == 0:
        #         subId.name = Ice.generateUUID()
        #     subscriber = adapter.add(SoupI(), subId)
        #
        #     adapter.activate()
        #     qos = {}
        #     subscriber = subscriber.ice_oneway()
        #
        #     try:
        #         topic.subscribeAndGetPublisher(qos, subscriber)
        #     except IceStorm.AlreadySubscribed:
        #         # This should never occur when subscribing with an UUID
        #         assert(id)
        #         print("reactivating persistent subscriber")
        #
        #     ice_storm_communicator.waitForShutdown()
        #soup.libraryUpdate = SOUP.LibraryUpdatesPrx.uncheckedCast(publisher)

        communicator.waitForShutdown()
