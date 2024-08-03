from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_session import Session
import sqlite3
import base64


app = Flask(__name__)

    #save_image_to_db('Tokyo Revenger','static/images/tokio-revenger-picture.jpg', 24, 'Action, Drama, School, Shounen', 'Manga', 'Ongoing', '2021', 8.70, 'The story follows Takem ichi Hanag ak i, a young man who discovers he has the ability to travel back in time. He uses this power to save his girlfriend from being killed by a gang, but soon finds himself caught up in a dangerous conflict with the gang.')
    #save_image_to_db('Your Name','static/images/Your-name-picture.jpg', 1, 'Drama, Romance, School, Supernatural', 'Movie', 'Finished', '2016', 8.97, 'The story follows two high school students, Taki and Mitsuha, who mysteriously swap bodies. They communicate by leaving notes for each other and eventually fall in love.')
    #save_image_to_db('Seishun Buta Yarou','static/images/Seishun-Buta-Yarou-picture.jpg', 1, 'Comedy, Romance, School, Supernatural', 'Manga', 'Finished', '2018', 8.39, 'The rare and inexplicable Puberty Syndrome is thought of as a myth. It is a rare disease which only affects teenagers, and its symptoms are so supernatural that hardly anyone recognizes it as a legitimate occurrence. However, high school student Sakuta Azusagawa knows from personal experience that it is very much real, and happens to be quite prevalent in his school.')

@app.route('/', methods=['GET', 'POST'])
def index():
    animes = fetch_anime_images()
    if request.method == 'POST':
        title = request.form.get('title')
        if not title:
            return render_template('index.html', animes=animes)
        for anime in animes:
            if title.lower() in anime[1].lower():
                return render_template('index.html', animes = [anime])
        return render_template('index.html')
    return render_template('index.html', animes=animes)

@app.route('/get_animes')
def get_animes():
    animes = fetch_anime_images()
    animes_title = []
    for anime in animes:
        animes_title.append({"label": anime[1]}) 
    return jsonify(animes_title)

# Function to fetch animes from the database.
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