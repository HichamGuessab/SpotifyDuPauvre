module SOUP
{
    interface Hello
    {
        idempotent void helloWorld();
    };

    struct MetaData {
        string title;
        string artist;
    };

    sequence<byte> ByteSeq;
    sequence<MetaData> ObjectArray;

    interface SpotifyDuPauvre {
        ObjectArray researchMusic(string title);

        string addMusic(string title, string artist, string album, string genre, ByteSeq data);
        string deleteMusic(string title, string artist);
        string editMusic(string title, string artist, string newTitle, string newAlbum, string newGenre);

        string playMusic(string title, string artist);
        string pauseMusic();
        string resumeMusic();
        string stopMusic();
    };
};