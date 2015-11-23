import urllib2
import sqlite3
import re

from bs4 import BeautifulSoup
from urlparse import urljoin

ignore_words = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])

class Searcher(object):
	def __init__(self, dbname):
		self.con = sqlite3.connect(dbname)

	def __del__(self):
		self.con.close()

	def normalizescores(self, scores, smallIsBetter=False):
		"""
		Results in vals between 0 and 1
		"""
		vsmall = 0.00001 

		if smallIsBetter:
			minscore = min(scores.values())

			return dict([(u, float(minscore)/max(vsmall, l)) for
				(u, l) in scores.items()])

		else:
			maxscore = max(scores.values())

			if maxscore == 0:
				maxscore = vsmall

			return dict([(u, float(c)/maxscore) for 
				(u, c) in scores.items()])

	def pagerankscore(self, rows):
		pageranks = dict([(row[0], 
			self.con.execute("select score from pagerank where urlid=%d" 
				% row[0]).fetchone()[0]) for row in rows])

		maxrank = max(pageranks.values())
		normalizedscores = dict([(u, float(l)/maxrank) for (u,l) in
			pageranks.items()])

		return normalizedscores

	def frequencyscore(self, rows):
		counts = dict([(row[0], 0) for row in rows])

		for row in rows:
			counts[row[0]] += 1

		return self.normalizescores(counts)

	def locationscore(self, rows):
		locations = dict([(row[0], 1000000) for row in rows])

		for row in rows:
			loc = sum(row[1:])

			if loc < locations[row[0]]:
				locations[row[0]] = loc


		return self.normalizescores(locations, smallIsBetter=True)

	def distancescore(self, rows):
		# if there's only one word ,
		if len(rows[0]) <= 2:
			return dict([(row[0], 1.0) for row in rows])

		mindistance = dict([(row[0], 1000000) for row in rows])

		for row in rows:
			dist = sum([abs(row[i] - row[i-1]) for i in range(2, len(row))])

			if dist < mindistance[row[0]]:
				mindistance[row[0]] = dist

		return self.normalizescores(mindistance, smallIsBetter=True)

	def linktextscore(self, rows, wordids):
		linkscores = dict([(row[0], 0) for row in rows])

		for wordid in wordids:
			cur = self.con.execute(
				"select link.fromid, link.toid from linkwords, link where wordid=%d \
				and linkwords.linkid=link.rowid" % wordid)

			for (fromid, toid) in cur:
				if toid in linkscores:
					pr = self.con.execute("select score from \
						pagerank where urlid=%d" % fromid).fetchone()[0]

					linkscores[toid] += pr


		maxscore = max(linkscores.values())
		print maxscore
		normalizedscores = dict([(u, float(l)/maxscore) for (u, l)
			in linkscores.items()])

		return normalizedscores

	def getscoredlist(self, rows, wordids):
		totalscores = dict([(row[0], 0) for row in rows])

		weights = [(1.0, self.frequencyscore(rows)),
				   (1.0, self.locationscore(rows)),
				   (1.0, self.distancescore(rows)),
				   (1.0, self.pagerankscore(rows)),
				   (1.0, self.linktextscore(rows, wordids))]

		for (weight, scores) in weights:
			for url in totalscores:
				totalscores[url] += weight*scores[url]

		return totalscores

	def geturlname(self, id):
		return self.con.execute(
			"select url from urllist where rowid=%d" %id).fetchone()[0]

	def query(self, q):
		rows, wordids = self.get_matching_rows(q)
		scores = self.getscoredlist(rows, wordids)

		rankedscores = sorted([(score, url) for (url, score) in scores.items()], reverse=1)

		for (score, urlid) in rankedscores[0:15]:
			print "%f\t%s" % (score, self.geturlname(urlid))

	def get_matching_rows(self, q):
		# strings to build the query
		fieldlist = 'w0.urlid'
		tablelist = ''
		clauselist = ''
		wordids = []

		# split the words by spaces
		words = q.split(' ')
		tablenumber = 0

		for word in words:
			# Get the word ID
			wordrow = self.con.execute(
				"select rowid from wordlist where word='%s'" % word).fetchone()

			if wordrow != None:
				wordid = wordrow[0]
				wordids.append(wordid)
				if tablenumber > 0:
					tablelist += ','
					clauselist += ' and '
					clauselist += 'w%d.urlid=w%d.urlid and ' % (tablenumber-1, tablenumber)

				fieldlist += ',w%d.location' % tablenumber
				tablelist += 'wordlocation w%d' % tablenumber
				clauselist += 'w%d.wordid=%d' % (tablenumber, wordid)
				tablenumber += 1

		# create query from the separate words
		fullquery = "select %s from %s where %s" % (fieldlist, tablelist, clauselist)
		cur = self.con.execute(fullquery)
		rows = [row for row in cur]
		return rows, wordids

