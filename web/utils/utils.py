from utils.countInversions import countInversions
from operator import itemgetter
from bs4 import BeautifulSoup
import requests

def get_movie_info(movie):
    '''
    Uses the OMDB API to get movie info from IMDb
    Returns genres, thumbnail and imdb link for a given movie
    '''
    movie_info = requests.get(
                "http://www.omdbapi.com/",
                params={
                    "t": movie,
                    "apikey": "4a83a64e"}).json()
    movie_genres = movie_info["Genre"].split(", ")
    movie_thumbnail = movie_info["Poster"]
    movie_link = movie_info["imdbID"]

    return (movie_genres, movie_thumbnail, movie_link)

def get_favorite_movies(users):
    '''
    Uses Web scraping with BeautifulSoup to get 
    the five favorite movies of each user on letterbox
    and builds a list with info from all of them 
    '''

    movies = []

    for user in users:

        # downloading user's letterbox page of top rated watched movies
        user_movies_page = requests.get(f"https://letterboxd.com/{user.get('letterbox')}/films/by/member-rating/")

        # using beautiful soap to parse the webpage
        soup = BeautifulSoup(user_movies_page.content, 'html.parser')

        # getting just the five movies names with the highest rating
        user_movies = soup.find_all('img', class_='image')[:5]
        
        for movie in user_movies:

            # the movie name is in the alt attribute 
            movie_name = movie.get('alt')

            # getting movie info from OMDB api
            movie_info = get_movie_info(movie_name)
            movies.append({"movie":movie_name, "genres":movie_info[0], "thumbnail": movie_info[1], "link":movie_info[2]})
    
    return movies

def get_best_matches(base_order,base_user,all_users):   
    '''
    Compares the user's preference with the preference of all other users
    Returns the five users with the least inversions compared to the user making the request
    '''
    results = []
    n = len(base_order)

    # calculating the maximum number of inversions
    max_inversions = n * (n - 1) / 2

    # iterating through every recorded user
    for user in all_users:

        user_letterbox = user["letterbox"]

        # skipping the user making the request, if he/she has previously been
        # registered
        if  user_letterbox == base_user:
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
    return sorted(results, key=itemgetter('score'), reverse=True)[:5] 