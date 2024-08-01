from flask import Flask, render_template, request, redirect, url_for
from flask_session import Session
import sqlite3
import base64

app = Flask(__name__)

# Conection to the database


@app.route('/')
def index():
    
    #save_image_to_db('Blue-Lock','static/images/blue-lock-picture.jpg', 24, 'Action, Shounen, Sports', 'Manga', 'Ongoing', '2021', 8.5, 'The project is ultimate goal is to turn one of the selected players into the star striker for the Japanese national team. To find the best participant, each diamond in the rough must compete against others through a series of solo and team competitions to rise to the top. Putting aside his ethical objections to the project, Isagi feels compelled to fight his way to the top, even if it means ruthlessly crushing the dreams of 299 aspiring young strikers.')
    animes = fetch_anime_images()
    #image_base64 = get_image_from_db(int(animes[0][0]))
    # Renders the index.html template with the anime and image.
    return render_template('index.html', animes=animes)


def fetch_anime_images():
    conn = sqlite3.connect('anime.db', check_same_thread=False)
    db = conn.cursor()
    animes = db.execute('SELECT * FROM anime').fetchall()
    if not animes:
        conn.close()
        return []
    
    updated_animes = []
    for anime in animes:
        anime = list(anime)
        anime[2] = base64.b64encode(anime[2]).decode('utf-8') 
        updated_animes.append(anime)
    
    conn.close()
    return updated_animes

# Function to add anime to the database.
def save_image_to_db(title, image, episodes, genre, type, 
status, date, rating, description):
    
    conn = sqlite3.connect('anime.db', check_same_thread=False)
    db = conn.cursor()
    # Opens the image file.
    with open(image, 'rb') as file:
        blob_data = file.read()
    # Inserts the anime into the database.
    db.execute('INSERT INTO anime (title, image, episodes, genre, type, status, date, rating, description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
              (title, blob_data, episodes, genre, type, status, date, rating, description))
    
    conn.commit()
    conn.close()

# Function to get the image from the database.
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