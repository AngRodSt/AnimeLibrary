from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_session import Session
import sqlite3
import base64
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user') is None:
            return redirect('/login')
        else:
            return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    #save_image_to_db('Pokemon', 'static/images/pokemon-picture.jpg', 276, 'Action, Adventure, Comedy, Kids, Fantasy', 'TV', 'Finished Airing', '1997', '7.34', 'Pokémon are peculiar creatures with a vast array of different abilities and appearances; many people, known as Pokémon trainers, capture and train them, often with the intent of battling others. Young Satoshi has not only dreamed of becoming a Pokémon trainer but also a "Pokémon Master," and on the arrival of his 10th birthday, he finally has a chance to make that dream a reality.')
    #save_image_to_db("Kuroshitsuji", 'static/images/blackb-picture.jpg', 24, 'Action, Comedy, Historical, Demons, Supernatural, Shounen', 'TV', 'Finished Airing', '2008', '7.77', 'Young Ciel Phantomhive is known as "the Queen''s Guard Dog," taking care of the many unsettling events that occur in Victorian England for Her Majesty. Aided by Sebastian Michaelis, his loyal butler with seemingly inhuman abilities, Ciel uses whatever means necessary to get the job done. But is there more to this black-clad butler than meets the eye?')
    #save_image_to_db('InuYasha', 'static/images/inuyasha-picture.jpg', 167, 'Action, Adventure, Comedy, Historical, Demons, Supernatural, Romance, Shounen', 'TV', 'Finished Airing', '2000', '7.86', "Kagome Higurashi's 15th birthday takes a sudden turn when she is forcefully pulled by a demon into the old well of her family's shrine. Brought to the past, when demons were a common sight in feudal Japan, Kagome finds herself persistently hunted by these vile creatures, all yearning for an item she unknowingly carries: the Shikon Jewel, a small sphere holding extraordinary power.")
    #save_image_to_db('JoJo no Kimyou na Bouken', 'static/images/jojo-man-picture.jpg', 26, 'Action, Adventure, Supernatural, Vampire, Shounen', 'TV', 'Finished Airing', '2012', '8.26', "Kujo Jotaro is a normal, popular Japanese high-schooler, until he thinks that he is possessed by a spirit, and locks himself in prison. After seeing his grandfather, Joseph Joestar, and fighting Joseph's friend Muhammad Abdul, Jotaro learns that the 'Spirit' is actually Star Platinum, his Stand, or fighting energy given a semi-solid form. ")
    # Fetches the animes from the database.
    animes = fetch_anime_images()
    animeLimit = fetch_anime_images_limit(0 , 5)
    if request.method == 'POST':
        # Gets the anime id from the form and saves it in the session to display the anime description.
        id_anime = request.form.get('anime_id')
        if id_anime:
            if not id_anime:
                flash('No Anime ID received', 'error')
                return render_template('index.html', animes=animeLimit)
            for anime in animes:
                if int(id_anime) == int(anime[0]):
                    session['anime'] = [anime]
                    return render_template('descripcion.html', animes = [anime])
        # Gets the title from the form and filters the animes by the title.
        title = request.form.get('title')
        if not title:
            flash('Space can not be blank', 'error')
            return render_template('index.html', animes=animeLimit)
        for anime in animes:
            if title.lower() in anime[1].lower():
                return render_template('index.html', animes = [anime])
        return render_template('index.html', animes=animes)
    return render_template('index.html', animes=animeLimit)

# Route to save the user in the database
@app.route('/register', methods=['GET', 'POST'])
def register():
    # If the request is a POST request, it will save the user in the database.
    if request.method == 'POST':
        conn = sqlite3.connect('anime.db', check_same_thread=False)
        db = conn.cursor()
        username = request.form.get('name')
        password = request.form.get('password')
        confirmed_password = request.form.get('confirm')

        # Checks if the password and the confirmed password are the same.
        if password != confirmed_password:
            flash('Passwords does not mach', 'error')
            return render_template('register.html')
        password = generate_password_hash(password)
        rows = db.execute('SELECT * FROM users WHERE name = ?', (username,)).fetchall()

        # Checks if the user already exists in the database
        if rows:
            flash('User already exist', 'error')
            return render_template('register.html')
        db.execute('INSERT INTO users (name, password) VALUES (?, ?)', (username, password))

        # Gets the user from the database and saves it in the session.
        getUser= db.execute('SELECT id FROM users WHERE name = ?', (username,)).fetchone()
        session['user'] = getUser
        conn.commit()
        conn.close()
        return redirect('/login')
    return render_template('register.html')

# Route to look for the user in the database
@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        conn = sqlite3.connect('anime.db', check_same_thread=False)
        db = conn.cursor()
        username = request.form.get('user')
        if not username:
            flash('No username received', 'error')
            return render_template('login.html')
        password = request.form.get('password')
        if not password:
            flash('No password received', 'error')
            return render_template('login.html')
        rows = db.execute('SELECT * FROM users WHERE name = ?', (username,)).fetchall()
        if not rows:
            flash('User does not exist', 'error')
            return render_template('login.html')

        user = rows[0]
        if not check_password_hash(user[2], password):
            flash('Invalid password', 'error')
            return render_template('login.html')
        session['user'] = user
        conn.close()
        return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/myList', methods=['GET', 'POST'])