class Crawler(object):

	def __init__(self, dbname):
		self.con = sqlite3.connect(dbname)

	def __del__(self):
		self.con.close()

	def db_commit(self):
		self.con.commit()

	# aux function for getting an entry id and adding
	# it if it's not present
	def get_entry_id(self, table, field, value, createnew=True):
		cur = self.con.execute(
			"select rowid from %s where %s='%s'" % (table, field, value)
		)

		result = cur.fetchone()

		if result == None:
			cur = self.con.execute(
				"insert into %s (%s) values ('%s')" % (table, field, value)
			)

			return cur.lastrowid

		else:
			return result[0]

	# index an individual page
	def add_to_index(self, url, soup):
		if self.is_indexed(url):
			print "Skipping %s" % url
			return

		print "Indexing %s" % url

		# get individual words
		text = self.get_text_only(soup)
		words = self.separate_words(text)

		# get the url id
		urlid = self.get_entry_id('urllist', 'url', url)

		print "URL %s HAS %s WORDS" % (urlid, len(words))

		# link each word to this url
		for i in range(len(words)):
			word = words[i]

			if word in ignore_words:
				continue

			# makes an entry for the word if it doesnt exist, or gets
			# its ID if it already exists 
			wordid = self.get_entry_id('wordlist', 'word', word)

			# adds new wordlocation reference
			self.con.execute('insert into wordlocation(urlid, wordid, location) \
				values(%d, %d, %d)' % (urlid, wordid, i))

	# extract text from HTML page
	def get_text_only(self, soup):
		"""
		Returns a long string of all the text on the page.
		"""
		v = soup.string
		if v == None:
			c = soup.contents
			result_text = ''
			for t in c:
				subtext = self.get_text_only(t)
				result_text += subtext + '\n'
			return result_text
		else:
			return v.strip()

	# separate words by any non-whitespace char
	def separate_words(self, text):
		splitter = re.compile('\\W*')
		return [s.lower() for s in splitter.split(text) if s != '']

	# return true if this url is already indexed
	def is_indexed(self, url):
		u = self.con.execute(
			"select rowid from urllist where url='%s'" % url).fetchone()

		if u != None:
			# check if it has actually been crawled
			v = self.con.execute(
				"select * from wordlocation where urlid=%d" % u[0]).fetchone()
			if v != None:
				return True

		return False

	# add a link between two pages
	def add_link_ref(self, url_from, url_to, link_text):
		words = self.separate_words(link_text)
		fromid = self.get_entry_id('urllist', 'url', url_from)
		toid = self.get_entry_id('urllist', 'url', url_to)

		# cant link to itself
		if fromid == toid:
			return

		cur = self.con.execute("insert into link(fromid, toid) values (%d, %d)" %
			(fromid, toid))

		linkid = cur.lastrowid
		# store the words that were actually used in the link
		for word in words:
			if word in ignore_words:
				continue

			wordid = self.get_entry_id("wordlist", "word", word)

			self.con.execute("insert into linkwords(linkid, wordid) values (%d,%d)" %
				(linkid, wordid))

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

	def calculatepagerank(self, iterations=20):
		# clear out the current pagerank tables
		self.con.execute('drop table if exists pagerank')
		self.con.execute('create table pagerank(urlid primary key, score)')

		# init every url with a pagerank of 1
		self.con.execute('insert into pagerank select rowid, 1.0 from urllist')
		self.db_commit()

		for i in range(iterations):
			print "Iteration %d" % i
			for (urlid,) in self.con.execute('select rowid from urllist'):
				pr = 0.15

				# Loop thru all pages that link to this one
				for (linker, ) in self.con.execute(
					"select distinct fromid from link where toid=%d" % urlid):
					# get pagerank of linker
					linkingpr = self.con.execute(
						"select score from pagerank where urlid=%d" % linker).fetchone()[0]


					# get total number of links from linker
					linkingcount = self.con.execute(
						"select count(*) from link where fromid=%d" % linker).fetchone()[0]

					pr += 0.85 * (linkingpr / linkingcount)

				self.con.execute(
					"update pagerank set score=%f where urlid=%d" % (pr, urlid))

				self.db_commit()

	# create the database tables
	def create_index_tables(self):
		self.con.execute('create table urllist(url)')
		self.con.execute('create table wordlist(word)')
		self.con.execute('create table wordlocation(urlid, wordid, location)')
		self.con.execute('create table link(fromid integer, toid integer)')
		self.con.execute('create table linkwords(wordid, linkid)')
		self.con.execute('create index wordidx on wordlist(word)')
		self.con.execute('create index urlidx on urllist(url)')
		self.con.execute('create index wordurlidx on wordlocation(wordid)')
		self.con.execute('create index urltoidx on link(toid)')
		self.con.execute('create index urlfromidx on link(fromid)')
		self.db_commit()







