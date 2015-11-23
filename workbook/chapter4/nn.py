import sqlite3

from math import tanh

class SearchNet(object):
	def __init__(self, dbname):
		self.con = sqlite3.connect(dbname)


	def __del__(self):
		self.con.close()

	def maketables(self):
		 self.con.execute('create table hiddennode(create_key)')
		 self.con.execute('create table wordhidden(fromid, toid, strength)')
		 self.con.execute('create table hiddenurl(fromid, toid, strength)')
		 self.con.commit()


	def get_strength(self, fromid, toid, layer):
		if layer == 0:
			table = 'wordhidden'
		else:
			table = 'hiddenurl'

		res = self.con.execute(
			'select strength from %s where fromid=%d and toid=%d' %
			(table, fromid, toid)).fetchone()

		if res is None:
			if layer == 0:
				return -0.2
			if layer == 1:
				return 0

		return res[0]

	def set_strength(self, fromid, toid, layer, strength):
		if layer == 0:
			table = 'wordhidden'
		else:
			table = 'hiddenurl'

		res = self.con.execute(
			'select rowid from %s where fromid=%d and toid=%d' %
			(table, fromid, toid)).fetchone()

		if res is None:
			self.con.execute(
				'insert into %s (fromid, toid, strength) values (%d, %d, %f)' %
				(table, fromid, toid, strength))

		else:
			rowid = res[0]
			self.con.execute(
				'update %s set strength=%f where rowid=%d' %
				(table, strength, rowid))

	def generate_hidden_node(self, wordids, urls):
		if len(wordids) > 3:
			return None

		# check if we already created a node
		# for this set of words
		create_key = '_'.join(sorted([str(wi) for wi in wordids]))

		res = self.con.execute(
			"select rowid from hiddennode where create_key='%s'" %
			create_key).fetchone()

		# if not, create it
		if res == None:
			cur = self.con.execute(
				"insert into hiddennode (create_key) values ('%s')" % 
				create_key)

			hiddenid = cur.lastrowid

			# put in some default weights
			for wordid in wordids:
				self.set_strength(wordid, hiddenid, 0, 1.0/len(wordids))

			for urlid in urls:
				self.set_strength(hiddenid, urlid, 1, 0.1)

			self.con.commit()
