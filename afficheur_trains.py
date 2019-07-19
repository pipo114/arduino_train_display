import csv
import datetime
import sys
import time

# type afficheurs : departs ou arrivees
import serial
import serial.tools.list_ports

serie = serial.Serial()

# indexes des colonnes dans le fichier d'horaires
HEURE = 0
DESTINATION = 1
VOIE = 2

NB_TRAINS_A_AFFICHER = 6
TEMPORISATION_SEC = 5

SSD1306_NB_CHAR_LIGNE = 21
SSD1306_NB_LIGNES = 8


def formater_lignes_afficheur(trains_a_afficher, is_depart=True):
    '''
    Formate les trains pour que cela rendre bien sur le module SSD1306
    :param trains_a_afficher:
    :return: string contenant toutes les lignes a envoyer à l'arduino
    '''

    '''
    répartition des charactères :
	heure : 5 char
	espace
	destination 12 char
	espace
	voie : 2 char
    '''
    result = ''

    # ligne de titre / en tetes
    titre = "DEPART" if is_depart else "ARRIVEE"
    titre = titre.ljust(10, " ")
    result += "HEURE %s VOIE;" % titre;
    result += "---------------------;";

    # affichage des trains
    for train in trains_a_afficher:
        # on tronque la destination
        train[DESTINATION] = str(train[DESTINATION])[:12]
        train[VOIE] = str(train[VOIE])[:2]

        result += train[HEURE]
        result += ' '
        result += str(train[DESTINATION]).ljust(12, " ")
        result += ' '
        result += str(train[VOIE]).rjust(2, " ")
        result += ";"
    return result


def charger_fichier(fichier):
    '''
    Charge le fichier d'horaireq
    :param fichier:
    :return:
    '''
    horaires = []
    with open(fichier, 'r') as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            horaires.append(row)
    csvFile.close()

    return horaires


def get_heure():
    '''
    Récupère l'heure de référence.
    :return:
    '''
    return datetime.datetime.now()


def filtrer_trains(horaires):
    '''
    Filtre les trains à afficher en fonction d'une heure donnée
    :param horaires:
    :return:
    '''
    now = get_heure();
    trains_a_afficher = []

    # filtre les trains à afficher
    for train in horaires:
        heure = train[HEURE]
        destination = train[DESTINATION]
        voie = train[VOIE]

        # transforme la date str en date
        heure = datetime.datetime.strptime(heure, '%H:%M')
        heure = now.replace(hour=heure.hour, minute=heure.minute, second=0, microsecond=0)

        if heure > now:
            trains_a_afficher.append(train)
        if len(trains_a_afficher) >= NB_TRAINS_A_AFFICHER:
            break
    return trains_a_afficher


def envoi_serial(ligne):
    ligne += '\n'
    ligne = ligne.encode('ascii')

    if serie.is_open:
        serie.write(ligne)


def afficheur_trains():
    '''
    Programme principal
    :return:
    '''

    # récupérations des bons COM ports
    com_ports_dispo = []
    for port in serial.tools.list_ports.comports():
        com_ports_dispo.append(port.device)
    print("Ports séries détectés : %s " % com_ports_dispo)
    #com_ports_dispo = ['/dev/ttyUSB0']

    # ouverture du premier port série disponible
    global serie
    for port in com_ports_dispo:
        try:
            serie = serial.Serial(port, 115200, timeout=1)
            if not serie.is_open:
                serie.open()
            break
        except (OSError, serial.SerialException):
            pass

    while True:
        # chargement des trains depuis le fichier en question
        horaires_arrivees = charger_fichier('arrivees.csv')
        horaires_departs = charger_fichier('departs.csv')
        # filtrage des trains en fonction de l'heure de référence
        trains_arrivees = filtrer_trains(horaires_arrivees)
        trains_departs = filtrer_trains(horaires_departs)

        # formatage de la ligne en question.
        ligne = formater_lignes_afficheur(trains_arrivees, False)
        # les arrivees et departs sont séparées par un @
        ligne += '@'
        ligne += formater_lignes_afficheur(trains_departs, True)

        print(ligne)
        # envoi de la ligne sur le serial
        envoi_serial(ligne)

        time.sleep(TEMPORISATION_SEC)

    sys.exit(0)


if __name__ == '__main__':
    afficheur_trains()
