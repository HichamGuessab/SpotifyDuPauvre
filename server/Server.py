import Ice
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

    def researchMusicByTitle(self, title, current):
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
        return response

    def deleteMusic(self, title, artist, current):
        if not self.collection.find_one({"metadata.title": title, "metadata.artist": artist}):
            response = "The song " + title + " from " + artist + " doesn't exists."
        else:
            self.collection.delete_one({"metadata.title": title, "metadata.artist": artist})
            response = "The song " + title + " from " + artist + " has been deleted."
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
        return response

    def playMusic(self, title, artist, current):
        song = self.collection.find_one({"metadata.title": title, "metadata.artist": artist})
        song_filename = song.get("filename")
        song_data = song.get("data")
        if not song_data:
            response = "The song " + title + " from " + artist + " does not exist."
        else:
            if self.player.is_playing():
                self.player.stop()

            temp_filename = os.path.join("assets", f"{song_filename}.mp3")
            with open(temp_filename, "wb") as f:
                f.write(song_data)

            output = 'sout=#transcode{vcodec=none,acodec=mp3,ab=128,channels=2,samplerate=44100}:http{mux=raw,dst=:8080/stream.mp3}'
            media = self.vlc_instance.media_new(temp_filename, output)

            self.player.set_media(media)
            self.player.play()

            response = "The song " + title + " from " + artist + " is playing on " + self.streaming_url
        return response

    def pauseMusic(self, current):
        self.player.pause()
        return "The song has been paused."

    def resumeMusic(self, current):
        self.player.play()
        return "The song has been resumed."

    def stopMusic(self, current):
        self.player.stop()
        self.vlc_instance.release()
        return "The song has been stopped."


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
