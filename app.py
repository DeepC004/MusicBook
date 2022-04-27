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

USER_PHOTO_FOLDER = 'static/images/user'
app.config["USER_PHOTO_FOLDER"] = USER_PHOTO_FOLDER

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
    for i in range(len(top_artists)):
        if (top_artists[i]['USER_PHOTO'] is not None):
            imageFile = top_artists[i]['USER_PHOTO'].decode('UTF-8')
            fileName = imageFile.split(' ')
            filename = fileName[1]
            fileName = 'images/user/' + filename.strip("'")
            imageInfo = url_for('static', filename = fileName)
            top_artists[i]['USER_PHOTO'] = imageInfo
    print('\n\nTOP ARTISTS: ', top_artists)

    latestSongsQuery = '''SELECT * FROM ALBUM ORDER BY ALBUM_ID DESC LIMIT 7'''
    cursor.execute(latestSongsQuery)
    latestAlbums = cursor.fetchall()
    print('\n\nLatest Albums: ', latestAlbums)
    latest_albums = []
    for i in range(len(latestAlbums)):
        latest_albums.append(latestAlbums[i])
    for i in range(len(latestAlbums)):
        imageFile = latest_albums[i]['ALBUM_PHOTO'].decode('UTF-8')
        fileName = imageFile.split(' ')
        filename = fileName[1]
        fileName = 'images/album/' + filename.strip("'")
        imageInfo = url_for('static', filename = fileName)
        latest_albums[i]['ALBUM_PHOTO'] = imageInfo

    print('\n\nLatest Albums: ', latestAlbums)

    playlistQuery = '''SELECT * FROM PLAYLIST WHERE USER_ID = %s ORDER BY PLAYLIST_ID ASC LIMIT 3'''
    playlistValues = [session['user_id']]
    cursor.execute(playlistQuery, playlistValues)
    quickAccess = cursor.fetchall()
    print('\n\nQuick Access: ', quickAccess)

    quick_access = []
    for i in range(len(quickAccess)):
        quick_access.append(quickAccess[i])
    for i in range(len(quickAccess)):
        if (quick_access[i]['PLAYLIST_PHOTO'] is not None):
            imageFile = quick_access[i]['PLAYLIST_PHOTO'].decode('UTF-8')
            fileName = imageFile.split(' ')
            filename = fileName[1]
            fileName = 'images/playlist/' + filename.strip("'")
            imageInfo = url_for('static', filename = fileName)
            quick_access[i]['PLAYLIST_PHOTO'] = imageInfo

    print('\n\nquick acess modified: ', quick_access)


    latestSongsQuery = '''SELECT S.SONG_NAME song_name, A.ALBUM_NAME album_name, A.ALBUM_ID album_id FROM SONG S INNER JOIN ALBUM A ON S.ALBUM_ID = A.ALBUM_ID ORDER BY S.SONG_ID DESC LIMIT 7'''
    cursor.execute(latestSongsQuery)
    latestSongs = cursor.fetchall()
    print('\n\nLatest Songs: ', latestSongs)


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
            # album_list = []
            # for i in range(len_songs):
            #     album_list.append(albums[i])
            joinTablesQuery = '''SELECT S.SONG_NAME song, S.SONG_ID song_id, A.ALBUM_NAME album, A.ALBUM_ID album_id, A.ALBUM_PHOTO album_art, U.NAME user, U.USER_ID id FROM SONG S INNER JOIN ALBUM A ON S.ALBUM_ID = A.ALBUM_ID INNER  JOIN USER U ON A.USER_ID = U.USER_ID WHERE S.SONG_NAME LIKE %s OR A.ALBUM_NAME LIKE %s OR U.NAME LIKE %s'''
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
            cursor.execute("SELECT * FROM PLAYLIST WHERE user_id=%s", [session['user_id']])
            current_playlists=cursor.fetchall()
            db.connection.commit()
            cursor.close()
            print('\n\n Current Playlists: \n', current_playlists)
            current_playlists_array = []
            for pl in current_playlists:
                current_playlists_array.append(pl)
            print('\n\n Current Playlists Array: \n', current_playlists_array)
            return render_template('results.html', results = results, current_playlists=current_playlists_array)
        else:
            return render_template('error.html')
    else:
        return render_template('home.html', top_artists = top_artists, quick_access = quick_access, latest_albums = latest_albums, latest_songs = latestSongs)

 
 
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
    current_user_id = session['user_id']
    if user_id is None:
        user_id = session['user_id']
    userID = user_id
    # print(userID)
    cursor = db.connection.cursor()
    cursor.execute('SELECT * FROM USER WHERE USER_ID = %s', [userID])
    userDetails = cursor.fetchall()
    # print(userDetails)
    userDetails = userDetails[0]
    print('\n\nUser Details: ', userDetails)
    searchQuery = '''SELECT * FROM PLAYLIST WHERE USER_ID = %s'''
    cursor.execute(searchQuery, [userID])
    playlists = cursor.fetchall()
    # print(playlists)
    results = []
    for i in range(len(playlists)):
        results.append(playlists[i])
    print('\n\nRESULTS: ', results)
    for i in range(len(playlists)):
        if (results[i]['PLAYLIST_PHOTO'] is not None):
            imageFile = results[i]['PLAYLIST_PHOTO'].decode('UTF-8')
            fileName = imageFile.split(' ')
            filename = fileName[1]
            fileName = 'images/playlist/' + filename.strip("'")
            imageInfo = url_for('static', filename = fileName)
            results[i]['PLAYLIST_PHOTO'] = imageInfo
    userResults = []
    userResults.append(userDetails)
    print('USER RESULTS:\n\n', userResults)
    if (userResults[0]['USER_PHOTO'] is not None):
        for i in range(len(userResults)):
            imageFile = userResults[i]['USER_PHOTO'].decode('UTF-8')
            fileName = imageFile.split(' ')
            filename = fileName[1]
            fileName = 'images/user/' + filename.strip("'")
            imageInfo = url_for('static', filename = fileName)
            userResults[i]['USER_PHOTO'] = imageInfo
    userResults = userResults[0]
    print('\n\nUser Results: ', userResults)
    # *-------------- SONGS QUERY -----------------------
    songsQuery = '''SELECT COUNT(*) song_count FROM SONG S INNER JOIN ALBUM A ON A.ALBUM_ID = S.ALBUM_ID INNER JOIN USER U ON A.USER_ID = U.USER_ID WHERE U.USER_ID = %s'''
    cursor.execute(songsQuery, [userID])
    songs = cursor.fetchall()
    # print(songs)
    # print(songs[0]['song_count'])
    # song_count = songs[0]['song_count']
    followQuery = '''SELECT * FROM FOLLOWS WHERE FOLLOWER_ID = %s AND FOLLOWING_ID = %s'''
    followValues = (current_user_id, userID)
    cursor.execute(followQuery, followValues)
    follows = cursor.fetchall()

    albumQuery = '''SELECT * FROM ALBUM WHERE USER_ID = %s'''
    cursor.execute(albumQuery, [userID])
    user_albums = cursor.fetchall()
    print(user_albums)

    album_results = []
    for i in range(len(user_albums)):
        album_results.append(user_albums[i])
    print('\n\nRESULTS: ', album_results)
    for i in range(len(user_albums)):
        if (album_results[i]['ALBUM_PHOTO'] is not None):
            imageFile = album_results[i]['ALBUM_PHOTO'].decode('UTF-8')
            fileName = imageFile.split(' ')
            filename = fileName[1]
            fileName = 'images/album/' + filename.strip("'")
            imageInfo = url_for('static', filename = fileName)
            album_results[i]['ALBUM_PHOTO'] = imageInfo


    db.connection.commit()
    cursor.close()
    return render_template('user.html', user = userResults, follows = follows, playlists = results, song_count = songs[0]['song_count'], current_user_id = current_user_id, albums = album_results)
 
