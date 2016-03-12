import re
import math

def get_words(doc):
	splitter = re.compile('\\W*')

	# split words by non-alpha chars
	# ignore words less than 2 chars and
	# greater than 20 chars
	words = [s.lower() for s in splitter.split(doc)
			if len(s) > 2 and len(s) < 20]

	# return unique set of words
	unique_words = dict([(w, 1) for w in words])

	return unique_words

class Classifier:

	def __init__(self, get_features_method, filename=None):
		# counts of feature/category combinations
		self.feature_counts = {}

		# counts of documents in each category
		self.category_counts = {}

		# feature extraction method
		self.get_features_method = get_features_method


	# increase count of a feature/category pair
	def increase_feature_count(self, feature, category):
		self.feature_counts.setdefault(feature, {})
		self.feature_counts[feature].setdefault(category, 0)
		self.feature_counts[feature][category] += 1

	# increase the count of a category
	def increase_category_count(self, category):
		self.category_counts.setdefault(category, 0)
		self.category_counts[category] += 1

	# get number of times a feature has appeared in a category
	def get_feature_category_count(self, feature, category):
		feature_exists = feature in self.feature_counts
		category_exists = category in self.feature_counts[feature]

		count = 0.0
		if feature_exists and category_exists:
			count = float(self.feature_counts[feature][category])

		return count

	# get number of items in a category
	def get_category_items_count(self, category):
		category_exists = category in self.category_counts
		
		count = 0
		if category_exists:
			count = float(self.category_counts[category])

		return count

	# get total number of items
	def get_total_items_count(self):
		"""
		Assumes each document only has 1 category.
		"""
		count = sum(self.category_counts.values())
		return count

	# get all categories
	def get_categories(self):
		return self.category_counts.keys()

	def train(self, item, category):
		features = self.get_features_method(item)

		# increment count for every feature with this category
		for f in features:
			self.increase_feature_count(f, category)

		# increment count for this category
		self.increase_category_count(category)

	def feature_prob(self, feature, category, debug=False):
		"""
		Returns feature probability for a specific 
		category.
		"""
		if self.get_category_items_count(category) == 0:
			return 0

		f_count = self.get_feature_category_count(feature, category) 
		c_count = self.get_category_items_count(category)
		prob = f_count / c_count

		if debug:
			print "%s (%s appearances in %s items)" % (prob, f_count, c_count)

		return prob

	def weighted_prob(self, feature, category, prob_func, 
					 weight=1.0, assumed_prob=0.5):

		# calculate the current probability of
		# feature X for category Y
		basic_prob = prob_func(feature, category)

		# count total number of times this feature
		# appeared in each category
		total = sum([self.get_feature_category_count(feature, c)
				 for c in self.get_categories()])

		# calculate the weighted average
		# basic_prob is what the actual ratio of 
		# feature_count/items is for a specific category
		# ... eg (1/1) for "money" appearing in 1 "bad" document
		# and then we weigh this down based off assumed_prob
		# and get it closer to 0 or 1
		weighted_prob = ((weight * assumed_prob) + (total * basic_prob)) / (weight + total)
		return weighted_prob

def test_populate(classifier):
	classifier.train('Nobody owns the water.', 'good')
	classifier.train('the quick rabbit jumps fences', 'good')
	classifier.train('buy pharmaceuticals now', 'bad')
	classifier.train('make quick money at the online casino', 'bad')
	classifier.train('the quick brown fox jumps', 'good')

