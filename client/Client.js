const Ice = require("ice").Ice;
const SOUP = require("./generated/SOUP").SOUP;
const fs = require("fs");
const converter = require("convert-string");

async function helloWorld(twoway) {
    console.log("Calling helloWorld...");
    twoway.helloWorld();
}

async function addMusic(filename, title, artist, album, genre, twoway) {
    console.log("Adding music...");
    const filePath = `./assets/${filename}.mp3`;
    let data = fs.readFileSync(filePath);
    console.log(await twoway.addMusic(filename, title, artist, album, genre, data));
}

async function deleteMusic(title, artist, twoway) {
    console.log("Deleting music...");
    console.log(await twoway.deleteMusic(title, artist));
}

async function playMusic(title, artist, twoway) {
    console.log("Playing music...");
    console.log(await twoway.playMusic(title, artist));
}

async function pauseMusic(twoway) {
    console.log("Pausing music...");
    console.log(await twoway.pauseMusic());
}

async function resumeMusic(twoway) {
    console.log("Resuming music...");
    console.log(await twoway.resumeMusic());
}

async function stopMusic(twoway) {
    console.log("Stopping music...");
    console.log(await twoway.stopMusic());
}

async function main() {
    try {
        // --------- ICE configuration ---------
        properties = Ice.createProperties();
        properties.setProperty("Ice.MessageSizeMax", "102400");  // Set the maximum message size to 100 MB
        properties.setProperty("Ice.Override.ConnectTimeout", "5000");  // Set the connection timeout to 5 seconds

        let initialization_data = new Ice.InitializationData(properties);

        // Initialisation du communicateur
        const communicator = Ice.initialize(initialization_data);

        // Création d'un proxy vers l'interface soup
        const proxySpotifyDuPauvre = communicator.stringToProxy("soup:default -p 10000").ice_twoway().ice_secure(false);
        // Création d'un proxy vers l'interface hello
        const proxyHello = communicator.stringToProxy("hello:default -p 10000").ice_twoway().ice_secure(false);

        // Cast des proxys en interfaces
        const twoway1 = await SOUP.HelloPrx.checkedCast(proxyHello);
        const twoway2 = await SOUP.SpotifyDuPauvrePrx.checkedCast(proxySpotifyDuPauvre);

        // Si le cast échoue, on lève une exception
        if (!twoway1 && !twoway2) {
            throw new Error("Invalid proxy");
        }

        // await helloWorld(twoway1);
        // await addMusic("Merveille_Citadelle", "Citadelle", "Merveille", "Citadelle", "Pop", twoway2);
        // await deleteMusic("Citadelle", "Merveille", twoway2);
        // await playMusic("Citadelle", "Merveille", twoway2);
        // await stopMusic(twoway2);
        // await pauseMusic(twoway2);
        await resumeMusic(twoway2);

        communicator.destroy();
    } catch (err) {
        console.error(err.toString());
        process.exitCode = 1;
    }
}

main();