import urllib2
from bs4 import BeautifulSoup
from urlparse import urljoin

class Crawler(object):

	def __init__(self, dbname):
		pass

	def __del__(self):
		pass

	def db_commit(self):
		pass

	# aux function for getting an entry id and adding
	# it if it's not present
	def get_entry_id(self, table, field, value, createnew=True):
		return None

	# index an individual page
	def add_to_index(self, url, soup):
		print "Indexing %s" % url

	# extract text from HTML page
	def get_text_only(self, soup):
		return None

	# separate words by any non-whitespace char
	def separate_words(self, text):
		return None

	# return true if this url is already indexed
	def is_indexed(self, url):
		return False

	# add a link between two pages
	def add_link_ref(self, url_from, url_to, link_text):
		pass

	# starting with a list of pages, do a breadth
	# first search to the given depth, indexing pages
	# as we go
	def crawl(self, pages, depth=2):
		for i in range(depth):
			newpages = set()

			for page in pages:
				try:
					c = urllib2.urlopen(page)
				except:
					print "Could not open %s" % page
					continue

				soup = BeautifulSoup(c.read())
				self.add_to_index(page, soup)

				# get all the links on the page,
				# which'll eventually become the
				# pages we index
				
				links = soup('a')
				for link in links:
					if 'href' in dict(link.attrs):
						url = urljoin(page, link['href'])
						if url.find("'") != -1:
							continue

						url = url.split('#')[0] # remove any anchors
						if url[0:4] == 'http' and not self.is_indexed(url):
							newpages.add(url)

						link_text = self.get_text_only(link)
						self.add_link_ref(page, url, link_text)

				self.db_commit()

			pages = newpages

	# create the database tables
	def create_index_tables(self):
		pass