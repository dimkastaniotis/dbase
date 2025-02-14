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

# Μοντέλα Βάσης Δεδομένων
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    songs = db.relationship('Song', backref='playlist', lazy=True)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    artist = db.Column(db.String(200))
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)

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

def get_top_songs():
    # ID της playlist "Top που ακουσα τελευταία"
    playlist_id = '3OwTcD9Z1VAPKCCgtLLR5B'
    # Παίρνουμε τα tracks από την playlist
    results = sp.playlist_items(playlist_id)
    tracks = results['items']
    top_songs = []
    for track in tracks:
        song = {
            'title': track['track']['name'],
            'artist': track['track']['artists'][0]['name']
        }
        top_songs.append(song)
    return top_songs

# Routes
@app.route('/')
def index():
    playlists = Playlist.query.all()
    return render_template('index.html', playlists=playlists)

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    name = request.form['name']
    playlist = Playlist(name=name)
    db.session.add(playlist)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/playlist/<playlist_id>')
def playlist(playlist_id):
    playlist = Playlist.query.get(int(playlist_id))
    songs = Song.query.filter_by(playlist_id=playlist_id).all()
    query = request.args.get('query', '')  # Παίρνουμε το query από τα arguments
    search_results = search_spotify(query) if query else None
    return render_template('playlist.html', playlist=playlist, songs=songs, search_results=search_results, query=query)

@app.route('/search/<playlist_id>', methods=['POST'])
def search(playlist_id):
    query = request.form['query']
    playlist = Playlist.query.get(int(playlist_id))
    results = search_spotify(query)
    return render_template('playlist.html', playlist=playlist, songs=Song.query.filter_by(playlist_id=playlist_id).all(), search_results=results, query=query)

@app.route('/add/<playlist_id>', methods=['POST'])
def add(playlist_id):
    title = request.form['title']
    artist = request.form['artist']
    query = request.form.get('query', '')
    song = Song(title=title, artist=artist, playlist_id=playlist_id)
    db.session.add(song)
    db.session.commit()
    return redirect(url_for('playlist', playlist_id=playlist_id, query=query))

@app.route('/delete/<id>')
def delete(id):
    song = Song.query.get(int(id))
    playlist_id = song.playlist_id
    db.session.delete(song)
    db.session.commit()
    return redirect(url_for('playlist', playlist_id=playlist_id))

@app.route('/popular')
def popular():
    top_songs = get_top_songs()
    return render_template('popular.html', top_songs=top_songs)

#Δημιουργία των πινάκων
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
