const Ice = require("ice").Ice;
const Demo = require("./generated/Hello").Demo;

const main = async () => {
    try {
        // Initialisation du communicateur
        const communicator = Ice.initialize();

        // Création d'un proxy vers l'interface Hello
        const proxy = communicator.stringToProxy("hello:default -p 10000").ice_twoway().ice_secure(false);

        // Cast du proxy en une interface HelloPrx
        const twoway = await Demo.HelloPrx.checkedCast(proxy);

        // Si le cast échoue, on lève une exception
        if (!twoway) {
            throw new Error("Invalid proxy");
        }

        // Appel de la méthode helloWorld de l'interface HelloPrx
        await twoway.helloWorld();

        // Destruction du communicateur
        communicator.destroy();

    } catch (err) {
        console.error(err.toString());
        process.exitCode = 1;
    }
};

main();
