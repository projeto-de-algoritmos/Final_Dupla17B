from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from countInversions import countInversions
from flask import request
from flask_pymongo import PyMongo
from flask import jsonify
from operator import itemgetter
from bs4 import BeautifulSoup
import requests


app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config["MONGO_URI"] = "mongodb://paa:21milEmmEa57yKDx@paa-shard-00-00.se53e.mongodb.net:27017,paa-shard-00-01.se53e.mongodb.net:27017,paa-shard-00-02.se53e.mongodb.net:27017/movie_recommendation?ssl=true&replicaSet=atlas-10i7up-shard-0&authSource=admin&retryWrites=true&w=majority"
mongo = PyMongo(app)


@app.route('/')
def index():
    genres = [
        "Action",
        "Comedy",
        "Drama",
        "Fantasy",
        "Horror",
        "Mystery",
        "Romance",
        "Thriller",
        "Western"]
    return render_template('index.html', genres=genres)


@app.route('/record_user_preference', methods=['POST'])
def record_user_preference():
    '''
    Inserts a user and his/her respective preferences of movie genres
    '''
    base_order = list(request.json['user_preference'])
    user_letterbox = request.json['user_letterbox']
    mongo.db.movie_recommendation.insert_one(
        {'letterbox': user_letterbox, "preference": base_order})
    return jsonify(success=True), 200


@app.route('/get_best_matches', methods=['POST'])
def get_best_matches():
    '''
    Compares the user's preference with the preference of all other users
    Returns the five users with the least inversions compared to the user making the request
    '''
    base_order = list(request.json['user_preference'])
    base_user_letterbox = request.json['user_letterbox']

    all_users = mongo.db.movie_recommendation.find({}, {"_id": 0})

    results = []
    n = len(base_order)

    # calculating the maximum number of inversions
    max_inversions = n * (n - 1) / 2

    # iterating through every recorded user
    for user in all_users:

        user_letterbox = user["letterbox"]

        # skipping the user making the request, if he/she has previously been
        # registered
        if  user_letterbox == base_user_letterbox:
            continue

        user_preference = user["preference"]

        # building the array for the user in the current iteration based on the base_order.
        # For each genre we see what is its position in the base order and
        # append it to the array
        compared_user_preference = [
            base_order.index(genre) +
            1 for genre in user_preference]

        # Getting the number of inversions for the user in the current
        # iteration
        number_of_inversions = countInversions(compared_user_preference)[1]

        # Calculating the score of the user in the current iteration
        # That score represents how compatible the said user is with the user
        # making the request
        score = int(100 - ((number_of_inversions / max_inversions) * 100))

        results.append({"letterbox": user_letterbox, "score": score})

    # Getting the five users with the biggest score
    results = sorted(results, key=itemgetter('score'), reverse=True)[:5]

    # ---------------------------------------------------------------

    for user in results:
        user_movies_page = requests.get(f"https://letterboxd.com/{user.get('letterbox')}/films/by/member-rating/")
        soup = BeautifulSoup(user_movies_page.content, 'html.parser')
        user_movies = soup.find_all('img', class_='image')[:5]
        user["movies"] = []
        for movie in user_movies:
            movie_name = movie.get('alt')
            movie_genres = requests.get(
                        "http://www.omdbapi.com/",
                        params={
                            "t": movie_name,
                            "apikey": "4a83a64e"}).json()
            movie_genres = movie_genres["Genre"].split(", ")
            user["movies"].append({"name": movie_name, "genres": movie_genres})
        

    return render_template('result.html', results=results)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
