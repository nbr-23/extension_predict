#app.py
from flask import Flask, request, session, redirect, url_for, render_template, flash
from flask_socketio import SocketIO, emit
import psycopg2
import psycopg2.extras
import re 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from matplotlib.figure import Figure
from flask import Response
import joblib
import io
import ephem
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from datetime import datetime
model = joblib.load('pro.joblib')

app = Flask(__name__)
socketio = SocketIO(app, logger=False, engineio_logger=False)
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['TESTING'] = True

#model = pickle.load(open("model.pkl", 'rb'))
app.secret_key = 'extension_version'


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
    if request.method == 'POST' and 'login' in request.form and 'password' in request.form:
        # Create variables for easy access
        customer = request.form['customer']
        login = request.form['login']
        password = request.form['password']


        _hashed_password = generate_password_hash(password)

        #Check if account exists using MySQL
        cursor.execute('SELECT * FROM customer WHERE login = %s', (login,))
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')

        elif not re.match(r'[A-Za-z0-9]+', login):
            flash('login must contain only characters and numbers!')
        elif not login or not password:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into customer table
            #cursor.execute("INSERT INTO customer (customer, login, password, ) VALUES (%s,%s,%s)", (customer, login, _hashed_password))
            add_costumer = ("INSERT INTO customer "
               "(customer, login, password) "
               "VALUES (%s, %s, %s)")
            cursor.execute(add_costumer,(customer, login, _hashed_password))
            conn.commit()
            flash('You have successfully registered!')
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



@app.route('/plot/<n>', methods=['GET', 'POST'])
def plot_png1(n):
    n = int(n)
    fig = create_figure1(n)
    output = io.BytesIO()
    #flash('You have successfully added data!')
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure1(n):
    fig = Figure()
    axis = fig.add_subplot(1,1,1)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    future = model.make_future_dataframe(periods=n)
    forecast60 = model.predict(future)
    for i in range(len(forecast60['yhat'])):
        add_costumer = ("INSERT INTO result "
               "( id_advertising, id_product, prediction_id, date, prediction)"
               "VALUES (%s, %s, %s,%s,%s)")
        cursor.execute(add_costumer,(1,1,1,str(forecast60['ds'][i]),str(forecast60['yhat'][i]) ))
        conn.commit()
    figTrH = model.plot(forecast60)
    return figTrH

@app.route('/predict_sales', methods=['GET', 'POST'])
def predict(): 
    #cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Check if user is loggedin
    if 'loggedin' in session:
        # Show the profile page with account info
        return render_template('predict.html', 
       data = [{'asin':'ASIN'}, {'asin': 'C00DL2DN30'}])
        
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))



if __name__ == "__main__":
    app.run(debug=True)