@app.route('/upload_profile_photo', methods=['POST', 'GET'])
def upload_profile_photo():
    if request.method == 'POST':
        cursor = db.connection.cursor()
        files = request.files.getlist('user_photo')
        image_file = []
        for file in files:
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['USER_PHOTO_FOLDER'], filename))
                image_file.append(file)
        user_photo = image_file[0]
        print('\n\nUser photo: \n\n', user_photo)
        user_id = session['user_id']
        updateQuery = '''UPDATE USER SET USER_PHOTO = %s WHERE USER_ID = %s'''
        insertValues = (user_photo, user_id)
        cursor.execute(updateQuery, insertValues)
        db.connection.commit()
        cursor.close()
    return redirect('/user')

@app.route('/follow_request', methods=['POST', 'GET'])
def follow_request():
    if request.method == 'POST':
        follower_id = request.form.get('follower_id')
        following_id = request.form.get('following_id')
        print('\n\nFollow Request: \n\n', follower_id, following_id)
        # * ----- INSERTING  INTO DB -----
        """
        1) check if FOLLOWS playlist doesn't already contain the 
            follower : following pair
        2) If not => insert into DB
        3) else => remove from db since user wants to unfollow
        
        """
        insertValue = (follower_id, following_id)
        checkQuery = '''SELECT * FROM FOLLOWS WHERE FOLLOWER_ID = %s AND FOLLOWING_ID = %s'''
        cursor = db.connection.cursor()
        cursor.execute(checkQuery, insertValue)
        values = cursor.fetchall()
        print(values)
        print(len(values))
        if (len(values) == 0):
            insertQuery = '''INSERT INTO FOLLOWS VALUES (%s, %s)'''
            cursor.execute(insertQuery, insertValue)
            updateFollowerQuery = '''UPDATE USER SET FOLLOWERS = FOLLOWERS + 1 WHERE USER_ID = %s'''
            updateFollowingQuery = '''UPDATE USER SET FOLLOWING = FOLLOWING + 1 WHERE USER_ID = %s'''
            cursor.execute(updateFollowerQuery, [following_id])
            cursor.execute(updateFollowingQuery, [follower_id])
        else:
            removeQuery = '''DELETE FROM FOLLOWS WHERE FOLLOWER_ID = %s AND FOLLOWING_ID = %s'''
            cursor.execute(removeQuery, insertValue)
            updateFollowerQuery = '''UPDATE USER SET FOLLOWERS = FOLLOWERS - 1 WHERE USER_ID = %s'''
            updateFollowingQuery = '''UPDATE USER SET FOLLOWING = FOLLOWING - 1 WHERE USER_ID = %s'''
            cursor.execute(updateFollowerQuery, (following_id))
            cursor.execute(updateFollowingQuery, (follower_id))
        db.connection.commit()
        cursor.close()
    return redirect(f'/user/{following_id}')

