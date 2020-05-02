from statistics import mean,stdev
from collections import OrderedDict 
from sortedcontainers import SortedList



class ConsistentHashedRing():
	"""
	Ring structure for consistent hashing
	"""
	
	def __init__(self,hash_function,replicas = 50,csz = 50):

		self.hash_function = hash_function
		self.replicas = replicas
		self.keys = SortedList([])
		self.ring = {}
		self.csz = csz



	def add(self,key):
		"""
		add cache server to the ring
		"""

		for i in range(self.replicas):
			r_hash = self.hash_function(bytearray("{0}{1}".format(i,key),"utf-8"))
			node = Node(key,self,self.csz)
			self.ring[r_hash] = node			
			self.keys.add(r_hash)

			# find server index to rehash
			ind=self.keys.index(r_hash)
			ind=(ind+1)%len(self.keys)
			tn=self.ring[self.keys[ind]]
			tn=tn.get_all()

			temp={}
			for k,v in tn.items():
				temp[k]=v

			# redistribute data
			for k,v in temp.items():
				rh = self.hash_function(bytearray("{0}".format(k),"utf-8"))
				if rh < r_hash:
					self.ring[r_hash].add_data(k,v)
					del tn[k]


			
	def get(self,key):
		"""
		get cache server nearest to the given key
		"""

		if self.keys == []:
			return None

		r_hash = self.hash_function(bytearray("{0}".format(key),"utf-8"))
		self.keys.add(r_hash)
		i = self.keys.index(r_hash)
		self.keys.remove(r_hash)
		i=i%(len(self.keys))

		return self.ring[self.keys[i]]#add CW



	def remove(self,key):
		"""
		remove cache server from ring [server goes down]
		"""

		# check if node exists
		r_hash = self.hash_function(bytearray("{0}{1}".format(0,key),"utf-8"))
		if r_hash not in self.keys:
			return {}
			
		a={}
		for i in range(self.replicas):
			r_hash = self.hash_function(bytearray("{0}{1}".format(i,key),"utf-8"))
			self.keys.remove(r_hash)
			
			temp=self.ring[r_hash]
			temp=temp.get_all()
			for k,v in temp.items():
				a[k]=v
			
			del self.ring[r_hash]

		# return k,v pairs to redistribute		
		return a



	def stats(self):
		"""
		return ring information
		"""

		result = {}
		for key in self.keys:
			node = self.ring[key]
			host,port = node.key.split(":")
			temp = {
				"host": host,
				"port": port,
				"key": key,
				"data": node.get_all()
			}
			result[key] = temp

		return result



	def performance(self):
		"""
		returns load distribution stats
		"""

		if len(self.keys) == 0:
			return {}

		mu = []
		temp = {}

		# combine data from all virtual nodes
		for key in self.keys:
			node = self.ring[key]

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



	def clean(self,r,c):
		"""
		reset the server
		"""

		for key in self.keys:
			self.ring[key].clean()
		self.ring.clear()
		self.keys = SortedList([])
		self.replicas = int(r)
		self.csz = int(c)



class Node():
	"""
	LRU Cache node structure 
	"""

	def __init__(self,key,ring,sz):

		self.key = key
		self._ring = ring
		self._container = OrderedDict()
		self._cachesz = sz



	def get_data(self,key):
		
		if key not in self._container:
			return None
		
		#LRU access 
		val = self._container[key]
		del self._container[key]
		self._container[key] = val
		return self._container[key]



	def add_data(self,key,data):

		self._container[key] = data
		# LRU removal
		if len(self._container) > self._cachesz:
			temp=[]
			for k in self._container.keys():
				temp.append(k)
			del self._container[temp[0]]



	def get_all(self):
		return self._container

	def get_len(self):
		return len(self._container)

	def clean(self):
		self._container.clear()