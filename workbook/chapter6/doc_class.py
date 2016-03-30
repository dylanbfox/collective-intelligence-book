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

class Classifier(object):

	def __init__(self, get_features_method):
		# counts of feature/category combinations
		self.feature_counts = {}

		# counts of documents in each category
		self.category_counts = {}

		# feature extraction method
		self.get_features_method = get_features_method

		# thresholds
		self.thresholds = {}

	def set_threshold(self, category, threshold):
		self.thresholds[category] = threshold

	def get_threshold(self, category):
		if category not in self.thresholds:
			return 1.0

		return self.thresholds[category]

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
		"""
		Assumed probability (assumed_prob) is the probability
		of a feature of a feature when you have very little
		information about it.
		"""

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
		# and then we weight this probability down based off 
		# assumed_prob and get it closer to 0 or 1
		weighted_prob = ((weight * assumed_prob) + (total * basic_prob)) / (weight + total)
		return weighted_prob

class NaiveBayesClassifier(Classifier):
	"""
	Assume probability of an entire document
	given a classification. Assume probabilities
	of individual features are independent of one
	another.
	"""

	def doc_prob(self, item, category):
		"""
		Probability of Document given Category.

		P(Document | Category)

		Probability of seeing Document, given Category
		(ie: probability of data, given hypothesis)

		Done by summing all individual feature
		probabilities...

			ie, P(Word | Category) -> probability Word appears in Category

		...together to get an overall probability
		"""
		features = self.get_features_method(item)

		# multiply probabilities of all the features together
		prob = 1
		for f in features:
			prob *= self.weighted_prob(f, category, self.feature_prob)

		return prob

	def category_prob(self, item, category):
		"""
		Apply Bayes' Theorem to get

		P(Category | Document) = P(Document | Category) * P(Category)
		(ie: probablity of hypothesis, given the data)

		ie: given a specific document, calculate
		probability it fits into this category.
		"""

		# probability this Category is randomly chosen
		category_prob = self.get_category_items_count(category) / self.get_total_items_count()

		# probability that Document appears in Category, given Category 
		doc_prob = self.doc_prob(item, category)
		print "doc_prob: %s" % doc_prob
		print "bayes prob: %s" % (doc_prob * category_prob)
		return doc_prob * category_prob	

	def classify(self, item, default=None):
		max = 0.0
		probs = {}
		for category in self.get_categories():
			probs[category] = self.category_prob(item, category)
			if probs[category] > max:
				max = probs[category]
				best = category

		# make sure prob fo winner exceeds threshold
		for category in probs:
			if category == best:
				continue

			# any probablity * winner's threshold multipler
			# must be less than winner's confidence
			# eg, if 'A' has a threshold of 3, it must
			# be 3x as confident as the next best category
			# so if 'A' is 30 but the next best 'B' is 15,
			# 15 * 3 > 30 ... so the threshold is not met
			# and the label is returned as 'unknown'
			if probs[category] * self.get_threshold(best) > probs[best]:
				return default

		return best

def test_populate(classifier):
	classifier.train('Nobody owns the water.', 'good')
	classifier.train('the quick rabbit jumps fences', 'good')
	classifier.train('buy pharmaceuticals now', 'bad')
	classifier.train('make quick money at the online casino', 'bad')
	classifier.train('the quick brown fox jumps', 'good')

