module SOUP
{
    interface Hello
    {
        idempotent void helloWorld();
    };

    sequence<byte> ByteSeq;

    interface SpotifyDuPauvre {
        string addMusic(string filename, string title, string artist, string album, string genre, ByteSeq data);
        string deleteMusic(string title, string artist);
        string playMusic(string title, string artist);
        string pauseMusic();
        string resumeMusic();
        string stopMusic();
    };
};