from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask import request
from flask_pymongo import PyMongo
from flask import jsonify
from utils.movies import *
from utils.moviesGraph import MoviesGraph
import json

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


@app.route('/best_matches', methods=['POST'])
def best_matches():

    base_order = list(request.json['user_preference'])
    base_user_letterbox = request.json['user_letterbox']
    all_users = mongo.db.movie_recommendation.find({}, {"_id": 0})
    results = get_best_matches(base_order,base_user_letterbox,all_users)
    return render_template('best_matches.html', results=results)

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():


    best_matches = json.loads(request.form['results'].replace("\'", "\""))
    movies = get_favorite_movies(best_matches)

    user_movie = request.form['user_movie']
    user_movie_genres = get_movie_genres(user_movie)

    movies.append({"movie":user_movie, "genres":user_movie_genres})

    
    movies_graph = MoviesGraph(movies) 
    recommendations = movies_graph.get_movie_recommendations(user_movie)

    return render_template('recommendations.html', recommendations=recommendations, user_movie=user_movie)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
