import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from helpers import login_required

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


## api key :3ZdRtZuPYHNnTuIgTI7QHw

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")



# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "3ZdRtZuPYHNnTuIgTI7QHw", "isbns":"9781632168146"})
    print(res.json())
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template("login.html")
    
    else:

        username = request.form['name']
        password = request.form['password']
        
        if not username.strip():
            return render_template('error.html',error='Username cannot be empty!', direction='/login')
        elif not password.strip():
            return render_template('error.html',error='Password cannot be empty!', direction='/login')
                




@app.route('/register', methods = ['GET', 'POST'])
def register():

    ## if the user wanna sign up redirect him to this page
    if request.method == 'GET':
        return render_template("register.html")
        
    else:

        ## storing form data into vatiables
        password = request.form['password']
        confirmPassword = request.form['confirm_password']
        username = request.form['username']

        ## validating form fields
        if not password.strip():
            return render_template('error.html', error='Password cannot be empty !', direction = '/register')
        elif not confirmPassword.strip():
            return render_template('error.html', error='Confirm password cannot be empty !', direction = '/register')
        elif not username.strip():
            return render_template('error.html', error='Username Cannot be Empty !', direction = '/register')
        elif password == confirmPassword and len(password) < 8 and len(confirmPassword) < 8:
             return render_template('error.html', error='Password must be more than 8 letters', direction = '/register')
        elif password != confirmPassword:
            return render_template('error.html', error='Password does not match !', direction = '/register')
                

        else:

            ## hashing the password and making sure the the user name
            hash = generate_password_hash(password)
            try:
                db.execute("INSERT INTO users (username,hash) VALUES(:username, :hash)", {
                    "username":username, "hash":hash
                })
                user_id = db.execute("SELECT id FROM users WHERE username = :username", {"username": username}).fetchone()
                session['user_id'] = user_id[0]
                print('### new ###', user_id)
                db.commit()
            except:
                return render_template('error.html', error='username is already used', direction ='/register')    


        return render_template('index.html')


    

