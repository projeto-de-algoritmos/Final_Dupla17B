from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from countInversions import countInversions
from flask import request
from flask_pymongo import PyMongo
from flask import jsonify
from operator import itemgetter


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
    user_name = request.json['user_name']
    user_contact = request.json['user_contact']
    mongo.db.users.insert_one(
        {'name': user_name, "preference": base_order, 'contact': user_contact})
    return jsonify(success=True), 200


@app.route('/get_best_matches', methods=['POST'])
def get_best_matches():
    '''
    Compares the user's preference with the preference of all other users
    Returns the five users with the least inversions compared to the user making the request
    '''
    base_order = list(request.json['user_preference'])
    base_user_name = request.json['user_name']

    all_users = mongo.db.users.find({}, {"_id": 0})

    results = []
    n = len(base_order)

    # calculating the maximum number of inversions
    max_inversions = n * (n - 1) / 2

    # iterating through every recorded user
    for user in all_users:

        user_name = user["name"]

        # skipping the user making the request, if he/she has previously been
        # registered
        if  user_name == base_user_name:
            continue

        user_contact = user["contact"]
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

        results.append({"name": user_name,
                        "score": score, "contact": user_contact})

    # Getting the five users with the biggest score
    results = sorted(results, key=itemgetter('score'), reverse=True)[:5]
    return render_template('best_matches.html', results=results)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
