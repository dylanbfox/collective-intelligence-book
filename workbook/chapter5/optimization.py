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

