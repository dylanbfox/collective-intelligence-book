from PIL import Image, ImageDraw

class Bicluster(object):

	def __init__(self, vec, left=None, right=None,
		distance=0.0, id=None):

		self.left = left
		self.right = right
		self.vec = vec
		self.id = id
		self.distance = distance

def get_height(cluster):
	# Is this an endpoint? If so, height == 1
	if cluster.left == None and cluster.right == None:
		return 1

	# Otherwise, height == sum of heights of each branch
	return get_height(cluster.left) + get_height(cluster.right)

def get_depth(cluster):
	# the distance of an endpoint is 0.0
	if cluster.left == None and cluster.right == None:
		return 0

	# the distance of a branch is the greater of its two
	# sides plus its own distance
	return max(get_depth(cluster.left), get_depth(cluster.right)) + cluster.distance

def draw_dendrogram(cluster, labels, jpeg='clusters.jpg'):
	# height and width
	height = get_height(cluster) * 20
	width = 1200
	depth = get_depth(cluster)

	# width is fixed, so scale distances accordingly
	scaling = float(width - 150) / depth

	# create a new image with a white background
	img = Image.new('RGB', (width, height), 
		(255, 255, 255))
	draw = ImageDraw.Draw(img)

	draw.line( (0, height/2, 10, height/2), fill=(255, 0 , 0) )

	# Draw the first node
	draw_node(draw, cluster, 10, (height/2), scaling, labels)
	img.save(jpeg, 'JPEG')

def draw_node(draw, cluster, x, y, scaling, labels):
	if cluster.id < 0:
		h1 = get_height(cluster.left) * 20
		h2 = get_height(cluster.right) * 20
		top = y - (h1 + h2) / 2
		bottom = y + (h1 + h2) / 2

		# line length
		ll = cluster.distance * scaling

		# vertical line from this cluster to children
		draw.line((x, top+h1/2, x, bottom-h2/2), fill=(255, 0, 0))

		# horizontal line to left item
		draw.line((x, top+h1/2, x+ll, top+h1/2), fill=(255, 0, 0))

		# horizontal line to right item
		draw.line((x, bottom-h1/2, x+ll, bottom-h1/2), fill=(255, 0, 0))

		# draw left and right nodes
		draw_node(draw, cluster.left, x+ll, top+h1/2, scaling, labels)
		draw_node(draw, cluster.right, x+ll, bottom-h2/2, scaling, labels)

	else:
		# if this is an endpoint, draw the item label
		draw.text((x+5, y-7), labels[cluster.id], (0,0,0))


def readfile(filename):
	lines = [line for line in file(filename)]

	# First line is the column titles
	colnames = lines[0].strip().split('\t')[1:]
	rownames = [] # ie, blognames
	data = [] #list of lists. each list is counts of tokens for blog

	for line in lines[1:]:
		p = line.strip().split('\t') # p... real descriptive!

		# first column in each row is the rowname (ie, blogname)
		rownames.append(p[0])

		# data is token counts
		data.append([float(x) for x in p[1:]])

	return rownames, colnames, data

from math import sqrt
def pearson(v1, v2):

	# simple sums
	sum1 = sum(v1)
	sum2 = sum(v2)

	# sums of the squares
	sum1sq = sum([pow(v, 2) for v in v1])
	sum2sq = sum([pow(v, 2) for v in v2])

	# sum of products
	psum = sum([v1[i] * v2[i] for i in range(len(v1))])

	# calculate the Pearson score
	num = psum - (sum1 * sum2 / len(v1))
	den = sqrt((sum1sq - pow(sum1, 2) / len(v1)) * (sum2sq - pow(sum2, 2) / len(v1)))

	if den == 0:
		return 0

	return 1.0 - num / den

def printclust(clust, labels=None, n=0):
	# indent to make a hierarchy layout
	for i in range(n):
		print ' ',

	if clust.id < 0:
		# negative means that this cluster is a branch
		print '-'

	else:
		# positive id means that this is an endpoint
		if labels == None:
			print clust.id
		else:
			print labels[clust.id]

	# now print the left and right branches, recursively
	if clust.left != None:
		printclust(clust.left, labels=labels, n=n+1)

	if clust.right!= None:
		printclust(clust.right, labels=labels, n=n+1)

def hcluster(rows, distance=pearson):

	distances = {}
	currentclustid = -1

	# clusters are initially just the rows
	clust = [Bicluster(rows[i], id=i) for i in range(len(rows))]

	while len(clust) > 1:
		lowestpair = (0, 1)
		closest = distance(clust[0].vec, clust[1].vec)

		# loop through every pair looking for the smallest distance
		for i in range(len(clust)):
			for j in range(i+1, len(clust)):
				# distances is the cache of distance calculations
				if (clust[i].id, clust[j].id) not in distances:
					distances[(clust[i].id, clust[j].id)] = distance(clust[i].vec, clust[j].vec)

				d = distances[(clust[i].id, clust[j].id)]

				if d < closest:
					closest = d
					lowestpair = (i, j)

		# calculate the average of the two clusters
		mergevec = [(clust[lowestpair[0]].vec[i] + clust[lowestpair[1]].vec[i]) / 2.0
			for i in range(len(clust[0].vec))]

		# create new cluster
		newcluster = Bicluster(mergevec, left=clust[lowestpair[0]],
			right=clust[lowestpair[1]], distance=closest,
			id=currentclustid)

		# cluster ids that weren't in the original set are negative
		currentclustid -= 1
		del clust[lowestpair[1]]
		del clust[lowestpair[0]]
		clust.append(newcluster)

	return clust[0]
