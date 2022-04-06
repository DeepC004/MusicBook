from enum import auto
from flask import Flask, request
from flask.templating import render_template
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'dbms'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'dbms_proj'

db = MySQL(app)

@app.route('/')
def login():
    return render_template('login.html')


@app.route('/login_validate', methods=['POST', 'GET'])
def form():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # TODO: VALIDATION LOGIC
    return


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

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/results')
def results():
    return render_template('results.html')

# class USERS(db.Model):
#     user_id = db.Column(db.Integer, primary_key = True)


if __name__ == "__main__":
    app.run(debug=True)
