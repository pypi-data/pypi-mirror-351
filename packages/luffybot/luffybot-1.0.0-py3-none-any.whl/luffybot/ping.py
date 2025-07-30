import requests
import threading
import time
import os

STATUS_URL = "https://bothulkvikidia.pythonanywhere.com/status"

def envoyer_ping():
    while True:
        try:
            requests.get(STATUS_URL)
        except Exception as e:
            print(f"Erreur en envoyant le statut : {e}")
        time.sleep(60)  # Ping toutes les 60 secondes

# Lancer le thread en arrière-plan
threading.Thread(target=envoyer_ping, daemon=True).start()