#!python3 

"""
Defines a class Trader that represents a Trader in an auction for a single good-kind,
and related utility functions.

Author: Erel Segal-Halevi
Since : 2018-08
"""

from operator import itemgetter

class Trader:
	"""
	Represents a multi-unit trader with decreasing-marginal-returns (DMR).
	"""

	def __init__(self, isBuyer:bool, valuations:list, index:int=None):
		"""
		valuations is a list of pairs. Each pair is of the form (numUnits,value).
		They will be sorted automatically by decreasing/increasing value for a buyer/seller resp.
		"""
		self.valuations = sorted(valuations, key=itemgetter(1), reverse=isBuyer)
		self.isBuyer = isBuyer
		if index is not None:
			self.index = index

	def totalUnits(self):
		"""
		Return the total number of units this agent demands/offers.

		>>> Trader(True,((2, 100), (3,200), (4,150))).totalUnits()
		9
		"""
		return sum([v[0] for v in self.valuations])

	def valueOf(self, numBundles:float)->int:
		"""
		The value of the first numBundles bundles.
		>>> Trader(True,((3,200), (4,150), (2, 100))).valueOf(2)
		1200
		"""
		return sum([v[0]*v[1] for v in self.valuations[0:numBundles]])

	def abovePrice(self, price:float)->list:
		"""
		Return only the valuations with value above the given price.
		"""
		return [v for v in self.valuations if v[1]>price]

	def belowPrice(self, price:float)->list:
		"""
		Return only the valuations with value below the given price.
		"""
		return [v for v in self.valuations if v[1]<price]

	def demand(self, price:float)->int:
		"""
		The demand of the given agent in the given price.
		>>> Trader(True,((2, 100), (3,200), (4,150))).demand(151)
		3
		"""
		return sum([v[0] for v in self.abovePrice(price)])

	def demandValue(self, price:float)->int:
		"""
		The total value of the demand of the given agent in the given price.
		>>> Trader(True,((2, 100), (3,200), (4,150))).demandValue(151)
		600
		"""
		return sum([v[0]*v[1] for v in self.abovePrice(price)])

	def supply(self, price:float)->int:
		"""
		The supply of the given agent in the given price.
		>>> Trader(True,((2, 100), (3,200), (4,150))).supply(151)
		6
		"""
		return sum([v[0] for v in self.valuations if v[1]<price])

	def supplyValue(self, price:float)->int:
		"""
		The total value of the supply of the given agent in the given price.
		>>> Trader(True,((2, 100), (3,200), (4,150))).supplyValue(151)
		800
		"""
		return sum([v[0]*v[1] for v in self.valuations if v[1]<price])

	def __repr__(self):
		return ('B' if self.isBuyer else 'S') + self.valuations.__repr__()


	### Static factory methods:

	def Buyer(valuations:list, index:int=None):
		"""
		A helper function to create a buyer.
		>>> Trader.Buyer(((2, 100), (3,200), (4,150)))
		B[(3, 200), (4, 150), (2, 100)]
		"""
		return Trader(True, valuations, index)

	def Seller(valuations:list, index:int=None):
		"""
		A helper function to create a seller.
		>>> Trader.Seller(((2, 100), (3,200), (4,150)))
		S[(2, 100), (4, 150), (3, 200)]
		"""
		return Trader(False, valuations, index)

def virtualTraders(traders:list):
	"""
	INPUT: a list of traders.
	OUTPUT: two lists, one contains the valuations of all buyers,
	        one contains the valuations of all sellers.

	>>> b1 = Trader.Buyer([[4,100],[3,200]])
	>>> b2 = Trader.Buyer([[5,150]])
	>>> s1 = Trader.Seller([[4,100],[3,200]])
	>>> s2 = Trader.Seller([[5,150]])
	>>> (b,s) = virtualTraders([b1,s1,b2,s2])
	>>> b
	[[3, 200], [4, 100], [5, 150]]
	>>> s
	[[4, 100], [3, 200], [5, 150]]
	"""
	virtualBuyers  = []
	virtualSellers = []
	for trader in traders:
		if trader.isBuyer:
			virtualBuyers  += trader.valuations
		else:
			virtualSellers += trader.valuations
	return [virtualBuyers, virtualSellers]


def virtualTradersWithIndices(traders:list)->list:
	"""
	INPUT: A list of lists, each of which contains pairs (quantity, value).

	OUTPUT: a flattened list of triplets: (quantity, value, index).

	>>> virtualTradersWithIndices([ [(5,100),(3,300)], [(4,200),(6,400)] ])
	[(5, 100, 0), (3, 300, 0), (4, 200, 1), (6, 400, 1)]
	"""
	return [(v[0],v[1],index)
		for (index,valuations) in enumerate(traders)
		for v in valuations
		]


def winningAndLosingTraders(traders:list, quota:int)->tuple:
	"""
	INPUT: a list of tuples. In each tuple, element 0 represents "quantity".

	OUTPUT: two lists of tuples: winners and losers.
	        The winners are selected from the beginning of the input list,
	        until the quota is filled; the rest are losers.
	>>> traders = [(5, 100, 0), (3, 300, 0), (4, 200, 1), (6, 400, 1)]
	>>> (winners,losers) = winningAndLosingTraders(traders, quota=10)
	>>> winners
	[(5, 100, 0), (3, 300, 0), (2, 200, 1)]
	>>> losers
	[(2, 200, 1), (6, 400, 1)]
	"""
	winners = []
	losers =  []
	for v in traders:
		currentQuantity = v[0]
		if quota >= currentQuantity:
			winners.append(v)
			quota -= currentQuantity
		elif quota > 0:
			winningQuantity = quota
			losingQuantity  = currentQuantity - winningQuantity
			winners.append( (winningQuantity,)+v[1:] )
			losers.append( (losingQuantity,)+v[1:] )
			quota = 0
		else:
			losers.append( (currentQuantity,)+v[1:] )
	return(winners,losers)




if __name__ == "__main__":
	import doctest
	doctest.testmod()
	print("Doctest OK!\n")
