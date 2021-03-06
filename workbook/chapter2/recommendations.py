# A dictionary of movie critics and their ratings of a small
# set of movies
critics={'Lisa Rose': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 
 'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 
 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 
 'You, Me and Dupree': 3.5}, 
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
 'Superman Returns': 3.5, 'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
 'The Night Listener': 4.5, 'Superman Returns': 4.0, 
 'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 
 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
 'You, Me and Dupree': 2.0}, 
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0}}

from math import sqrt

# Returns euclidian distance score for person 1 and 2
def sim_distance(ratings, person1, person2):
	# Get list of similary rated movies
	similar = {}
	for rating in ratings[person1]:
		if rating in ratings[person2]:
			similar[rating] = 1

	# if they have no ratings in common, return 0
	if len(similar) == 0:
		return 0

	# Add up squares of all differences (euclidian distance score)
	sum_of_squares = sum([pow(ratings[person1][rating] - ratings[person2][rating], 2) for rating in similar])

	return 1/(1+sqrt(sum_of_squares))

def sim_tanimoto_A(ratings, person1, person2):
    '''
    Return the Tanimoto score between two users. 

	No validation is performed except same
	length checks. It is assumed that
	the caller passes properly weighted data.
    '''

    # Create N-dimensonal vectors.
    # The two N-dimensional vectors (eg: critic or product)
    # to find the Tanimoto coefficient for. MUST be
    # of the same length    
    vec1 = ratings[person1]
    vec2 = ratings[person2]

    for rating in vec1.copy():
    	if rating not in vec2:
    		vec1.pop(rating, None)

    for rating in vec2.copy():
    	if rating not in vec1:
    		vec2.pop(rating, None)

    N = len(vec1)

    # make sure vectors are same length,
    # ie ... make sure the number of features
    # match. since we're comparing similarity, 
    # we need two vectors w/ the same features to
    # compare against each other
    assert N == len(vec2)

    v1v2, v1v1, v2v2 = 0., 0., 0.

    # remember, N is number of features
    for rating in vec1:
        v1v2 += vec1[rating] * vec2[rating]
        v1v1 += vec1[rating] * vec1[rating]
        v2v2 += vec2[rating] * vec2[rating]

    return v1v2 / (v1v1 + v2v2 - v1v2)

# returns pearson correlation coefficient for person 1 and 2
def sim_pearson(ratings, person1, person2):
	# get list of similarly rated movies
	similar = {}
	for rating in ratings[person1]:
		if rating in ratings[person2]:
			similar[rating] = 1

	# find number of similarly rated movies
	N = len(similar)

	# if they have no ratings in common, return 0
	if N == 0:
		return 0

	# Add up all ratings
	sum1 = sum([ratings[person1][rating] for rating in similar])
	sum2 = sum([ratings[person2][rating] for rating in similar])

	# sum up the squares of each rating
	sum1_sq = sum([pow(ratings[person1][rating], 2) for rating in similar])
	sum2_sq = sum([pow(ratings[person2][rating], 2) for rating in similar])

	# sum of the products
	sum_of_products = sum([ratings[person1][rating] * ratings[person2][rating] for rating in similar])

	# Calculate the pearson score
	numerator = sum_of_products - (sum1*sum2/N)
	denominator = sqrt((sum1_sq - pow(sum1, 2)/N) * (sum2_sq - pow(sum2, 2)/N))
	
	if denominator == 0:
		return 0

	score = numerator / denominator

	return score

def top_matches(ratings, person, n=5, algorithm=sim_pearson):
	scores = []

	for critic in ratings:

		# dont compare the person to himself
		if critic == person:
			continue

		# how similar is the person to each critic?
		# determine similarity score using above algorithms,
		# that look at all critics' movie ratings
		score = algorithm(ratings, person, critic)
		scores.append((score, critic))

	scores.sort()
	scores.reverse()
	return scores[:n]


def get_recommendations(ratings, person, algorithm=sim_pearson):
	"""
	User based filtering.

	How similar is User A to User X, Y, and Z?
	Use these similarity scores to figure out which
	movies to recommend, based off what User X, Y, and Z
	rated that User A hasn't seen yet.
	"""
	totals = {}
	similarity_sums = {}

	for critic in ratings:
		if critic == person:
			continue

		score = algorithm(ratings, person, critic)

		# ignore scores lower than 0
		if score <= 0:
			continue

		for rating in ratings[critic]:
			# only recommend movies I haven't seen yet
			if rating not in ratings[person] or ratings[person][rating] == 0:

				# update total similarity score for this movie (score  * rating (eg: 0.88 * 5))
				# . we keep a running tally of the total score * rating for each critic
				totals.setdefault(rating, 0)
				totals[rating] += ratings[critic][rating] * score

				# update sum of similarities for this movie
				similarity_sums.setdefault(rating, 0)
				similarity_sums[rating] += score

	# create normalized list
	rankings = [(total / similarity_sums[rating], rating) for rating, total in totals.items()]

	rankings.sort()
	rankings.reverse()
	return rankings

def get_recommended_items(ratings, similarity_set, user):
	"""
	Item based filtering.

	Given how similar Product A is to B, C, and D, 
	how likely is User A to purchase product B, C, or D.
	Or, what rating is User A likely to give to product B, C, or D.
	"""

	user_ratings = rating[user]
	scores = {}
	total_sim = {}

	# Loop over items rated by this user
	for (item, rating) in user_ratings.items():

		# loop over items similar to this one
		for (similarity, item2) in similarity_set[item]:

			# ignore if user already rated item
			if item2 in user_ratings:
				continue

			# Weighted sum of rating for item2 * similarity score to item
			# eg: 3.5 * 0.555 (if Phantom of Opera (item2) is 0.555 similar
			# to Superman (item), and Superman (item) received a 3.5 rating)
			scores.setdefault(item2, 0)
			scores[item2] += similarity * rating

			# sum of all the similarity scores of item2s compared to item
			total_sim[item2] += similarity

	# Divide each total score by total weight to get average
	rankings = [(score / total_sim[item], item) for item, score in scores.items()]

def load_movielens(path='data/movielens'):

	# Get movie (product) titles
	movies = {}
	for line in open(path+'/u.item'):
		(id, title) = line.split('|')[:2]
		movies[id] = title

	# Load data
	ratings = {}
	for line in open(path+'/u.data'):
		(user, movieid, rating, ts) = line.split('\t')
		ratings.setdefault(user, {})
		movie_title = movies[movieid]
		ratings[user][movie_title] = float(rating)

	return ratings



