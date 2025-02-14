from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

# Δημιουργία εφαρμογής Flask
app = Flask(__name__)

# Ρύθμιση Βάσης Δεδομένων (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db' #Σχετική διαδρομή
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Μοντέλο TODO
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    complete = db.Column(db.Boolean)

# Routes
@app.route('/')
def index():
    todos = Todo.query.all()
    return render_template('index.html', todos=todos)

@app.route('/add', methods=['POST'])
def add():
    text = request.form['text']
    todo = Todo(text=text, complete=False)
    db.session.add(todo)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/complete/<id>')
def complete(id):
    todo = Todo.query.get(int(id))
    todo.complete = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<id>')
def delete(id):
    todo = Todo.query.get(int(id))
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('index'))

#Δημιουργία των πινάκων
with app.app_context():
        db.create_all()

if __name__ == '__main__':
    app.run(debug=True)