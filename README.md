# SpOtify dU Pauvre (SOUP) - ICE Project

## Hicham Guessab - M1 ALTERNANT

## Installation 

### Serveur
- Créer un environnement virtuel
```
cd server
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Client
```
cd client
npm install
```

## Lancement : Hello World

### Serveur

```bash
cd server
source venv/bin/activate # Si ce n'est pas déjà fait
python3.11 Server.py
```

### Client
NodeVersion : 21.7.1
```bash
npm install #très important sinon le client ne fonctionnera pas
cd client
slice2js SOUP.ice --output-dir generated
node Client.js
```

### Subscriber

```bash
icebox --Ice.Config=config.icebox
```

```bash
python3.11 TwoSubscriber.py
```

## Informations
### Structure BDD

```
    {
        'filename': filename,
        'metadata': {
            'title': title,
            'artist': artist
            'genre': genre,
            'album': album,
        },
        'data': data
    }
```

### Autres

J'ai laissé l'autre fichier 'subscriber.py' et 'publisherTest.py' pour prouver le travail acharné que j'ai effectué sur le cas du IceStorm qui ne fonctionnait pas avec mon javascript.
J'ai également laissé les quelques commentaires en rapport avec ces essais.
Quoi qu'il en soit le IceStorm fonctionne bien, le 'twosubscriber.py' est donc présent pour prouver que le IceStorm fonctionne bien.