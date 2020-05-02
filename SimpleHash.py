from Ring import Node
from statistics import mean,stdev



class SimpleHash():
	"""
	Ring structure for orthodox hashing
	"""
	
	def __init__(self,hash_function,csz=2500):

		self.hash_function = hash_function
		self.simplehash = []
		self.n = 0
		self.csz=csz


	def add(self):
		"""
		add cache server to the ring
		"""

		self.n += 1
		node = Node(self.n,self,self.csz)
		self.simplehash.append(node)

		# redistribution
		for i in range(0,self.n,1):
			temp = self.simplehash[i].get_all().copy()
			self.simplehash[i].clean()
			for key,value in temp.items():
				r_hash = self.hash_function(bytearray("{0}".format(key),"utf-8"))
				self.simplehash[r_hash%(self.n)].add_data(key,value)



	def get(self,key):
		"""
		get cache server nearest to the given key
		"""

		if self.n:
			r_hash = self.hash_function(bytearray("{0}".format(key),"utf-8"))
			return self.simplehash[r_hash%(self.n)]
		else:
			return None



	def remove(self,key):
		"""
		remove cache server from ring [server goes down]
		"""

		key = int(key)
		if (self.n >= 1) and (0 <= key < self.n):

			# delete key
			a = {}
			temp = self.simplehash[key]
			temp = temp.get_all()
			for k,v in temp.items():
				a[k] = v

			del self.simplehash[key]
			self.n = self.n - 1
			
			# redistribution
			if self.n >= 1:

				# redistribute deleted node's data
				for key,value in a.items():
					r_hash = self.hash_function(bytearray("{0}".format(key),"utf-8"))
					self.simplehash[r_hash%(self.n)].add_data(key,value)

				# redistribute data
				for i in range(0,self.n,1):
					temp = self.simplehash[i].get_all().copy()
					self.simplehash[i].clean()
					for key,value in temp.items():
						r_hash = self.hash_function(bytearray("{0}".format(key),"utf-8"))
						self.simplehash[r_hash%(self.n)].add_data(key,value)



	def stats(self):
		"""
		return ring information
		"""

		result = {}
		for i in range(self.n):
			node = self.simplehash[i]
			temp = {
				"id": i,
				"data": node.get_all()
			}
			result[i] = temp
		return result



	def performance(self):
		"""
		returns load distribution stats
		"""

		if len(self.simplehash) == 0:
			return {}

		mu = []
		temp = {}
		for i in range(self.n):
			node = self.simplehash[i]

			if node.key in temp:
				temp[node.key] = temp[node.key] + node.get_len()
			else:
				temp[node.key] = node.get_len()

		for key in temp:
			mu.append(temp[key])

		if len(mu) == 1:
			return "Only 1 server present"

		result = {
			"Load/Server": mu,
			"Mean": mean(mu),
			"Standard Deviation": stdev(mu),
			"SD as percentage of Mean": str((stdev(mu)/mean(mu))*100)+"%"
		}

		return result



	def clean(self):
		"""
		reset the server
		"""
		
		for i in range(self.n):
			self.simplehash[i].clean()
		self.simplehash = []
		self.n = 0