from machine import UART
from wrap import display_len
from wrap import wrap_text
import upynitel
import network
import urequests
import ujson
import time

#Variable du Minitel
mini = None

def init():
    # Init du serveur Vidéotex
    global mini
    mini = upynitel.Pynitel(UART(2, baudrate=1200, parity=0, bits=7, stop=1))
    try:
        if mini:
            print('Initialisation Terminée !')
            mini.send('Initialisation Terminée !')
            mini.bip()
    except Exception as e:
        print(f"Erreur: {e}")


def connect_wifi():
    # Connection au Wifi
    ssid = "Votre Nom de WIFI"
    password = "MDP Du Wifi"
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connection au réseau ...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('Config Réseau : ', wlan.ifconfig())


def connect_to_api(prompt):
    
    api_key = "Mettez Ici votre clée API"
    url = "https://api.mistral.ai/v1/chat/completions"  # Mettez Votre URL de Modèle que vous souhaitez

    # Préparation des headers HTTP
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Utiliser le texte saisi comme prompt
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.55  # Paramètre pour contrôler la créativité de l'IA
    }

    try:
        json_body = ujson.dumps(payload).encode('utf-8')
        response = urequests.post(url, headers=headers, data=json_body)
        if response.status_code == 200:
            data = response.json()
            # Récupération de la réponse
            result = data["choices"][0]["message"]["content"]
            # Conversion des accents pour Minitel
            result_text_accent = mini.accents(result)
            print(result_text_accent)
            # Clean la zone d'écriture
            mini.canblock(9, 23, 9)
            # Ecriture de la réponse
            lines = wrap_text(result_text_accent, 30)
            for i, line in enumerate(lines[:15]):
                if display_len(line) > 30:
                    cropped = ''
                    count = 0
                    j = 0
                    while j < len(line) and count < 30:
                        if line[j] == '\x19':
                            cropped += line[j:j+3]
                            j += 3
                            count += 1
                        else:
                            cropped += line[j]
                            j += 1
                            count += 1
                    line_to_send = cropped
                else:
                    line_to_send = line
                    
                mini.locate(i + 9,9)
                mini.send(line)
            
        else:
            print("Erreur API:", response.status_code)
            print("Details :", response.text)
    except Exception as e:
        print("Erreur lors de la connexion à l'API:", e)


def send_message(prompt):
    mini.message(5, 8, 5, mini.accents("Envoi de la requête..."))
    connect_to_api(prompt + " et Réponds brièvement")


# Connexion WiFi et initialisation
connect_wifi()
init()
# Rafraichissement de l'écran puis affichage de la page
mini.cls()
mini.xdraw('page.vtx')
# Lancement du message de bienvenue
send_message("Tu est un Minitel Intelligent et il faut que tu te présente à l'utilisateur")
texte_initial = ""

# Boucle principale : on attend une saisie sur le Minitel
while True:
    # Affiche une zone de saisie à la ligne 4, colonne 8, de longueur 32
    texte_saisi, touche = mini.input(ligne=4, colonne=8, longueur=32, data=texte_initial, caractere=' ', redraw=True)
    # Si la touche # est pressée, on envoie le texte saisi à l'API
    if touche == ord('#'):
        send_message(texte_saisi)

