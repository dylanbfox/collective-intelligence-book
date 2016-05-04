class matchrow:

	def __init__(self, row, allnum=False):
		if allnum:
			self.data = [float(row[i]) for i in range(len(row) - 1)]
		else:
			self.data = row[0:len(row) - 1]

		# match is the label; which is in the 
		# last index of the row
		self.match = int(row[len(row) - 1])

def loadmatch(f, allnum=False):
	"""
	Creates a list of matchrow classes each
	containing the raw data and the match.

	Ie, the x and y values.
	"""
	rows = []
	for line in file(f):
		rows.append(matchrow(line.split(','), allnum))

	return rows

def lineartrain(rows):
	"""
	A linear classifier finds the average of all the 
	data in each class, and constructs a point that 
	represents the center of the class. It can then 
	classify new points by determining to which center 
	point they are closest.

	This method gets the average point for each class.
	"""

	averages = {}
	counts = {}

	# rows of matchrow classes
	for row in rows:
		# get class of this point
		cl = row.match

		averages.setdefault(cl, [0.0]*len(row.data))
		counts.setdefault(cl, 0)

		# add this point to the averages
		for i in range(len(row.data)):
			averages[cl][i] += float(row.data[i])

		# keep track of how many points in each class
		counts[cl] += 1

	# divide sums by counts to get averages
	for cl, avg in averages.items():
		for i in range(len(avg)):
			avg[i] /= counts[cl]


	return averages

def dotproduct(v1, v2):
	return sum([v1[i] * v2[i] for i in range(len(v1))])

def dpclassify(point, avgs):
	b = (dotproduct(avgs[1], avgs[1]) - dotproduct(avgs[0], avgs[0])) / 2
	y = dotproduct(point, avgs[0]) - dotproduct(point, avgs[1]) + b
	if y > 0:
		return 0
	else:
		return 1

def rbf(v1, v2, gamma=20):
	"""
	Radial basis function.

	- mapping function that returns what the
	  dot product of 2 vectors *would* have
	  been in a higher dimensional space

	- "kernel"
	"""
	dv = [v1[i] - v2[i] for i in range(len(v1))]
	l = veclength(dv)
	return math.e**(-gamma*l)

def nlclassify(point, rows, offset, gamma=10):
	"""
	Function to calculate distance from 1 point
	to the rest of the points in the higher dimensional
	space. 

	Don't have the actual vectors of the points in the
	higher dimensional space though. Only have what the
	dot product would have been between points in the
	higher dimensional space.

	Instead, we take the average of the "dot-products"
	for a point versus every other point in the set.
	Using the mapping function for the higher 
	dimensional space.

	Calculate the radial-basis function between
	the point and every other point in the class to
	get what the dot product for that point and
	every other point in the class *would* have
	been in a higher dimensional space. And then
	average the values.
	"""

	sum0 = 0.0
	sum1 = 0.0
	count0 = 0
	count1 = 0

	for row in rows:
		if row.match == 0:
			sum0 += rbf(point, row.data, gamma)
			count0 += 1
		else:
			sum1 += rbf(point, row.data, gamma)
			count1 += 1

	y = (1.0/count0) * sum0 - (1.0/count1) * sum1 + offset

	if y < 0:
		return 0
	else:
		return 1

def getoffset(rows, gamma=10):
	l0 = []
	l1 = []

	for row in rows:
		if row.match == 0:
			l0.append(row.data)

		else:
			l1.append(row.data)

	sum0 = sum(sum([rbf(v1,v2,gamma) for v1 in l0] for v2 in l0))
	sum1 = sum(sum([rbf(v1,v2,gamma) for v1 in l1] for v2 in l1))

	return (1.0/(len(l1)**2)) * sum1 - (1.0/(len(l0)**2)) * sum0
