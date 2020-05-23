import os

from flask import Flask, session, render_template, request, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, get_reviews
from models.books import Books
from models.defaultbooks import Defbooks
from models.reviews import Review
import requests



app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



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



@app.route("/", methods = ['GET', 'POST'])
@login_required
def index():
    if request.method == 'GET':
        return render_template("index.html")

    else:
        title = request.form['title']
        author = request.form['author']
        isbn  = request.form['isbn']
        row = None
        books = list()
       
        if not title.strip() and not author.strip() and not isbn.strip():
            return render_template('error.html', error = 'You must at least provide one info', direction = '/')
        elif title.strip():
            row = db.execute("select author, title, isbn from books where title like :title or title like :xtitle",{'title':"%"+title+"%", 'xtitle':"%" +title.swapcase()+"%"}).fetchall()
        elif author.strip():
            row = db.execute("select author, title, isbn from books where author like :author or author like :xauthor",{'author':"%"+author+"%",'xauthor':"%" + author.swapcase() + "%"}).fetchall()
        elif isbn.strip():
            row = db.execute("select author, title, isbn from books where isbn like :isbn",{'isbn':"%"+isbn+"%"}).fetchall()

        if not row == None:    
            for i in range(len(row)):
                oneBook = Defbooks(
                    row[i]['author'],
                    row[i]['title'],
                    row[i]['isbn']
                )
                books.append(oneBook)

        return render_template("result.html", books=books)

        
    return render_template("result.html")




@app.route('/bookdetails/<string:book_isbn>', methods=['GET','POST'])
def bookdetails(book_isbn):

    if request.method == 'POST':
        row = db.execute("select id from books where isbn = :isbn ",{'isbn':book_isbn}).fetchone()
        book_id = row[0]
        rating = request.form['rate']
        review = request.form['review']
        print(rating)
        print(review)
        if rating == None or not review.strip():
            return render_template('error.html',error="you must provide both rate and review !", direction = "/bookpage")
        
        else:
            try:
                db.execute('insert into reviews(bookid,userid,review,rating) VALUES(:book_id,:user_id,:review,:rating)',
                {'book_id':book_id,'user_id':session['user_id'],'review':review,'rating':rating}
                )
                db.commit()
                return redirect(request.referrer)
            except:
                return render_template("error.html",error="you already made a review on this book", direction="/bookpage")  
    else:                
        try:
            book = db.execute("select * from books where isbn = :isbn", {'isbn':book_isbn}).fetchone()
        except:
            return render_template("error.html", error="error fetching data",direction="/bookpage")    
        oneBook = Books(
            int(book['id']),
            book['author'],
            book['title'],
            book_isbn,
            book['year']
        )
        
        greview = get_reviews(book_isbn)
        print(greview)
        return render_template("bookdetails.html", book=book,greview=greview)


@app.route('/bookpage')
@login_required
def bookpage():
    row = None
    books = list()
    try:
        row =  db.execute("select isbn, title, author from books limit 300").fetchall()
        for i in range (len(row)):
            oneBook = Defbooks(
                row[i]['author'],
                row[i]['title'],
                row[i]['isbn'],
                )
            books.append(oneBook)
    except ValueError as e:
        return render_template("error.html",error="error while fetching data", direction = "/")

    return render_template("bookpage.html", books=books)



@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template("login.html")
    
    else:
        session.clear()    
        username = request.form['username']
        password = request.form['password']
        row = db.execute("Select id, username, hash from users where username = :username", {'username':username}).fetchone()
        if not username.strip():
            return render_template('error.html',error='Username cannot be empty!', direction='/login')
        elif not password.strip():
            return render_template('error.html',error='Password cannot be empty!', direction='/login')
        elif row == None or not check_password_hash(row[2], password):
            return render_template('error.html',error='wrong password or username', direction='/login')
        
        session['user_id'] = row[0]
        print('###logged in', row[0])

        return redirect('/')





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


    

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
