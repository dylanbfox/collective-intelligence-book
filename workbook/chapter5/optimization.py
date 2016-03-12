import time
import random
import math

people = [('Seymour', 'BOS'),
		  ('Franny', 'DAL'),
		  ('Zooey', 'CAK'),
		  ('Walt', 'MIA'),
		  ('Buddy', 'ORD'),
		  ('Les', 'OMA')]

destination = 'LGA'

def get_minutes(t):
	x = time.strptime(t, '%H:%M')
	return x[3] * 60 + x[4]

def print_schedule(r):
	for d in range(0, len(r)/2): # each person has 2 results (arrive + depart)
		name = people[d][0]
		origin = people[d][1]

		out = flights[(origin, destination)][r[2*d]]
		ret = flights[(origin, destination)][r[2*d+1]]

		print "%10s%10s %5s-%5s $%3s %5s-%5s $%3s" % (
			name, origin, out[0], out[1], out[2],
			ret[0], ret[1], ret[2])


def schedule_cost(sol):
	# sol == solution
	total_price = 0
	latest_arrival = 0
	earliest_dep = 24*60

	for d in range(len(sol)/2):
		# Get inbound and outbound flights
		origin = people[d][1]
		outbound = flights[(origin, destination)][int(sol[2*d])]
		returnf = flights[(origin, destination)][int(sol[2*d+1])]

		# total place is price of all outbound and return flights
		total_price += outbound[2]
		total_price += returnf[2]

		# track latest arrival and earliest departure
		if latest_arrival < get_minutes(outbound[1]):
			latest_arrival = get_minutes(outbound[1])

		if earliest_dep > get_minutes(returnf[0]):
			earliest_dep = earliest_dep = get_minutes(returnf[0])

	# every person must wait at the aiport until the last person arrives
	# they also must arrive at the same time and wait for their dep. flights
	total_wait = 0
	for d in range(len(sol)/2):
		origin = people[d][1]
		outbound = flights[(origin, destination)][int(sol[2*d])]
		returnf = flights[(origin, destination)][int(sol[2*d+1])]

		total_wait += latest_arrival - get_minutes(outbound[1])
		total_wait += get_minutes(returnf[0]) - earliest_dep


	# fee if return car later in day than
	# on day you rented it
	if earliest_dep > latest_arrival:
		total_price += 50

	total_cost = total_price + total_wait
	return total_cost

def random_optimize(domain, costf):
	best = 999999999
	bestr = None
	for i in range(10000):
		# create a random solution
		r = [random.randint(domain[i][0], domain[i][1]) 
			for i in range(len(domain))]

		# get its cost
		cost = costf(r)

		# compare it to the best one so far
		if cost < best:
			best = cost
			bestr = r

	return bestr

def annealing_optimize(domain, costf, T=10000.0, cool=0.95, step=1):
	# initialize the values randomly
	vec = [float(random.randint(domain[i][0], domain[i][1]))
		  for i in range(len(domain))]

	while T>0.1:
		# choose random index from vector
		i = random.randint(0, len(domain)-1)

		# choose a random direction to change it
		dir = step*(-1)**int(round(random.random()))

		# create a new list with one of the values changed

		vecb = vec[:] # copy current solution to work on
		vecb[i] += dir # change random index by 1 or -1

		# if change is less than MIN, make MIN
		if vecb[i] < domain[i][0]:
			vecb[i] = domain[i][0]

		# if change is greater than MAX, make MAX
		if vecb[i] > domain[i][1]:
			vecb[i] = domain[i][1]

		# calculate current cost and new cost
		ea = costf(vec)
		eb = costf(vecb)

		# is it better, or does it make the
		# probability cutoff?
		if eb < ea:
			vec = vecb
		else:
			p = pow(math.e, (-eb-ea)/T)
			if random.random() < p:
				vec = vecb

		# decrease the temp
		T = T*cool

	return vec


def genetic_optimze(domain, cstf, pop_size=50, step=1,
	mutprob=0.2, elite=0.2, maxiter=100):

	# mutation operation
	def mutate(vec):
		i = random.randint(0, len(domain)-1)
		# flip a coin AND if the value is greater
		# than the minimum allowed value, decrease
		# by 1
		if random.random() < 0.5 and vec[i] > domain[i][0]:
			return vec[0:i] + [vec[i] - step] + vec[i+1:]

		# otherwise if the value is less than the
		# max allowed value, increase by 1
		elif vec[i] < domain[i][1]:
			return vec[0:i] + [vec[i] + step] + vec[i+1:]

	# AKA breeding
	def crossover(r1, r2):
		i = random.randint(1, len(domain) - 2)
		return r1[0:i] + r2[i:]

	# build the initial population
	pop = []
	for i in range(popsize):
		vec = [random.randint(domain[i][0], domain[i][1])
			  for i in range(len(domain))]

		pop.append(vec)

	# how many winners from each generation
	topelite = int(elite*popsize)

	# main
	for i in range(maxiter):
		scores = [(costf(v), v) for v in pop]
		scores.sort()
		ranked = [v for (s,v) in scores]

		# start with pure winners
		pop = ranked[0:topelite]

		# add mutated and bred forms of the winners
		while len(pop) < popsize:
			if random.random() < mutprob:

				# mutation
				c = random.randint(0, topelite)
				pop.append(mutate(ranked[c]))

			else:

				# crossover
				c1 = random.randint(0, topelite)
				c2 = random.randint(0, topelite)
				pop.append(crossover(ranked[c1], ranked[c2]))

		# print current top score
		print scores[0][0]

	# return top score vector set
	return scores[0][1]


def hillclimb(domain, costf):
	# create random solution
	sol = [random.randint(domain[i][0], domain[i][1]) 
		  for i in range(len(domain))]


	while 1:

		# create list of neighboring solutions
		neighbors = []
		for j in range(len(domain)):

			# greater than min, room to drop down
			if sol[j] > domain[j][0]:
				neighbors.append(sol[0:j] + [sol[j]-1] + sol[j+1:])

			# less than max, room to go up
			if sol[j] < domain[j][1]:
				neighbors.append(sol[0:j] + [sol[j]+1] + sol[j+1:])


		# see what the best solution among the neighbors is
		current = costf(sol)
		best = current
		for j in range(len(neighbors)):
			cost = costf(neighbors[j])

			if cost < best:
				best = cost
				sol = neighbors[j]

		# no improvement
		if best == current:
			break

	return sol

###
flights = {}
for line in file('schedule.txt'):
	clean_line = line.strip()
	row = line.split(',')

	origin, dest, depart, arrive, price, = row
	flights.setdefault((origin, dest), [])

	# add flight info to list of possible flights
	flight = (depart, arrive, int(price))
	flights[(origin, dest)].append(flight)

