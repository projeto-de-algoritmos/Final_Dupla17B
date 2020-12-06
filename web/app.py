from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask import request
from flask_pymongo import PyMongo
from flask import jsonify
from bs4 import BeautifulSoup
import requests
from utils.movies import get_best_matches
from utils.moviesGraph import MoviesGraph


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
    return jsonify(results)

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():


    best_matches = list(request.json['best_matches'])

    # movies_graph = {}
    # movies_list = []

    movies = []

    for user in best_matches:
        user_movies_page = requests.get(f"https://letterboxd.com/{user.get('letterbox')}/films/by/member-rating/")
        soup = BeautifulSoup(user_movies_page.content, 'html.parser')
        user_movies = soup.find_all('img', class_='image')[:5]
        
        for movie in user_movies:
            movie_name = movie.get('alt')
            movie_genres = requests.get(
                        "http://www.omdbapi.com/",
                        params={
                            "t": movie_name,
                            "apikey": "4a83a64e"}).json()
            movie_genres = movie_genres["Genre"].split(", ")
            movies.append({"movie":movie_name, "genres":movie_genres})




    user_movie = request.json['user_movie']
    movie_genres = requests.get(
                "http://www.omdbapi.com/",
                params={
                    "t": user_movie,
                    "apikey": "4a83a64e"}).json()
    movie_genres = movie_genres["Genre"].split(", ")

    movies.append({"movie":user_movie, "genres":movie_genres})

    
    movies_graph = MoviesGraph(movies) 
    recommendations = movies_graph.get_movie_recommendations(user_movie)
    # if user_movie not in movies_graph:
    #     movies_list.append(user_movie)
    #     movies_graph[user_movie] = []
    #     for genre in movie_genres:
    #         movies_graph[user_movie].append(genre)
    #         if genre not in movies_graph:
    #             #adiciona tag ao grafo
    #             movies_graph[genre] = [user_movie]
    #         else:
    #             #adiciona musica a tag
    #             movies_graph[genre].append(user_movie)

    # ------------------------------------------------------------


    return jsonify(recommendations)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
