#!python3 

"""
Implementation of single-type multi-unit double-auction mechanisms.

Author: Erel Segal-Halevi
Since : 2017-07
"""

from operator import itemgetter, attrgetter
import functools
import math
import random


class Trader:
	def __init__(self, isBuyer:bool, valuations:list):
		"""
		valuations is a list of pairs. Each pair is of the form (numUnits,value).
		They will be sorted automatically by decreasing/increasing value for a buyer/seller resp.
		"""
		self.valuations = sorted(valuations, key=itemgetter(1), reverse=isBuyer)
		self.isBuyer = isBuyer
		
	def totalUnits(self):
		"""
		Return the total number of units this agent demands/offers.
		
		>>> Trader(True,((2, 100), (3,200), (4,150))).totalUnits()
		9
		"""
		return sum([v[0] for v in self.valuations])

	def Buyer(valuations:list):
		"""
		A helper function to create a buyer.
		>>> Trader.Buyer(((2, 100), (3,200), (4,150)))
		B[(3, 200), (4, 150), (2, 100)]
		"""
		return Trader(True, valuations)

	def Seller(valuations):
		"""
		A helper function to create a seller.
		>>> Trader.Seller(((2, 100), (3,200), (4,150)))
		S[(2, 100), (4, 150), (3, 200)]
		"""
		return Trader(False, valuations)
		
	def __repr__(self):
		return ('B' if self.isBuyer else 'S') + self.valuations.__repr__()
		

