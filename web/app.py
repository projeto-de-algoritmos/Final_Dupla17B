from flask import Flask, render_template
from flask import request, session
from flask import jsonify, send_file
from flask_bootstrap import Bootstrap
from flask_pymongo import PyMongo
from utils.utils import *
from utils.moviesGraph import MoviesGraph
from utils.graphImage import GraphImage
import json
import os

# The app key and database access should be secret
# but I will keep it here to simplify for anyone running the project

app = Flask(__name__)
app.secret_key = "This should be a secret"
bootstrap = Bootstrap(app)
app.config["MONGO_URI"] = "mongodb://paa:21milEmmEa57yKDx@paa-shard-00-00.se53e.mongodb.net:27017,paa-shard-00-01.se53e.mongodb.net:27017,paa-shard-00-02.se53e.mongodb.net:27017/movie_recommendation?ssl=true&replicaSet=atlas-10i7up-shard-0&authSource=admin&retryWrites=true&w=majority"
mongo = PyMongo(app)


@app.route('/')
def index():
    '''
    Home page. Has the genres sortable list 
    '''
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

    # base user preference
    base_order = list(request.json['user_preference'])

    # base user letterbox
    user_letterbox = request.json['user_letterbox']
    mongo.db.movie_recommendation.insert_one(
        {'letterbox': user_letterbox, "preference": base_order})
    return jsonify(success=True), 200


@app.route('/best_matches', methods=['POST'])
def best_matches():
    '''
    Page containing the requesting user's group
    of taste
    '''
    # base user preference
    base_order = list(request.json['user_preference'])

    # base user letterbox
    base_user_letterbox = request.json['user_letterbox']

    # user's info from the database
    all_users = mongo.db.movie_recommendation.find({}, {"_id": 0})

    # calculating the best matches for the base user
    results = get_best_matches(base_order,base_user_letterbox,all_users)

    # storing it in the session for later use
    session["best_matches"] = results
    return render_template('best_matches.html', results=results)

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    '''
    Page containing a list of recommended movies 
    for the user
    '''

    best_matches = session["best_matches"]

    # getting the five favorite movies of all users and their respective infos
    movies = get_favorite_movies(best_matches)

    # adding request user's movie, to be used as the base for the recommendation
    user_movie = request.form['user_movie']
    user_movie_info = get_movie_info(user_movie)

    movies.append({"movie":user_movie, "genres":user_movie_info[0], 
                        "thumbnail": user_movie_info[1], "link": user_movie_info[2]})

    # building the graph
    movies_graph = MoviesGraph(movies) 

    # geting the recommendation list
    recommendations = movies_graph.get_movie_recommendations(user_movie)
    
    # storing the adjacency list and names list for later use
    session["adjacency_list"] = movies_graph.get_movies_graph()
    session["movies_list"] = movies_graph.get_movies_list()


    return render_template('recommendations.html', recommendations=recommendations, 
                user_movie=user_movie)


@app.route('/render_graph_images/<layout>')
def render_graph_images(layout):
    '''
    Renders an image for a given graph
    Can be either in the default layout 
    or bipartide layout
    '''

    adjacency_list = session["adjacency_list"]
    movies_list = [movie[0] for movie in session["movies_list"]]


    if layout == "default":
        img = GraphImage(adjacency_list).render_graph_image()
    else:
        img = GraphImage(adjacency_list).render_bipartide_graph_image(movies_list)

    return send_file(img, mimetype='image/png')



@app.route('/view_graph_images/<layout>')
def view_graph_images(layout):
    '''
    Page containing the graph's images
    '''

    return render_template('view_graphs.html', layout=layout)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
