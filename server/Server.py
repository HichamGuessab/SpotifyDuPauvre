import Ice
import sys

# Importation du module
Ice.loadSlice('Hello.ice')
import Demo


# Définition d'une classe correspondant à l'interface "Hello" définit dans le fichier "Hello.ice"
class HelloI(Demo.Hello):
    def helloWorld(self, current=None):
        print(f"Hello World!")


def main():
    with Ice.initialize(sys.argv) as communicator:
        # Création d'un objet de type "ObjectAdapter" avec pour nom "HelloAdapter" et pour endpoint "default -h localhost -p 10000"
        adapter = communicator.createObjectAdapterWithEndpoints("HelloAdapter", "default -h localhost -p 10000")
        # Création d'un objet de type "HelloI"
        hello = HelloI()
        # Ajout de l'objet "hello" à l'adapter
        adapter.add(hello, communicator.stringToIdentity("hello"))
        # Activation de l'adapter
        adapter.activate()
        print("Server is ready to accept requests.")
        # Attente de la fin du serveur
        communicator.waitForShutdown()


if __name__ == "__main__":
    main()
