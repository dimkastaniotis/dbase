from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)

# Ρύθμιση Βάσης Δεδομένων (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Spotify Credentials (από μεταβλητές περιβάλλοντος)
CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')

# Αρχικοποίηση Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Μοντέλο Τραγουδιού
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    artist = db.Column(db.String(200))

# Συναρτήσεις Spotify
def search_spotify(query):
    results = sp.search(q=query, type='track')
    items = results['tracks']['items']
    songs = []
    for item in items:
        song = {
            'title': item['name'],
            'artist': item['artists'][0]['name']
        }
        songs.append(song)
    return songs

# Routes
@app.route('/')
def index():
    query = request.args.get('query', '')  # Παίρνουμε το query από τα arguments
    songs = Song.query.all()
    search_results = search_spotify(query) if query else None  # Κάνουμε την αναζήτηση μόνο αν υπάρχει query
    return render_template('index.html', songs=songs, search_results=search_results, query=query)

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    results = search_spotify(query)
    return render_template('index.html', songs=Song.query.all(), search_results=results, query=query)

@app.route('/add', methods=['POST'])
def add():
    title = request.form['title']
    artist = request.form['artist']
    query = request.form.get('query', '')  # Παίρνουμε το query αναζήτησης
    song = Song(title=title, artist=artist)
    db.session.add(song)
    db.session.commit()
    # Επιστρέφουμε στην index με το query αναζήτησης
    return redirect(url_for('index', query=query))

@app.route('/delete/<id>')
def delete(id):
    song = Song.query.get(int(id))
    db.session.delete(song)
    db.session.commit()
    return redirect(url_for('index'))

#Δημιουργία των πινάκων
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
