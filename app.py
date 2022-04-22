import datetime
import time
import os
import base64
from enum import auto
from flask import Flask, flash, redirect, render_template, request, session, g
from flask.helpers import url_for
from flask.templating import render_template
from flask_mysqldb import MySQL
from werkzeug.datastructures import FileStorage
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from helper import apology, login_required
from tempfile import mkdtemp
from PIL import Image
 
 
app = Flask(__name__)
app.secret_key = 'DBMS'
app.config["TEMPLATES_AUTO_RELOAD"] = True
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
# Configure session to use filesystem (instead of signed cookies)

ALBUM_ART_FOLDER = 'static/images/album'
app.config["ALBUM_ART_FOLDER"] = ALBUM_ART_FOLDER

PLAYLIST_ART_FOLDER = 'static/images/playlist'
app.config["PLAYLIST_ART_FOLDER"] = PLAYLIST_ART_FOLDER


app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'dbms'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'dbms_proj'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
 
db = MySQL(app)

@app.route('/', methods=["GET", "POST"])
@login_required
def index():
    g.current_user_id = session['user_id']
    cursor = db.connection.cursor()
    cursor.execute("SELECT * FROM USER ORDER BY FOLLOWERS DESC LIMIT 5")
    users = cursor.fetchall()
    top_artists = []
    for user in users:
        top_artists.append(user)
    print(top_artists)
    db.connection.commit()
    cursor.close()
    if request.method == "POST":
        if request.form.get("search"):        
            cursor = db.connection.cursor()
            test_search = request.form.get("search")
            print(test_search)
            search = "%" + request.form.get("search") + "%"
            getAlbumQuery = '''SELECT * FROM ALBUM WHERE ALBUM_NAME LIKE %s'''
            cursor.execute(getAlbumQuery, [search])
            albums = cursor.fetchall()
            len_albums = len(albums)
            getUserQuery = '''SELECT * FROM USER WHERE name LIKE %s'''
            cursor.execute(getUserQuery, [search])
            artists = cursor.fetchall()
            len_artists = len(artists)
            getSongQuery = '''SELECT * FROM SONG WHERE song_name LIKE %s'''
            cursor.execute(getSongQuery, [search])
            songs = cursor.fetchall()
            len_songs = len(songs)
            # print('Songs: ', songs)
            song_list = []
            for i in range(len_songs):
                song_list.append(songs[i])
            album_list = []
            for i in range(len_songs):
                album_list.append(albums[i])
            joinTablesQuery = '''SELECT S.SONG_NAME song, A.ALBUM_NAME album, A.ALBUM_PHOTO album_art, U.NAME user, U.USER_ID id FROM SONG S INNER JOIN ALBUM A ON S.ALBUM_ID = A.ALBUM_ID INNER  JOIN USER U ON A.USER_ID = U.USER_ID WHERE S.SONG_NAME LIKE %s OR A.ALBUM_NAME LIKE %s OR U.NAME LIKE %s'''
            cursor.execute(joinTablesQuery, [search, search, search])
            jointQuery = cursor.fetchall()
            print('\n\nJOINT TABLE QUERY: \n', jointQuery)
            results = []
            for i in range(len(jointQuery)):
                results.append(jointQuery[i])
            print('RESULTS:\n\n', results)
            for i in range(len(jointQuery)):
                imageFile = results[i]['album_art'].decode('UTF-8')
                fileName = imageFile.split(' ')
                filename = fileName[1]
                fileName = 'images/album/' + filename.strip("'")
                imageInfo = url_for('static', filename = fileName)
                results[i]['album_art'] = imageInfo

            # print('Albums: ', albums)
            # print('Artists: ', artists)
            db.connection.commit()
            cursor.close()
            # return render_template('results.html', albums = albums, artists = artists, songs = songs, len_albums = len_albums, len_artists = len_artists, len_songs = len_songs, results = results)
            return render_template('results.html', results = results)
        else:
            return render_template('error.html')
    else:
        return render_template('home.html', top_artists = top_artists)

 
 
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
 
    # Forget any user_id
    session.clear()
 
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
 
        # Query database for username
        cursor = db.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE email = %s", [request.form.get("email")])
        rows = cursor.fetchall()
        password = request.form.get("password")
        # Ensure username exists and password is correct
        if (len(rows) != 1 or not (check_password_hash(rows[0]["PASSWORD"], password))):
            message = 'Error validating user'
            return render_template("error.html", message = message)
 
        # Remember which user has logged in
        session["user_id"] = rows[0]["USER_ID"]
        db.connection.commit()
        cursor.close()
        g.current_user_id = session['user_id']

        # Redirect user to home page
        return redirect("/")
 
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
 
 
@app.route('/registration')
def registration():
    return render_template('registration.html')

