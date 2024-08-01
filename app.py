from flask import Flask, render_template, request, redirect, url_for
from flask_session import Session
import sqlite3
import base64

app = Flask(__name__)

# Conection to the database


@app.route('/')
def index():
    # Fetches all the anime from the database.
    conn = sqlite3.connect('anime.db', check_same_thread=False)
    db = conn.cursor()
    animes = db.execute('SELECT * FROM anime').fetchall()
    if not animes:
        conn.close()
        return 'No anime found in the database.'
    # Fetches the image from the database.
    image_base64 = get_image_from_db(int(animes[0][0]))
    # Renders the index.html template with the anime and image.
    return render_template('index.html', animes=animes, image_base64=image_base64)

def save_image_to_db(title, image, episodes, genre, type, 
status, start_date, end_date, rating, members):
    
    conn = sqlite3.connect('anime.db', check_same_thread=False)
    db = conn.cursor()
    with open(image, 'rb') as file:
        blob_data = file.read()

    db.execute('INSERT INTO anime (title, image, episodes, genre, type, status, start_date, end_date, rating, members) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
              (title, blob_data, episodes, genre, type, status, start_date, end_date, rating, members))
    
    conn.commit()
    conn.close()

def get_image_from_db(anime_id):

    conn = sqlite3.connect('anime.db', check_same_thread=False)
    db = conn.cursor()
    anime_id = int(anime_id)
    # Fetches the image from the database.
    image= db.execute('SELECT image FROM anime WHERE id = ?', (anime_id,)).fetchone()[0]
    # Encodes the image to base64.
    base64_data = base64.b64encode(image).decode('utf-8')
    conn.close()

    return base64_data

if __name__ == '__main__':
    app.run()