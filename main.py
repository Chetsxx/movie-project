from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import json

MOVIE_API_URL = 'https://api.themoviedb.org/3/search/movie'
MOVIE_API_KEY = 'f3af71e9446429ac03ace9a78a9468ea'

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)


class Edit(FlaskForm):
    rating = StringField("Your Rating Out of 10 e.g. 7.5")
    review = StringField("Your Review")
    submit = SubmitField("Done")

class AddMovie(FlaskForm):
   title = StringField("Movie Title")
   submit = SubmitField("Add Movie")


# db.create_all()
#
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
#
# db.session.add(new_movie)
# db.session.commit()



@app.route("/")
def home():
    movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(movies)):
        movies[i].ranking = len(movies) - i
    db.session.commit()

    return render_template("index.html", all_movies=movies)

@app.route("/edit", methods=["POST", "GET"])
def edit():
    form = Edit()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    print(movie)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, movie=movie)

@app.route("/delete")
def delete():
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=["GET", "POST"])
def add():
    movie_form = AddMovie()
    if movie_form.validate_on_submit():
        movie_title = movie_form.title.data
        response = requests.get(MOVIE_API_URL, params={"api_key": MOVIE_API_KEY, "query": movie_title})
        data = response.json()['results']
        print(data)
        return render_template("select.html", data=data)
    return render_template("add.html", form=movie_form)

@app.route("/find", methods=["GET", "POST"])
def find():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        MOVIE_URL = f"https://api.themoviedb.org/3/movie/{movie_api_id}"
        IMAGE_URL = "https://image.tmdb.org/t/p/w500/"
        response = requests.get(MOVIE_URL, params={"api_key": MOVIE_API_KEY})
        data = response.json()
        print(data)
        new_movie = Movie(title=data["title"], year=data["release_date"].split("-")[0], description=data["overview"], img_url=f"{IMAGE_URL}{data['poster_path']}")
        db.session.add(new_movie)
        db.session.commit()

        return redirect(url_for("edit", id=new_movie.id))

if __name__ == '__main__':
    app.run(debug=True)
