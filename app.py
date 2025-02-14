from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

# Δημιουργία εφαρμογής Flask
app = Flask(__name__)

# Ρύθμιση Βάσης Δεδομένων (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///music.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Μοντέλο Τραγουδιού
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    artist = db.Column(db.String(200))

# Routes
@app.route('/')
def index():
    songs = Song.query.all()
    return render_template('index.html', songs=songs)

@app.route('/add', methods=['POST'])
def add():
    title = request.form['title']
    artist = request.form['artist']
    song = Song(title=title, artist=artist)
    db.session.add(song)
    db.session.commit()
    return redirect(url_for('index'))

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
