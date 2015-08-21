import random

class MockDeliciousAPI(object):

	def get_popular(self, tag):
		"""
		Returns a list of the recent popular posts.

		Each dict in the response contains (at least) keys:
		* URL (href)
		* description (description)
		* user (user)
		"""
		def create_data(i):
			href = 'http://www.foo.com/' + str(i)
			user =  'user_' + str(i)
			return {'href': href, 'user': user}

		mock_popular_data = [create_data(i) for i in xrange(50)]

		return mock_popular_data

	# def get_urlposts(href):
	# 	"""
	# 	Returns all the posts for a given URL. 
	# 	Returns last 30 people to post the link.
	# 	"""
	# 	mock_urlposts = [{'user': 'user_'+ str(random.randrange(0, 100))} for i in xrange(30)]
	# 	for i in xrange(30):
	# 		data = {'user': 'user_' + str(random.randrange(0, 100))}
	# 		if 
	# 	return mock_urlposts


	def get_userposts():
		"""
		Returns all the posts for a given user
		"""

def initialize_user_dict(tag, count=5):
	api = MockDeliciousAPI()
	user_dict = {}

	# get the top "count" popular posts
	popular_posts = api.get_popular(tag=tag)[:count]
	for popular_post in popular_posts:
		# find all users who posted this post
		post_url = popular_post['href']
		for _post in get_urlposts(post_url):
			user = _post['user']
			user_dict[user] = {}

	return user_dict