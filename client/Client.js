const Ice = require("ice").Ice;
const SOUP = require("./generated/SOUP").SOUP;
const fs = require("fs");
const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
});

class LibraryUpdatesI {
    libraryUpdated(action, data) {
        console.log("Received notification");  // Add this line
        console.log(`Library updated: ${action} - ${data}`);
    }
}

async function displayMenu() {
    console.log("\n*** Spotify Du Pauvre ***");
    console.log("1. Add Music");
    console.log("2. Delete Music");
    console.log("3. Edit Music");
    console.log("--------------");
    console.log("4. Play Music");
    console.log("5. Pause Music");
    console.log("6. Resume Music");
    console.log("7. Stop Music");
    console.log("--------------");
    console.log("8. Research Music");
    console.log("0. Exit");
}

async function handleUserInput(twoway) {
    readline.question('Enter your choice: ', async choice => {
        switch (choice) {
            case '1':
                await addMusicMenu(twoway);
                break;
            case '2':
                await deleteMusicMenu(twoway);
                break;
            case '3':
                await editMusicMenu(twoway);
                break;
            case '4':
                await playMusicMenu(twoway);
                break;
            case '5':
                await pauseMusic(twoway);
                break;
            case '6':
                await resumeMusic(twoway);
                break;
            case '7':
                await stopMusic(twoway);
                break;
            case '8':
                await researchMusicMenu(twoway);
                break;
            case '0':
                console.log("Exiting...");
                communicator.destroy();
                process.exit();
                break;
            default:
                console.log("Invalid choice. Please enter a number from the menu.");
        }
    });
}

async function addMusicMenu(twoway) {
    readline.question('Enter filename, title, artist, album, genre (separated by commas): ', async input => {
        const [filename, title, artist, album, genre] = input.split(",").map(item => item.trim());
        await addMusic(filename, title, artist, album, genre, twoway);
        await displayMenu();
        await handleUserInput(twoway);
    });
}

async function deleteMusicMenu(twoway) {
    readline.question('Enter title and artist (separated by comma): ', async input => {
        const [title, artist] = input.split(",").map(item => item.trim());
        console.log(await twoway.deleteMusic(title, artist));
        await displayMenu();
        await handleUserInput(twoway);
    });
}

async function editMusicMenu(twoway) {
    readline.question('Enter old title, artist, new title, album, genre (separated by commas): ', async input => {
        const [oldTitle, artist, newTitle, album, genre] = input.split(",").map(item => item.trim());
        console.log(await twoway.editMusic(oldTitle, artist, newTitle, album, genre));
        await displayMenu();
        await handleUserInput(twoway);
    });
}

async function playMusicMenu(twoway) {
    readline.question('Enter title and artist: ', async input => {
        const [title, artist] = input.split(",").map(item => item.trim());
        console.log(await twoway.playMusic(title, artist));
        await displayMenu();
        await handleUserInput(twoway);
    });
}

async function researchMusicMenu(twoway) {
    readline.question('Search by \n 0.Title \n 1.Artist \n Enter your choice: ', async choice => {
        switch (choice) {
            case '0':
                await researchMusicByTitleMenu(twoway);
                break;
            case '1':
                await researchMusicByArtistMenu(twoway);
                break;
            default:
                console.log("Invalid choice. Please enter either '0' or '1'.");
        }
    });
}

async function researchMusicByTitleMenu(twoway) {
    readline.question('Enter title: ', async title => {
        await researchMusicByTitle(title, twoway);
    });
}

async function researchMusicByArtistMenu(twoway) {
    readline.question('Enter artist: ', async artist => {
        await researchMusicByArtist(artist, twoway);
    });
}

async function helloWorld(twoway) {
    console.log("Calling helloWorld...");
    twoway.helloWorld();
}

async function researchMusicByTitle(title, twoway) {
    console.log("Researching music by title...");
    const responses = await twoway.researchMusicByTitle(title);
    let i = 0;
    for (const res in responses) {
        console.log(`${i}. Title: ${responses[res].title} | Artist: ${responses[res].artist}`);
        i++;
    }
    readline.question('Enter the number of the song you want to play (or \'q\' to exit): ', async songNumber => {
        if (songNumber === 'q') {
            await displayMenu();
            await handleUserInput(twoway);
        } else if (songNumber < 0 || songNumber >= responses.length) {
            console.log("Invalid number");
        } else {
            await playMusic(responses[songNumber].title, responses[songNumber].artist, twoway);
        }
    });
}

async function researchMusicByArtist(artist, twoway) {
    console.log("Researching music by artist...");
    const responses = await twoway.researchMusicByArtist(artist);
    let i = 0;
    for (const res in responses) {
        console.log(`${i}. Title: ${responses[res].title} | Artist: ${responses[res].artist}`);
        i++;
    }
    readline.question('Enter the number of the song you want to play (or \'q\' to exit): ', async songNumber => {
        if (songNumber === 'q') {
            await displayMenu();
            await handleUserInput(twoway);
        } else if (songNumber < 0 || songNumber >= responses.length) {
            console.log("Invalid number");
        } else {
            await playMusic(responses[songNumber].title, responses[songNumber].artist, twoway);
        }
    });
}

async function addMusic(filename, title, artist, album, genre, twoway) {
    console.log("Adding music...");
    const filePath = `./assets/${filename}.mp3`;
    let data = fs.readFileSync(filePath);
    console.log(await twoway.addMusic(title, artist, album, genre, data));
}

async function editMusic(oldTitle, artist, newTitle, newAlbum, newGenre, twoway) {
    console.log("Editing music...");
    console.log(await twoway.editMusic(oldTitle, artist, newTitle, newAlbum, newGenre));
}

async function playMusic(title, artist, twoway) {
    console.log("Playing music...");
    console.log(await twoway.playMusic(title, artist));
    await displayMenu();
    await handleUserInput(twoway);
}

async function pauseMusic(twoway) {
    console.log("Pausing music...");
    console.log(await twoway.pauseMusic());
    await displayMenu();
    await handleUserInput(twoway);
}

async function resumeMusic(twoway) {
    console.log("Resuming music...");
    console.log(await twoway.resumeMusic());
    await displayMenu();
    await handleUserInput(twoway);
}

async function stopMusic(twoway) {
    console.log("Stopping music...");
    console.log(await twoway.stopMusic());
    await displayMenu();
    await handleUserInput(twoway);
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

        // Création d'un proxy vers l'interface LibraryUpdates
        const libraryUpdates = new LibraryUpdatesI();
        const proxyLibraryUpdates = communicator.stringToProxy("LibraryUpdates:default -p 10001").ice_twoway().ice_secure(false);
        const twoway3 = await SOUP.LibraryUpdatesPrx.checkedCast(proxyLibraryUpdates);
        twoway2.subscribeUpdates(twoway3);

        // Affichage du menu et gestion des choix de l'utilisateur
        await displayMenu();
        await handleUserInput(twoway2);

        process.on('SIGINT', function() {
            console.log("Exiting...");
            twoway2.unsubscribeUpdates(twoway3);
            communicator.destroy();
            process.exit();
        });
    } catch (err) {
        console.error(err.toString());
        process.exitCode = 1;
    }
}

main();