@app.route('/register_user', methods=['POST', 'GET'])
def register_user():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)
        cursor = db.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE email = %s", [email])
        duplicates = cursor.fetchall()
        if(len(duplicates) != 0):
            db.connection.commit()
            cursor.close()
            flash(u'User already exists', 'error')
            return redirect(request.url)
        insertQuery = '''INSERT INTO USER VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
        insertValues = (auto, name, email, hashed_password, phone, 0, 0, None)
        cursor.execute(insertQuery, insertValues)
        # id, name, year, user_id, photo
        year = datetime.date.today().strftime("%Y")
        defaultPlaylistQuery = '''INSERT INTO PLAYLIST VALUES (%s, %s, %s, %s, %s)'''
        new_user_id = cursor.lastrowid
        playlistValues = (auto, 'Liked Songs', year, new_user_id, None)
        cursor.execute(defaultPlaylistQuery, playlistValues)
        db.connection.commit()
        cursor.close()
    else:
        return render_template('error.html', message = 'Unknown error occurred')
    flash('Registration successful!')
    # time.sleep(3) 
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

@app.route('/album/<album_id>')
@login_required
def album(album_id):
    current_user_id = session['user_id']
    cursor = db.connection.cursor()
    selectQuery = '''SELECT S.SONG_NAME song_name, S.DURATION duration, A.ALBUM_NAME album_name, A.ALBUM_PHOTO album_art, U.NAME artist_name, U.USER_ID user_id FROM SONG S INNER JOIN ALBUM A ON S.ALBUM_ID = A.ALBUM_ID INNER JOIN USER U ON A.USER_ID = U.USER_ID WHERE A.ALBUM_ID = %s'''
    selectValues = [album_id]
    cursor.execute(selectQuery, selectValues)
    album_songs=cursor.fetchall()
    print('\n\nALBUM SONGS: ', album_songs)
    selectQuery = '''SELECT ALBUM_NAME FROM ALBUM WHERE ALBUM_ID=%s'''
    selectValues = [album_id]
    cursor.execute(selectQuery, selectValues)
    album_name = cursor.fetchone()
    print('\n\nALBUM NAME: ', album_name)
    results = []
    for i in range(len(album_songs)):
        results.append(album_songs[i])
    for i in range(len(album_songs)):
        imageFile = results[i]['album_art'].decode('UTF-8')
        fileName = imageFile.split(' ')
        filename = fileName[1]
        fileName = 'images/album/' + filename.strip("'")
        imageInfo = url_for('static', filename = fileName)
        results[i]['album_art'] = imageInfo
    db.connection.commit()
    cursor.close()
    return render_template('album.html', results = results, album_name=album_name)

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
            if (songs[i] != '' and durations[i] != ''):
                cursor.execute("INSERT INTO song VALUES (%s, %s, %s, %s)", (auto, album_id, songs[i], durations[i]))
        # !-----------------
        db.connection.commit()
        cursor.close()
        return redirect('/user')
    else:
        return render_template('create_album.html')

@app.route('/add_to_playlist', methods=['POST', 'GET'])
def addToPlaylist():
    if request.method=='POST':
        song_id = request.form['song__id']
        print('')
        playlist_name = request.form['playlist__name']
        user_id = session['user_id']
        cursor = db.connection.cursor()
        # !--- Playlist ID, Playlist Name, Playlist Year, User ID, Playlist_Photo
        cursor.execute("SELECT PLAYLIST_ID FROM PLAYLIST WHERE PLAYLIST_NAME=%s AND USER_ID=%s", (playlist_name, user_id))
        playlist_id=cursor.fetchall()
        toParse=playlist_id[0]["PLAYLIST_ID"]
        cursor.execute("SELECT * FROM PLAYLIST_HAS_SONGS WHERE PLAYLIST_ID= %s AND SONG_ID=%s", (toParse, song_id))
        playlistSongs = cursor.fetchall()
        print(playlistSongs)
        print('\n\nTO PARSE: ', toParse)
        print('\n\nSONG ID: ', song_id)
        if len(playlistSongs)==0 :
            cursor.execute("INSERT INTO PLAYLIST_HAS_SONGS VALUES (%s, %s)", (toParse, song_id))
            db.connection.commit()
            cursor.close()
        return redirect(f'playlist/{toParse}')
    else:
        return render_template('results.html')

@app.route('/playlist', defaults={'playlist_id': None})
@app.route('/playlist/<playlist_id>')
@login_required
def playlist(playlist_id):
    user_id = session['user_id']
    cursor = db.connection.cursor()
    if playlist_id is None:
        defaultPlaylistQuery = '''SELECT PLAYLIST_ID FROM PLAYLIST WHERE USER_ID = %s AND PLAYLIST_NAME = %s'''
        cursor.execute(defaultPlaylistQuery, [user_id, 'Liked Songs'])
        playlist = cursor.fetchall()
        print('\n\n PLAYLIST TESTING: ', playlist)
        # print(playlist[0]['PLAYLIST_ID'])
        playlist_id = playlist[0]['PLAYLIST_ID']
        # print(playlist_id)
    playlistQuery = '''SELECT * FROM PLAYLIST WHERE PLAYLIST_ID = %s'''
    cursor.execute(playlistQuery, [playlist_id])
    playlistDetails = cursor.fetchall()
    playlistDetails = playlistDetails[0]
    print(playlistDetails)
    selectQuery = '''SELECT S.SONG_NAME song_name, A.ALBUM_ID album_id, A.ALBUM_YEAR album_year, A.ALBUM_NAME album_name, A.ALBUM_PHOTO album_art, U.NAME artist_name, U.USER_ID artist_id FROM SONG S, ALBUM A, USER U WHERE S.ALBUM_ID = A.ALBUM_ID AND A.USER_ID = U.USER_ID AND S.SONG_ID IN (SELECT SONG_ID FROM PLAYLIST_HAS_SONGS WHERE PLAYLIST_ID=%s)'''
    selectValues = [playlist_id]
    cursor.execute(selectQuery, selectValues)
    playlist_songs=cursor.fetchall()
    results = []
    for i in range(len(playlist_songs)):
        results.append(playlist_songs[i])
    for i in range(len(playlist_songs)):
        imageFile = results[i]['album_art'].decode('UTF-8')
        fileName = imageFile.split(' ')
        filename = fileName[1]
        fileName = 'images/album/' + filename.strip("'")
        imageInfo = url_for('static', filename = fileName)
        results[i]['album_art'] = imageInfo
    playlistOwnerQuery = '''SELECT USER_ID FROM PLAYLIST WHERE PLAYLIST_ID = %s'''
    cursor.execute(playlistOwnerQuery, selectValues)
    playlist_owner = cursor.fetchall()
    playlist_owner = playlist_owner[0]
    print('\n\n Playlist Owner: ', playlist_owner)
    db.connection.commit()
    cursor.close()
    print(results)
    return render_template('playlist.html', playlist_id = playlist_id, results = results, playlist = playlistDetails, user_id = user_id, playlist_owner = playlist_owner)

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

@app.route('/delete_playlist', methods=['POST', 'GET'])
def delete_playlist():
    if request.method == 'POST':
        playlist_id = request.form['playlist_id']
        cursor = db.connection.cursor()
        deleteQuery = '''DELETE FROM PLAYLIST WHERE PLAYLIST_ID = %s'''
        cursor.execute(deleteQuery, [playlist_id])
        db.connection.commit()
        cursor.close()
    return redirect('/user')
 
if __name__ == "__main__":
    app.run(debug=True)