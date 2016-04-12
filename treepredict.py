my_data = [line.split('\t') for line in file('decision_tree_example.txt')]

class DecisionNode(object):

	def __init__(self, col=-1, value=None, results=None, 
				tb=None, fb=None):

		self.col = col
		self.value = value
		self.results = results
		self.tb = tb
		self.fb = fb

	# divides a set on a specific column. numeric
	# or nominal values
	def divide_set(rows, column, value):
		# function to tell if row is in
		# first group (true) or second group (false)
		split_function = None

		if isinstance(value, int) or isinstance(value, float):
			split_function = lambda row: row[column] >= value
		else:
			split_function = lambda row: row[column] == value

		# divide the rows into two sets and return them
		set1 = [row for row in rows if split_function(row)]
		set2 = [row for row in rows if not split_function(row)]
		return (set1, set2)

	# get list of counts for possible results
	# eg (Premium: 8, None: 20)
	def unique_counts(rows):
		results = {}
		for row in rows:
			r = row[len(row) - 1]
			if r not in results:
				results[r] = 0
			results[r] += 1

		return results