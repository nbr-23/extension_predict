import pickle
import re
import psycopg2  # pip install psycopg2
import psycopg2.extras
from flask import Flask, request, session, redirect, url_for, render_template, flash
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'extension_version'
#model = pickle.load(open("model.pkl", 'rb'))

app.secret_key = 'extension_version'


DB_HOST = ""
DB_NAME = ""
DB_USER = ""
DB_PASS = ""
 
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

 

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,
                        password=DB_PASS, host=DB_HOST)


@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:

        # User is loggedin show them the home page
        return render_template('home.html')
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/login/', methods=['POST', 'GET'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if "login" and "password" POST requests exist (user submitted form)
    # HERE !! VERIFY ALL INPUT FORM -- 'login' in --> 'username' in
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        login = request.form['username']
        password = request.form['password']

        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM customer WHERE login = %s', (login,))
        # Fetch one record and return result
        account = cursor.fetchone()

        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in customer table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['login'] = account['login']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or login/password incorrect
                flash('Incorrect login/password')
        else:
            # Account doesnt exist or login/password incorrect
            flash('Incorrect login/password')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if "login", "password" POST requests exist (user submitted form)
    # HERE !! VERIFY ALL INPUT FORM -- 'login' in --> 'username' in && 'customer' in --> 'fullname' in
    if request.method == 'POST' and 'fullname' in request.form and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        login = request.form['username']
        customer = request.form['fullname']
        password = request.form['password']

        _hashed_password = generate_password_hash(password)
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM customer WHERE login = %s', (login,))
        account = cursor.fetchone()
        # print(account)
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')

        elif not re.match(r'[A-Za-z0-9]+', login):
            flash('login must contain only characters and numbers!')
        elif not login or not password:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into customer table
            cursor.execute("INSERT INTO customer (customer, login, password) VALUES (%s,%s,%s)",
                           (customer, login, _hashed_password,))
            conn.commit()
            flash('You have successfully registered!')
            return redirect(url_for('login'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('register.html')


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('login', None)
    # Redirect to login page
    return redirect(url_for('login'))

# ======================================================================================================
# ADDING THIS METHOD FOR UNITEST : NEED TO DELETE USER TEST IN DB FOR THE FOLLOWING TEST


@app.route("/delete", methods=["GET", "POST"])
def delete():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == "POST" and 'username' in request.form:
        cursor.execute('DELETE FROM customer WHERE login = %s',
                       (request.form["username"],))
        conn.commit()
        return redirect(url_for('login'))
    return redirect(url_for('login'))

# ========================================================================================================


@app.route('/predict_sales', methods=['GET', 'POST'])
def predict():
    #cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if user is loggedin
    if 'loggedin' in session:
        # Show the profile page with account info

        return render_template('predict.html', 
        data = [{'asin':'ASIN'}, {'asin': 'C00DL2DN30'}]
        )

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
