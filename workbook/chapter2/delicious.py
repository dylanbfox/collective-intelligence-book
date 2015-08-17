class MockDeliciousAPI(object):

	def __init__(self, sample_size=50):

		def create_data(i):
			href = 'http://www.foo.com/' + str(i)
			user =  'user_' + str(i)
			return {'href': href, 'user': user}

		self.mock_popular_data = [create_data(i) for i in xrange(sample_size)]

	def get_popular(self, tag):
		"""
		Returns a list of the recent popular posts.

		Each dict in the response contains (at least) keys:
		* URL (href)
		* description (description)
		* user (user)
		"""
		return self.mock_popular_data

	def get_urlposts(href):
		"""
		Returns all the posts for a given URL
		"""