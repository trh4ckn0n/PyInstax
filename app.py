from flask import Flask, render_template, request, jsonify
import os
from bruteforce import BruteForce

app = Flask(__name__)

# Route principale
@app.route('/')
def index():
    return render_template('index.html')

# Route pour lancer l'attaque de brute force
@app.route('/start_bruteforce', methods=['POST'])
def start_bruteforce():
    # Récupération des données du formulaire
    username = request.form['username']
    wordlist = request.form['wordlist']

    # Vérifie que le fichier de wordlist existe
    if not os.path.isfile(f'wordlists/{wordlist}.txt'):
        return jsonify({"status": "error", "message": "Le fichier de wordlist n'existe pas."})

    bf = BruteForce(username, wordlist)
    result = bf.start_attack()

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
