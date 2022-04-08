from enum import auto
from flask import Flask, flash, redirect, render_template, request, session
from flask.templating import render_template
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from helper import apology, login_required
from tempfile import mkdtemp
 
 
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
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'dbms'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'dbms_proj'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
 
db = MySQL(app)
 
@app.route('/')
@login_required
def index():
    return render_template('home.html')
 
 
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
        # Redirect user to home page
        return redirect("/")
 
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
 
 
@app.route('/registration')
def registration():
    return render_template('registration.html')
 
 
@app.route('/register_user', methods=['POST', 'GET'])
def register_user():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)
        print(name)
        print(phone)
        print(email)
        print(password)
        print(hashed_password)
        # TODO: write logic for updating user DB with user details
        cursor = db.connection.cursor()
        cursor.execute('''INSERT INTO USER VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (auto, name, email, hashed_password, phone, 0, 0, None))
        db.connection.commit()
        cursor.close()
    else:
        return render_template('error.html')
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
    return render_template('results.html')
 
# class USERS(db.Model):
#     user_id = db.Column(db.Integer, primary_key = True)
 
 
if __name__ == "__main__":
    app.run(debug=True)