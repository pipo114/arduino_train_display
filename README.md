# Afficheurs pour train

Ce projet présente un montage permettant de créer un mini tableau d'affichage de gare, afin d'être intégré dans les maquettes HO.
Ce montage a été pensé pour répondre aux besoins du réseau de TrainTrain76, représentant la gare de Rouen en 1968 (cf : http://gare-rouen-droite.over-blog.com/2019/07/afficheur-automatique-des-destinations-gare-rouen-droite.html)  

[![Vidéo](https://img.youtube.com/vi/AOTOA2RGIOY/0.jpg)](https://www.youtube.com/watch?v=AOTOA2RGIOY)

Ce projet est fortement inspiré du montage réalisé par [Gilbert](https://www.locoduino.org/spip.php?article205). 
Les différences notables avec son projet est que le montage est composé de 2 parties (affichage et intelligence), permetttant de modifier plus aisément les horaires et de se caler sur une horloge de référence.

Les ressources sont les suivantes :
- `2afficheur_gare_i2c.ino` : sketch Arduino permettant l'affichage des données sur deux petits écrans SDD1306 (dimension 128x64 pixels)
- `afficheur_trains.py` : programme en python qui lit les horaires et calcule les informations à afficher en fonction d'une heure de référence
- `departs.csv` et `arrivees.csv` : fichiers contenant les horaires de trains au départ et à l'arrivée.

## Architecture générale

Le principe du montage est composé de deux parties : 
1. Une partie affichage, composé d'ESP8266 (Weimos D1 mini), et de 2 écrans OLED SDD1306
2. Une partie intelligente et centralisée hébergée sur un PC, codé en python.

Les deux parties communiques par le biais d'un cable série micro USB. Afin d'être transportable, le montage ne doit pas reposer sur un réseau wifi.

Afin de simplifier au maximum le montage, il est plus facile de faire séparer les fonctions entre les deux parties : 
1. La partie affichage effectue seulement l'affichage, sans traiter les informations
2. La partie intelligente effectue les tâches plus complexes :
- lecture et référencement des horaires de départs et d'arrivées.
- récupération de l'heure de référence. Ici l'heure du PC hôte mais on pourra par la suite se baser sur une horloge simulée, comme le système de gestion de réseau LadyBird.
- calcul des prochains horaires de départs et d'arrivées en fonction de l'heure de référence
- mise en forme de l'information afin qu'il corresponde parfaitement aux afficheurs SDD1306 (nombre ligne, colonnes, etc...)
- détection des ports COM accessibles et connection au premier port trouvé.
- envoi de l'information et boucle de fonctionnement général.


## Schéma de câblage.

Afin de pouvoir faire fonctionner deux écrans connectés à un seul Arduino, il préférable d'utiliser le protocol I2C fonctionnant bus de donnée.
Le déplacement d'un résistance sur l'un des écrans est nécéssaire afin de modifier l'adresse d'un écran dans le bus I2C. (voir https://www.locoduino.org/spip.php?article205 )

![schema de cablage](https://www.locoduino.org/local/cache-vignettes/L610xH276/cablage_03-f01c7.jpg?1548598550)

## Prérequis

Pour la partie Arduino (ou ESP8266 dans notre cas), il faut les librairies suivantes :
- Adafruit_SSD1306
- Adafruit_GFX

Pour la partie intelligente (sur Windows/Mac/Linux), il faut les composants suivants :
- Python 3.7
- la librairie pySerial pour Python 3.7 (à installer avec pip)
- les drivers pour la communication avec l'Arduino/ESP. Dans notre cas, nous avons utilisé un Weimos D1 mini, et les drivers peuvent être téléchargés [ici](https://wiki.wemos.cc/downloads) 

Il est aussi nécessaire de respecter les formats des horaires dans les fichiers `departs.csv` et `arrivees.csv`
```
HH:mm,DESTINATION,VOIE
06:27,PARIS,2
```

## Lancement du programme
Une fois tout branché correctement, le programme peut être lancé sur l'ordinateur via la command shell suivante : 
```
python afficheur_trains.py 
```
Le lanceur `lancer_afficheurs.bat` permet de lancer ce programme facilement sur Windows.

## Améliorations possibles
- [X] Rafraichissement uniquement si détection de données différentes
- [X] Contrôle et selection manuelle du port COM à utiliser.
- [X] Amélioration de l'affichage sur la console.
- [ ] Dockerisation du système (facilitation de l'installation de python et des librairies)
- [ ] Intégration d'une version déportée sur page WEB de l'affichage
