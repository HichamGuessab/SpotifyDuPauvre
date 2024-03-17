module SOUP
{
    interface Hello
    {
        idempotent void helloWorld();
    };

    sequence<byte> ByteSeq;

    interface SpotifyDuPauvre {
        void addMusic(string filename, string title, string artist, string album, string genre, ByteSeq data);
        string playMusic(string title, string artist);
    };
};