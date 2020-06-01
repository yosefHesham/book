import os

from flask import Flask, session, render_template, request, redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, get_reviews
from models.books import Books
from models.defaultbooks import Defbooks
from models.reviews import Review
from models.user_reviews import UserReview
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


@app.route("/", methods=['GET', 'POST'])
# if the user is logged in this will be the index page
@login_required
def index():

    if request.method == 'GET':
        return render_template("index.html")

    else:
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        row = None
        books = list()

        # preventing user from typing spaces as an input
        if not title.strip() and not author.strip() and not isbn.strip():
            return render_template('error.html', error='You must at least provide one info', direction='/')

        # these conditions to specify which option the user choose to search with and the swapcase function to make it case insensitive
        elif title.strip():
            row = db.execute("select author, title, isbn from books where title like :title or title like :xtitle", {
                             'title': "%"+title+"%", 'xtitle': "%" + title.swapcase()+"%"}).fetchall()
        elif author.strip():
            row = db.execute("select author, title, isbn from books where author like :author or author like :xauthor", {
                             'author': "%"+author+"%", 'xauthor': "%" + author.swapcase() + "%"}).fetchall()
        elif isbn.strip():
            row = db.execute("select author, title, isbn from books where isbn like :isbn", {
                             'isbn': "%"+isbn+"%"}).fetchall()

        # if there are matching results it will append it to a list of Defbooks instance
        if not row == None:
            for i in range(len(row)):
                oneBook = Defbooks(
                    row[i]['author'],
                    row[i]['title'],
                    row[i]['isbn']
                )
                books.append(oneBook)

        return render_template("result.html", books=books)


@app.route('/bookdetails/<string:book_isbn>', methods=['GET', 'POST'])
def bookdetails(book_isbn):
    revs = list()

    # when the user is leaving a review about that specific book
    if request.method == 'POST':
        row = db.execute("select id from books where isbn = :isbn ", {
                         'isbn': book_isbn}).fetchone()
        book_id = row[0]
        rating = request.form['rate']
        review = request.form['review']

        # if the user entered an empty input he will be directed to the error page
        if rating == None or not review.strip():
            return render_template('error.html', error="you must provide both rate and review !", direction="/bookpage")

        # after validating the user input, it will be stored into the database and displayed
        else:
            try:
                db.execute('insert into reviews(bookid,userid,review,rating) VALUES(:book_id,:user_id,:review,:rating)',
                           {'book_id': book_id,
                               'user_id': session['user_id'], 'review': review, 'rating': rating}
                           )
                db.commit()
                return redirect(request.referrer)
            # expecting that the user would make a review more than once about the same book
            except:
                return render_template("error.html", error="you already made a review on this book", direction="/bookpage")

    # when the user is just requesting for the bookdetails page , the book info and it`s reviews will be displayed for him
    else:
        try:
            book = db.execute(
                "select * from books where isbn = :isbn", {'isbn': book_isbn}).fetchone()
        except:
            return render_template("error.html", error="error fetching data", direction="/bookpage")
        oneBook = Books(
            int(book['id']),
            book['author'],
            book['title'],
            book_isbn,
            book['year']
        )

        # getting any review about that book
        try:
            reviews = db.execute('Select rating, review, userid from reviews where bookid = :bookid', {
                                 'bookid': book.id}).fetchall()
        except:
            return render_template("error.html", error="error fetching data", direction="/bookpage")

        # parsing data to a list of UserReview instance
        for i in range(len(reviews)):
            # parsing the users who made the reviews
            user = db.execute('select username from users where id = :userid', {
                              'userid': reviews[i]['userid']}).fetchone()
            oneReview = UserReview(
                reviews[i]['review'],
                user['username'],
                reviews[i]['rating']
            )
            revs.append(oneReview)

        ## calling the function to get the data from goodreads api
        greview = get_reviews(book_isbn)
        return render_template("bookdetails.html", book=book, greview=greview, reviews=revs)



## this is an extra page and iam just displaying some random books for the user !
@app.route('/bookpage')
@login_required
def bookpage():
    row = None
    books = list()
    try:
        row = db.execute(
            "select isbn, title, author from books limit 300").fetchall()
        for i in range(len(row)):
            oneBook = Defbooks(
                row[i]['author'],
                row[i]['title'],
                row[i]['isbn'],
            )
            books.append(oneBook)
    except ValueError as e:
        return render_template("error.html", error="error while fetching data", direction="/")

    return render_template("bookpage.html", books=books)


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template("login.html")

    else:
        ## logging out any previous user for the same ip
        session.clear()
        username = request.form['username']
        password = request.form['password']

        ## checking if the username is existing
        row = db.execute("Select id, username, hash from users where username = :username", {
                         'username': username}).fetchone()
        if not username.strip():
            return render_template('error.html', error='Username cannot be empty!', direction='/login')
        elif not password.strip():
            return render_template('error.html', error='Password cannot be empty!', direction='/login')

        ## validating user password    
        elif row == None or not check_password_hash(row[2], password):
            return render_template('error.html', error='wrong password or username', direction='/login')

        ## remembering the user
        session['user_id'] = row[0]

        ## redirect to the index page
        return redirect('/')


@app.route('/register', methods=['GET', 'POST'])
def register():

    # if the user wanna sign up redirect him to this page
    if request.method == 'GET':
        return render_template("register.html")

    else:

        # storing form data into vatiables
        password = request.form['password']
        confirmPassword = request.form['confirm_password']
        username = request.form['username']

        # validating form fields
        if not password.strip():
            return render_template('error.html', error='Password cannot be empty !', direction='/register')
        elif not confirmPassword.strip():
            return render_template('error.html', error='Confirm password cannot be empty !', direction='/register')
        elif not username.strip():
            return render_template('error.html', error='Username Cannot be Empty !', direction='/register')
        elif password == confirmPassword and len(password) < 8 and len(confirmPassword) < 8:
            return render_template('error.html', error='Password must be more than 8 letters', direction='/register')
        elif password != confirmPassword:
            return render_template('error.html', error='Password does not match !', direction='/register')

        else:

            # hashing the password and validating the user name
            hash = generate_password_hash(password)
            try:
                db.execute("INSERT INTO users (username,hash) VALUES(:username, :hash)", {
                    "username": username, "hash": hash
                })
                user_id = db.execute("SELECT id FROM users WHERE username = :username", {
                                     "username": username}).fetchone()
                session['user_id'] = user_id[0]
                print('### new ###', user_id)
                db.commit()
            except:
                return render_template('error.html', error='username is already used', direction='/register')

        return render_template('index.html')


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/api/<string:book_isbn>")
def bookdata(book_isbn):
    book = db.execute("select * from books where isbn = :isbn",
                      {'isbn': book_isbn}).fetchone()
    if book == None:
        return "Book Not Found" + "    Error 404"

    greview = get_reviews(book_isbn)

    return jsonify(title=book['title'], author=book['author'], year=book['year'], isbn=book_isbn, review_count=greview.rating_count, average_rating=greview.average_rating)
