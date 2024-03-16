# SpOtify dU Pauvre (SOUP) - ICE Project

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
python3 Server.py
```

### Client

```bash
cd client
slice2js SOUP.ice --output-dir generated
node Client.js
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