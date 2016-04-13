import math

from random import random, randint

def wineprice(rating, age):
	# if rating is 80, peak age is 30,
	# so lower the rating the lower the
	# peak age. higher the rating higher
	# the peak age is.	
	peak_age = rating - 50

	# calculate price based on 
	# rating and age

	# higher the rating, higher the 
	# initial price
	price = rating/2

	if age > peak_age:
		# past peak, goes bad in 5 years,
		# otherwise, price increases but
		# at smaller ad smaller increments
		# (4x,3x,2x,etc) until reach 5 years
		# past 
		price = price * (5 - (age-peak_age))

	else:
		# increases 5x original value as it
		# approaches its peak, otherwise
		# just the normal price
		price = price * (5 * (age+1)/peak_age)

	if price < 0:
		price = 0

	return price

def wineset1():
	rows = []
	for i in range(300):
		# create random age and rating
		rating = random() * 50 + 50
		age = random() * 50

		# get reference price
		price = wineprice(rating, age)

		# add some noise
		price *= (random() * 0.4 + 0.8)

		# add to the data set
		rows.append({
			'input': (rating, age),
			'result': price	
		})

	return rows

def euclidian(v1, v2):
	d = 0.0
	for i in range(len(v1)):
		d += (v1[i] - v2[i]) ** 2

	return math.sqrt(d)

def getdistances(data, vec1):
	"""
	Get distances between a given vector,
	vec1, and every item in the dataset.
	"""
	distancelist = []
	for i in range(len(data)):
		vec2 = data[i]['input']
		distancelist.append((euclidian(vec1, vec2), i))
	distancelist.sort()
	return distancelist

def kNNestimate(data, vec1, k=5):
	# get sorted distances
	dlist = getdistances(data, vec1)
	avg = 0.0

	# take the average of the top k results
	for i in range(k):
		idx = dlist[i][1]
		avg += data[idx]['result']

	avg = avg/k
	return avg

def weightedkNNestimate(data, vec1, k=5, weightf=gaussian):
	# get sorted distances
	dlist = getdistances(data, vec1)
	avg = 0.0
	totalweight = 0.0

	# get weighted average
	for i in range(k):
		dist = dlist[i][0]
		idx = dlist[i][1]

		weight = weightf(dist)
		avg += weight * data[idx]['result']
		totalweight += weight

	avg = avg/totalweight
	return avg

def inverseweight(dist, num=1.0, const=0.1):
	return num/(dist+const)

def subtractweight(dist, const=1.0):
	if dist > const:
		return 0

	else:
		return const - dist

def gaussian(dist, sigma=10.0):
	return math.e**(-dist**2/(2*sigma**2))


def dividedata(data, test=0.5):
	trainset = []
	testset = []

	for row in data:
		if random() < test:
			testset.append(row)
		else:
			trainset.append(row)

	return trainset, testset

def testalgorithm(algf, trainset, testset):
	error = 0.0
	for row in testset:
		# get distance between sample from test set
		# and all the samples in the train set and
		# make a prediction on the price using algf
		guess = algf(trainset, row['input'])

		# square error to widen difference between
		# small and large errors
		error += (row['result'] - guess)**2

	return error / len(testset)

def crossvalidate(algf, data, trials=100, test=0.05):
	error = 0.0
	for i in range(trials):
		trainset, testset = dividedata(data, test)
		error += testalgorithm(algf, trainset, testset)

	# get average of the error scores for
	# all the trials
	return error / trials 


















