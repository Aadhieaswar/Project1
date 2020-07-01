import os

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests, json

app = Flask(__name__)

FLASK_DEBUG = True

FLASK_APP = 'applicset DATA_BASEation.py'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SECRET_KEY"] = "my secret key" #os.getenv("SECRET_KEY")


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup")
def sign():
    return render_template("signup.html")

@app.route("/login")
def log():
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html")

@app.route("/login/completelogin", methods=["POST", "GET"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")

    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).rowcount == 0:
        return render_template("error.html", message="please check your password and/or username")
    elif db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).rowcount == 1:
        session["user"] = username
        return render_template("success.html", nam2 = username)

@app.route("/signup/completesignup", methods=["POST", "GET"])
def signup():

    username = request.form.get("username")
    password = request.form.get("password")

    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 1:
        return render_template("index.html", message="Please enter a different username")
    elif (username == '' or password == ''):
        return render_template("index.html", message="Invalid form")

    session["user"] = username
    db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {"username": username, "password": password})
    db.commit()
    return render_template("success.html", nam2 = username)

@app.route("/back_to_search")
def returns():
    usurp = session["user"]
    return render_template("success.html", nam2=usurp)

@app.route("/search", methods=["POST", "GET"])
def search():

    key = request.form.get("key")

    String = f"SELECT * FROM books WHERE isbn LIKE '%{key}%' OR title LIKE '%{key}%' OR author LIKE '%{key}%' OR year LIKE '%{key}%'"

    if db.execute(String).rowcount == 0:
        return render_template("error.html", message = "Error 404 Not Found!")
    results = db.execute(String).fetchall()
    return render_template("results.html", results=results, nam3=session["user"])

class API:

    def __init__(self, isbn):
        self.isbn = isbn

    def apis(self):
        sell = self.isbn
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "TcXeSmEygfI5QyL1fMBhw", "isbns": sell})
        if res.status_code != 200:
            data = "N//A"
        data = res.json()
        numb = data['books'][0]["work_ratings_count"]
        return numb

    def apis1(self):
        sell = self.isbn
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "TcXeSmEygfI5QyL1fMBhw", "isbns": sell})
        if res.status_code != 200:
            data = "N//A"
        data = res.json()
        num = data['books'][0]["average_rating"]
        return num

@app.route("/review_for_<int:book_id>", methods=["GET", "POST"])
def review(book_id):

    star = request.form.get("star")
    review = request.form.get("review")
    result = db.execute("SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()

    f1 = API(isbn = result.isbn)
    numb = f1.apis()
    num = f1.apis1()

    revs = {
    'rating': None,
    'review': None
    }
    slide = db.execute("SELECT * FROM users WHERE username = :username", {"username": session["user"]}).fetchone()
    user_id = int(slide.id)

    if (review == None or star == None) and request.method == "POST":
        return render_template("error.html", message="Oops! you might have forgotten to enter a review and/or rating before submitting.")

    if request.method == "POST":
        db.execute("INSERT INTO reviews (review, rating, book_id, user_id) VALUES (:review, :star, :book_id, :user_id)", {"book_id": book_id, "user_id": user_id, "review": review, "star": star})
        db.commit()
        revs = {
        'rating': star,
        'review': review
        }
        return render_template("review.html", numb=numb, num=num, revs=revs, result=result, nam3=session["user"], dev="disabled", btn="button", msg="Sorry! Cannot add more than one review per book!")
    elif db.execute("SELECT * FROM reviews WHERE book_id = :book_id AND user_id = :user_id", {"book_id": book_id, "user_id": user_id}).rowcount == 1:
        revie = db.execute("SELECT * FROM reviews WHERE book_id = :book_id AND user_id = :user_id", {"book_id": book_id, "user_id": user_id}).fetchone()
        revs = {
        'rating': revie.rating,
        'review': revie.review
        }
        return render_template("review.html", numb=numb, num=num, revs=revs, result=result, nam3=session["user"], dev="disabled", btn="button", msg="Sorry! Cannot add more than one review per book!")
    return render_template("review.html", numb=numb, num=num, revs=revs, result=result, nam3=session["user"], dev=None, btn="submit", msg=" ")

@app.route("/api/<string:isbn>", methods=["POST", "GET"])
def api(isbn):

    appl = []

    if db.execute("SELECT * FROM books Where isbn = :isbn", {"isbn": isbn}).rowcount != 0:
        phase = db.execute("SELECT * FROM books Where isbn = :isbn", {"isbn": isbn}).fetchone()
        a = str(phase.isbn)
        b = str(phase.title)
        c = str(phase.author)
        d = str(phase.year)
        g = int(phase.id)
        review_count = db.execute("SELECT COUNT(review) FROM reviews WHERE book_id = :book_id", {"book_id": g}).fetchone()
        try:
            e = int(review_count[0])

        except:
            e = "None"
        average_rating = db.execute("SELECT AVG(rating) FROM reviews WHERE book_id = :book_id", {"book_id": g}).fetchone()
        try:
            f = int(average_rating[0])

        except:
            f = "None"
        grape = ({
        'title': b,
        'author': c,
        'year': d,
        'isbn': a,
        'review_count': e,
        'average_rating': f
        })
        appl.append(grape)
        resp = jsonify(appl)
        return resp
    return render_template("error.html", message="Error 404 Not Found. The isbn number you entered does not exist in our database")