def virtualTraders(traders:list):
	"""
	INPUT: a list of traders.
	OUTPUT: two lists, one contains the valuations of all buyers, one contains the valuations of all sellers.
	
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

	
def walrasianEquilibrium(traders:list):
	"""
	Calculate a Walrasian equilibrium (aka competitive equilibrium) in a single-type multi-unit market.
	INPUT: a list of Trader objects, each of which represents valuations with decreasing marginal returns.
	OUTPUT: (equilibriumPrice, sizeOfTrade, gainFromTrade)
	
	>>> b1 = Trader.Buyer([[5,250]])
	>>> b2 = Trader.Buyer([[4,150],[3,350]])
	>>> s1 = Trader.Seller([[5,200]])
	>>> s2 = Trader.Seller([[4,100],[3,300]])
	>>> walrasianEquilibrium([b1])[1:3]   # (quantity,gain)
	(0, 0)
	>>> walrasianEquilibrium([s1])[1:3]
	(0, 0)
	>>> walrasianEquilibrium([s1,b1])[1:3]
	(5, 250)
	>>> walrasianEquilibrium([s1,b2])[1:3]
	(3, 450)
	>>> walrasianEquilibrium([b1,s2])[1:3]
	(4, 600)
	>>> walrasianEquilibrium([b1,b2,s1,s2])[1:3]
	(8, 1100)
	"""
	(virtualBuyers,virtualSellers) = virtualTraders(traders)
	virtualBuyers.sort(key=itemgetter(1), reverse=False)   # last buyer has highest value
	virtualSellers.sort(key=itemgetter(1), reverse=False)  # last seller has highest value
	price = math.inf  # the price decreases until equilibrium is found
	demand = 0
	buyersValue = 0
	supply = sum ([s[0] for s in virtualSellers])
	sellersValue = sum([s[0]*s[1]for s in virtualSellers])
	sizeOfTrade = 0
	while demand < supply:
		(currentDemand,currentDemandValue) = virtualBuyers.pop() if virtualBuyers else (0,0)
		(currentSupply,currentSupplyValue) = virtualSellers.pop() if virtualSellers else (0,0)
		if currentDemandValue >= currentSupplyValue:  # a buyer enters the room
			price = currentDemandValue
			if demand+currentDemand > supply:
		 		units = supply-demand
			else:
				units = currentDemand
			buyersValue += units*currentDemandValue
			demand += units
			sizeOfTrade += units
			virtualSellers.append((currentSupply,currentSupplyValue))
		else:  # a buyer exits the room
			price = currentSupplyValue
			if demand > supply-currentSupply:
		 		units = supply-demand
			else:
				units = currentSupply
			sellersValue -= units*currentSupplyValue
			supply -= units
			virtualBuyers.append((currentDemand,currentDemandValue))

	# OLD ALGORITHM:
	# virtualSellers = []
	# virtualBuyers  = []  # sellers are also considered buyers - buying their own items.
	# for trader in traders:
	# 	if not trader.isBuyer:
	# 		virtualSellers += trader.valuations
	# 	virtualBuyers += [(v[0],v[1],trader.isBuyer) for v in trader.valuations]
	# 
	# supply = sum ([s[0] for s in virtualSellers])
	# sellersValue = sum([s[0]*s[1]for s in virtualSellers])
	# if walrasianEquilibrium.LOG: print("supply {}, sellersValue {}".format(supply,sellersValue))
	# 
	# virtualBuyers.sort(key=itemgetter(1), reverse=True)   # sort all virtual traders by decreasing value.
	# 
	# price = math.inf
	# demand = 0
	# sizeOfTrade = 0
	# buyersValue = 0
	# for (units,value,isBuyer) in virtualBuyers:
	# 	# If supply > 0, we will get into the loop and remain inside until supply=demand.
	# 	# Here, demand <= supply, so we can decrease the price.
	# 	price = value
	# 	if demand+units > supply:
	# 		units = supply-demand
	# 		buyersValue += units*value
	# 		demand += units
	# 		if isBuyer: sizeOfTrade += units
	# 		break  # equilibrium found
	# 	else:
	# 		buyersValue += units*value
	# 		demand += units
	# 		if isBuyer: sizeOfTrade += units 
	# 		# Here, demand <= supply.
	
	# Here, demand = supply (either both are 0, or both are made equal in the loop)
	return (price, sizeOfTrade, buyersValue-sellersValue)
walrasianEquilibrium.LOG=False


def randomPartition(theList:list)->(list,list):
	"""
	INPUT: one list.
	OUTPUT: two lists. Each item in input goes to each list in output with probabaility 1/2.
	"""
	left  = []
	right = []
	for item in theList:
		if random.random()<0.5:
			left.append(item)
		else:
			right.append(item)
	return (left,right)


def randomTradeWithExogeneousPrice(traders:list, price:float):
	"""
	Calculates the trade in the given market, when the price is determined exogeneously.
	Excess demand/supply is settled using a random permutation.
	
	INPUT: a list of Trader objects, and an exogeneous price.
	OUTPUT: (sizeOfTrade,gainFromTrade)
	
	TODO: if a trader's value exactly equals the price, 
	we should choose for him how many units he trades, to improve gain-from-trade.
	
	>>> b1 = Trader.Buyer([[5,250]])
	>>> b2 = Trader.Buyer([[4,150],[3,350]])
	>>> s1 = Trader.Seller([[5,200]])
	>>> s2 = Trader.Seller([[4,100],[3,300]])
	>>> randomTradeWithExogeneousPrice([b1,b2,s1,s2],50)[0]
	0
	>>> randomTradeWithExogeneousPrice([b1,b2,s1,s2],100)[0]
	4
	>>> randomTradeWithExogeneousPrice([b1,b2,s1,s2],150)[0]
	4
	>>> randomTradeWithExogeneousPrice([b1,b2,s1,s2],200)[0]
	8
	"""
	random.shuffle(traders)
	(virtualBuyers,virtualSellers) = virtualTraders(traders)
	virtualBuyers = [b for b in virtualBuyers if b[1]>=price]
	virtualSellers = [s for s in virtualSellers if s[1]<=price]

	sizeOfTrade = 0
	gainFromTrade = 0
	while virtualBuyers and virtualSellers:
		(currentDemand,currentDemandValue) = virtualBuyers.pop()
		(currentSupply,currentSupplyValue) = virtualSellers.pop()
		if randomTradeWithExogeneousPrice.LOG: print("Buyer: {} units at {}.  Seller: {} units at {}.".format(currentDemand,currentDemandValue,currentSupply,currentSupplyValue))
		units = min(currentSupply,currentDemand)
		if currentDemand > currentSupply:
			virtualBuyers.append((currentDemand-currentSupply, currentDemandValue))
		elif currentDemand < currentSupply:
			virtualSellers.append((currentSupply-currentDemand, currentSupplyValue))
		sizeOfTrade += units
		gainFromTrade += units*(currentDemandValue - currentSupplyValue)
	return (sizeOfTrade, gainFromTrade)
randomTradeWithExogeneousPrice.LOG = False



#### Implementation of mechanisms

def MIDA(traders:list) -> (int,float):
	"""
	Run the Multi-Item-Double-Auction mechanism.
	INPUT: a list of Trader objects, each of which represents valuations with decreasing marginal returns.
	OUTPUT: (sizeOfTrade, gainFromTrade)
	"""
	(tradersLeft,tradersRight) = randomPartition(traders)
	if MIDA.LOG: print ("Left:", tradersLeft, "Right:", tradersRight)
	priceLeft  = walrasianEquilibrium(tradersLeft)[0]
	priceRight = walrasianEquilibrium(tradersRight)[0]
	(sizeLeft,gainLeft) = randomTradeWithExogeneousPrice(tradersLeft, priceRight)
	(sizeRight,gainRight) = randomTradeWithExogeneousPrice(tradersRight, priceLeft)
	return (sizeRight+sizeLeft, gainRight+gainLeft)
MIDA.LOG = False

def WALRAS(traders:list) -> (int,float):
	"""
	Run the Walrasian-equilibrium mechanism.
	INPUT: a list of Trader objects, each of which represents valuations with decreasing marginal returns.
	OUTPUT: (sizeOfTrade, gainFromTrade)
	"""
	(price,sizeOfTrade,gainFromTrade) = walrasianEquilibrium(traders)
	return (price,sizeOfTrade)


if __name__ == "__main__":
	if True: # False: # 
		import doctest
		walrasianEquilibrium.LOG=False
		doctest.testmod()
		print("Doctest OK!\n")
	else:
		b1 = Trader.Buyer([[4,150],[3,350]])
		b2 = Trader.Buyer([[5,250]])
		s1 = Trader.Seller([[4,100],[3,300]])
		s2 = Trader.Seller([[5,200]])

		walrasianEquilibrium.LOG=True
		print(walrasianEquilibrium([b1,b2,s1,s2]))

		randomTradeWithExogeneousPrice.LOG = True
		print(randomTradeWithExogeneousPrice([b1,b2,s1,s2],50))
		print(randomTradeWithExogeneousPrice([b1,b2,s1,s2],100))
		print(randomTradeWithExogeneousPrice([b1,b2,s1,s2],150))
		print(randomTradeWithExogeneousPrice([b1,b2,s1,s2],200))
		print(randomTradeWithExogeneousPrice([b1,b2,s1,s2],225))  # demand=8 and supply=9; competition between a 100 seller and a 200 seller.

		walrasianEquilibrium.LOG=False
		randomTradeWithExogeneousPrice.LOG = False
		MIDA.LOG = True
		print(MIDA([b1,b2,s1,s2]))
