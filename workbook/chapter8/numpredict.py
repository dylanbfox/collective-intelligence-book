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