@app.route('/user', defaults={'user_id': None})
@app.route('/user/<user_id>')
@login_required
def user(user_id):
    g.current_user_id = session['user_id']
    if user_id is None:
        user_id = session['user_id']
    userID = user_id
    print(userID)
    cursor = db.connection.cursor()
    cursor.execute('SELECT * FROM user WHERE USER_ID = %s', [userID])
    userDetails = cursor.fetchall()
    userDetails = userDetails[0]
    # print(userDetails)
    db.connection.commit()
    cursor.close()
    return render_template('user.html', user = userDetails)
 

@app.route('/register_user', methods=['POST', 'GET'])
def register_user():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)
        cursor = db.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE email = %s", email)
        duplicates = cursor.fetchall()
        if(len(duplicates) != 0):
            db.connection.commit()
            cursor.close()
            flash(u'User already exists', 'error')
            time.sleep(3)
            return redirect(request.url)
        cursor.execute('''INSERT INTO USER VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (auto, name, email, hashed_password, phone, 0, 0, None))
        db.connection.commit()
        cursor.close()
    else:
        return render_template('error.html', message = 'Unknown error occurred')
    flash('Registration successful!')
    time.sleep(3) 
    return render_template('login.html')
 
@app.route("/logout")
def logout():
    """Log user out"""
 
    # Forget any user_id
    session.clear()
 
    # Redirect user to login form
    return redirect("/")

 
@app.route('/results')
def results():
    g.current_user_id = session['user_id']
    return render_template('results.html')

@app.route('/create_album', methods=['POST', 'GET'])
@login_required
def create_album():
    g.current_user_id = session['user_id']
    if request.method=='POST':
        songs = request.form["song__name"]
        album_name = request.form["album__name"]
        genre = request.form["album__genre"]
        durations = request.form["song__durations"]
        album_year = datetime.date.today().strftime("%Y")
        songs = songs.splitlines()
        durations = durations.splitlines()
        cursor = db.connection.cursor()
        files = request.files.getlist('album__art')
        # !-----------
        image_file = []
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['ALBUM_ART_FOLDER'], filename))
                image_file.append(file)
        album_art = image_file[0]
        # !-----------
        user_id = session['user_id']
        # !---- ALBUM_ID, ALBUM_NAME, YEAR, USER_ID. GENRE, IMAGE
        insertQuery = '''INSERT INTO ALBUM VALUES (%s, %s, %s, %s, %s, %s)'''
        insertValues = (auto, album_name, album_year, user_id, genre, album_art)
        cursor.execute(insertQuery, insertValues)
        getLatestAlbumIdQuery = '''SELECT ALBUM_ID FROM ALBUM WHERE ALBUM_ID = (SELECT MAX(ALBUM_ID) FROM ALBUM)'''
        cursor.execute(getLatestAlbumIdQuery)
        album_id = cursor.fetchone()
        album_id = album_id['ALBUM_ID']
        # !---- SONG_ID, ALBUM_ID, SONG_NAME, DURATION
        for i in range(len(songs)):
            cursor.execute("INSERT INTO song VALUES (%s, %s, %s, %s)", (auto, album_id, songs[i], durations[i]))
        # !-----------------
        db.connection.commit()
        cursor.close()
        return redirect('/user')
    else:
        return render_template('create_album.html')

@app.route('/playlist')
def playlist():
    return render_template('playlist.html')

@app.route('/create_playlist', methods=['POST', 'GET'])
def create_playlist():
    g.current_user_id = session['user_id']
    if request.method=='POST':
        playlist_name = request.form["playlist__name"]
        playlist_year = datetime.date.today().strftime("%Y")
        cursor = db.connection.cursor()
        files = request.files.getlist('playlist__art')
        # !-----------
        image_file = []
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['PLAYLIST_ART_FOLDER'], filename))
                image_file.append(file)
        playlist_art = image_file[0]
        # !-----------
        user_id = session['user_id']
        # !--- Playlist ID, Playlist Name, Playlist Year, User ID, Playlist_Photo
        insertQuery = '''INSERT INTO PLAYLIST VALUES (%s, %s, %s, %s, %s)'''
        insertValues = (auto, playlist_name, playlist_year, user_id, playlist_art)
        cursor.execute(insertQuery, insertValues)
        db.connection.commit()
        cursor.close()
        return redirect('/user')
    return render_template('create_playlist.html')



# class USERS(db.Model):
#     user_id = db.Column(db.Integer, primary_key = True)
 
 
if __name__ == "__main__":
    app.run(debug=True)