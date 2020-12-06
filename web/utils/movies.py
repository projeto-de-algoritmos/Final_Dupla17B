from utils.countInversions import countInversions
from operator import itemgetter

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