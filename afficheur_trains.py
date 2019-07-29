import argparse
import csv
import datetime
import json
import os
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


def formater_lignes_afficheur(trains_a_afficher, is_depart=True, sep=';'):
    """
    Formate les trains pour que cela rendre bien sur le module SSD1306
    :param trains_a_afficher: liste des train à afficher
    :type trains_a_afficher: dict
    :param is_depart: True si affichage des trains au départ
    :type is_depart: bool
    :param sep: séparateur de ligne à utiliser
    :type sep:basestring

    :return: string contenant toutes les lignes a envoyer à l'arduino
    """

    # répartition des charactères :
    # heure : 5 char
    # espace
    # destination 12 char
    # espace
    # voie : 2 char

    result = ''

    # ligne de titre / en tetes
    titre = "DEPART" if is_depart else "ARRIVEE"
    titre = titre.ljust(10, " ")
    result += "HEURE %s VOIE%s" % (titre, sep)
    result += "---------------------" + sep

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
        result += sep
    return result


def charger_fichier(fichier):
    """
    Charge le fichier d'horaireq
    :param fichier:
    :return:
    """
    horaires = []
    with open(fichier, 'r') as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            horaires.append(row)
    csvFile.close()

    return horaires


def get_heure():
    """
    Récupère l'heure de référence.
    :return:
    """
    return datetime.datetime.now()


def filtrer_trains(horaires):
    """
    Filtre les trains à afficher en fonction d'une heure donnée
    :param horaires:
    :return:
    """
    now = get_heure()
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


def print_trains_console(trains_arrivees, horaires_departs):
    # clear
    os.system('cls' if os.name == 'nt' else 'clear')

    print(formater_lignes_afficheur(trains_arrivees, False, '\n'))
    print(formater_lignes_afficheur(horaires_departs, True, '\n'))


def wait_still_next_train(horaires_departs, horaires_arrivees):
    """
    Attends jusqu'à l'arrivée ou le départ du prochaine train.
    :param horaires_departs: liste des trains au départ
    :param horaires_arrivees: liste des trains à l'arrivée
    """

    prochain_depart = filtrer_trains(horaires_departs)[0]
    prochain_arrivee = filtrer_trains(horaires_arrivees)[0]

    date_prochain_depart = datetime.datetime.strptime(prochain_depart[HEURE], '%H:%M')
    date_prochain_arrivee = datetime.datetime.strptime(prochain_arrivee[HEURE], '%H:%M')

    # calcul du prochain train
    prochain_train = date_prochain_depart if date_prochain_depart < date_prochain_arrivee else date_prochain_arrivee

    # format à la date d'aujourd'hui
    now = datetime.datetime.now()
    prochain_train = now.replace(hour=prochain_train.hour, minute=prochain_train.minute, second=0, microsecond=0)

    # attente jusqu'à cette heure
    while True:
        now = datetime.datetime.now()
        if prochain_train < now:
            break
        else:
            time.sleep(TEMPORISATION_SEC)


def print_trains_fichier(trains_arrivees, trains_departs):
    """
    Ecris les horaires dans un fichier
    :param trains_arrivees: trains à afficher à l'arrivée
    :param trains_departs:  trains à afficher au départ
    """
    train_json = {'arrivees': trains_arrivees, 'departs': trains_departs}
    with open(os.path.join('web', 'prochains_trains.json'), 'w') as f:
        json.dump(train_json, f, indent=4)


def afficheur_trains():
    """
    Programme principal
    :return:
    """

    selected_port = get_com_port()
    print("Port sélectionné : %s" % selected_port)

    # ouverture du premier port série disponible
    global serie
    try:
        serie = serial.Serial(selected_port, 115200, timeout=1)
        if not serie.is_open:
            serie.open()
    except (OSError, serial.SerialException):
        pass

    # chargement des trains depuis le fichier en question
    horaires_arrivees = charger_fichier('arrivees.csv')
    horaires_departs = charger_fichier('departs.csv')

    while True:
        # filtrage des trains en fonction de l'heure de référence
        trains_arrivees = filtrer_trains(horaires_arrivees)
        trains_departs = filtrer_trains(horaires_departs)

        # formatage de la ligne en question.
        ligne = formater_lignes_afficheur(trains_arrivees, False)
        # les arrivees et departs sont séparées par un @
        ligne += '@'
        ligne += formater_lignes_afficheur(trains_departs, True)

        print_trains_console(trains_arrivees, trains_departs)
        print_trains_fichier(trains_arrivees, trains_departs)

        # envoi de la ligne sur le serial
        envoi_serial(ligne)

        wait_still_next_train(horaires_departs, horaires_arrivees)

    sys.exit(0)


def get_com_port():
    """
    Récupère le port COM à utiliser
    Soit par le paramètre
    Soit en scannant
    :return: le port COM à utiliser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--comport', help='Definit un port COM à utiliser en particulier')
    args = parser.parse_args()
    if args.comport:
        selected_port = args.comport
    else:
        # récupérations des COM ports
        com_ports_dispo = []
        for port in serial.tools.list_ports.comports():
            com_ports_dispo.append(port.device)
        print("Ports séries détectés : %s " % com_ports_dispo)
        if len(com_ports_dispo) == 1:
            selected_port = com_ports_dispo[0]
        elif len(com_ports_dispo) > 1:
            i = 1
            for com_port in com_ports_dispo:
                print("[%s] %s" % (i, com_port))
            number = input("Quel port COM voulez vous utiliser ? ")
            number = int(number) - 1
            selected_port = com_ports_dispo[number]
        else:
            print("Aucun port trouvé")
            exit(1)
    return selected_port


if __name__ == '__main__':
    afficheur_trains()
