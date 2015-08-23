import feedparser
import random
import re

# Returns title and dictionary of word counts for an RSS feed
def getwordcounts(url):
	# Parse the feed
	document = feedparser.parse(url)
	wordcount = {}

	# Loop over all the entries
	for entry in document.entries:
		if 'summary' in entry:
			summary = entry.summary
		else:
			summary = entry.description


		# extract a list of words for the entry
		words = getwords(entry.title+' '+summary)
		for word in words:
			wordcount.setdefault(word, 0)
			wordcount[word] += 1

	title_details = document['feed'].get('title_detail', None)

	if title_details is None:
		title = 'Untitled_%s' % str(random.randint(0, 100))
	else:
		title = title_details.get('value', 'Untitled_%s' % str(random.randint(0, 100)))

	return title, wordcount

def getwords(html):
	# Remove all the HTML
	txt = re.compile(r'<[^>]+>').sub('', html)

	# Split words by non-alpha numberic chars
	words = re.compile(r'[^A-Z^a-z]+').split(txt)

	# Convert to lowercase
	return [w.lower() for w in words if w]

word_appeared_count = {}
blog_word_counts = {}
feedlist = []

for feedurl in file('feedlist.txt'):
	feedlist.append(feedurl)

	# get the wordcount for the each individual blog
	title, wordcount = getwordcounts(feedurl)
	blog_word_counts[title] = wordcount

	# keep track of how often a word appears
	# in all the blogs. the count here is
	# per blog. eg, if 'the' is in 2 blogs 100 times,
	# the count will be 2.
	for word, count in wordcount.items():
		word_appeared_count.setdefault(word, 0)
		if count > 1:
			word_appeared_count[word] += 1

# only do clustering based off words that are
# popular enough (> 0.1) but not too popular (< 0.5)
# between all the blogs we looked at
wordlist = []
for word, appeard_count in word_appeared_count.items():
	fraction = float(appeard_count) / len(feedlist)
	if fraction > 0.1 and fraction < 0.5:
		wordlist.append(word)

# output data to file
out = file('blogdata.txt' ,'w')
out.write('Blog')

for word in wordlist:
	out.write('\t%s' % word)

out.write('\n')
for blog, wordcount in blog_word_counts.items():
	print blog, type(blog)
	blog = blog.encode('ascii', 'ignore')
	out.write(blog)
	for word in wordlist:
		if word in wordcount:
			out.write('\t%d' % wordcount[word])
		else:
			out.write('\t0')
	out.write('\n')