def myList():
    animes = fetch_anime_images()
    anime_list = fetch_anime_images_library()
    if request.method == 'POST':
        user_id = session['user'][0]
        delete_id = request.form.get('delete_id')
        if delete_id:
            if not delete_id:
                flash('No Anime ID received', 'error')
                return render_template('myList.html',animes=anime_list)
            conn = sqlite3.connect('anime.db', check_same_thread=False)
            db = conn.cursor()
            db.execute('DELETE FROM library WHERE anime_id = ? and user_id = ?', (delete_id, user_id))
            conn.commit()
            conn.close()
            anime_list = fetch_anime_images_library()
            return render_template('/myList.html', animes=anime_list)
        id_anime = request.form.get('anime_id')
        if id_anime:
            if not id_anime:
                flash('No Anime ID received', 'error')
                return render_template('myList.html',animes=anime_list)
            for anime in animes:
                if int(id_anime) == int(anime[0]):
                    return render_template('descripcion.html', animes = [anime])
    return render_template('myList.html',animes=anime_list)

@app.route('/descripcion', methods=['GET', 'POST'])
def descripcion():
    animes = fetch_anime_images()
    if request.method == 'POST':
        conn = sqlite3.connect('anime.db', check_same_thread=False)
        db = conn.cursor()
        id_anime = request.form.get('anime_id')
        if not id_anime:
            flash('No Anime ID received', 'error')
            return render_template('descripcion.html',animes = session['anime'])

        anime_on_list = db.execute('SELECT * FROM library WHERE anime_id = ? AND user_id = ?', (id_anime, session['user'][0])).fetchall()
        if anime_on_list:
            flash('Anime already in your list', 'error')
            return render_template('descripcion.html',animes = session['anime'])
        db.execute('INSERT INTO library (anime_id, user_id) VALUES (?, ?)', (id_anime, session['user'][0]))
        conn.commit()
        conn.close()
        flash('Anime added to your list', 'success')
        return render_template('descripcion.html',animes = session['anime'])

    return render_template('descripcion.html',animes = session['anime'])

@app.route('/directory/1', methods=['GET', 'POST'])
def directory1():
    animes = fetch_anime_images()
    animeLimit = fetch_anime_images_limit(0 , 25)
    if request.method == 'POST':
        id_anime = request.form.get('anime_id')
        if id_anime:
            if not id_anime:
                flash('No Anime ID received', 'error')
                return render_template('directory1.html', animes=animeLimit)
            for anime in animes:
                if int(id_anime) == int(anime[0]):
                    session['anime'] = [anime]
                    return render_template('descripcion.html', animes = [anime])
        # Gets the title from the form and filters the animes by the title.
        title = request.form.get('title')
        if title:
            if not title:
                flash('Space cannot be blank', 'error')
                return render_template('directory1.html', animes=animes)
            else:
                filtered_animes = [anime for anime in animes if title.lower() in anime[1].lower()]
                if not filtered_animes:
                    flash('No animes found with the given title', 'error')
                    return render_template('directory1.html', animes=animeLimit)
                else:
                    return render_template('directory1.html', animes=filtered_animes)

    return render_template('directory1.html', animes=animeLimit)

@app.route('/directory/2', methods=['GET', 'POST'])
def directory2():
    animes = fetch_anime_images()
    animeLimit = fetch_anime_images_limit(25 , 25)
    if request.method == 'POST':
        id_anime = request.form.get('anime_id')
        if id_anime:
            if not id_anime:
                flash('No Anime ID received', 'error')
                return render_template('directory2.html', animes=animeLimit)
            for anime in animes:
                if int(id_anime) == int(anime[0]):
                    session['anime'] = [anime]
                    return render_template('descripcion.html', animes = [anime])
        # Gets the title from the form and filters the animes by the title.
        title = request.form.get('title')
        if title:
            if not title:
                flash('Space cannot be blank', 'error')
                return render_template('directory2.html', animes=animes)
            else:
                filtered_animes = [anime for anime in animes if title.lower() in anime[1].lower()]
                if not filtered_animes:
                    flash('No animes found with the given title', 'error')
                    return render_template('directory2.html', animes=animeLimit)
                else:
                    return render_template('directory2.html', animes=filtered_animes)

    return render_template('directory2.html', animes=animeLimit)

# Route to autocomplete the search bar
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

def fetch_anime_images_library():
    conn = sqlite3.connect('anime.db', check_same_thread=False)
    db = conn.cursor()
    user_id = session['user'][0]
    query = '''
    SELECT id, title, image, date, description
    FROM library
    JOIN anime ON library.anime_id = anime.id
    WHERE library.user_id = ?
    '''
    animes = db.execute(query, (user_id,)).fetchall()
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

def fetch_anime_images_limit(id, limit):
    conn = sqlite3.connect('anime.db', check_same_thread=False)
    db = conn.cursor()
    animes = db.execute('SELECT * FROM anime WHERE id > ? LIMIT ?', (id, limit,)).fetchall()
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

if __name__ == '__main__':
    app.run()
