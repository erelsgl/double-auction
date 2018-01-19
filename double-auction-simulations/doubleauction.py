#!python3 

"""
Implementation of single-good multi-unit double-auction mechanisms.

Author: Erel Segal-Halevi
Since : 2017-07
"""

from operator import itemgetter, attrgetter
import functools
import math
import random
from collections import defaultdict


class Trader:
	"""
	Represents a multi-unit trader with decreasing-marginal-returns (DMR).
	"""

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
	
	def Buyer(valuations:list):
		"""
		A helper function to create a buyer.
		>>> Trader.Buyer(((2, 100), (3,200), (4,150)))
		B[(3, 200), (4, 150), (2, 100)]
		"""
		return Trader(True, valuations)

	def Seller(valuations:list):
		"""
		A helper function to create a seller.
		>>> Trader.Seller(((2, 100), (3,200), (4,150)))
		S[(2, 100), (4, 150), (3, 200)]
		"""
		return Trader(False, valuations)

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

	
def winningAndLosingTraders(traders:list, quota:int)->tuple:
	"""
	INPUT: a list with elements of type (quantity,value,index).
	
	OUTPUT: two lists: winning elements and losing elements. The total quantity of the winning items is at most the quota.
	
	>>> (winners,losers) = winningAndLosingTraders([(5, 100, 0), (3, 300, 0), (4, 200, 1), (6, 400, 1)], 10)
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
		
def walrasianEquilibrium(traders:list):
	"""
	Calculate a Walrasian equilibrium (aka competitive equilibrium) in a single-type multi-unit market.
	INPUT: a list of Trader objects, each of which represents valuations with decreasing marginal returns.
	OUTPUT: (equilibriumPrice, numOfBuyers, numOfSellers, totalUnitsTraded, gainFromTrade)
	
	>>> b1 = Trader.Buyer([[5,250]])
	>>> b2 = Trader.Buyer([[4,150],[3,350]])
	>>> s1 = Trader.Seller([[5,200]])
	>>> s2 = Trader.Seller([[4,100],[3,300]])
	>>> walrasianEquilibrium([b1])[1:5]   # (quantity,gain)
	(0, 0, 0, 0)
	>>> walrasianEquilibrium([s1])[1:5]
	(0, 0, 0, 0)
	>>> walrasianEquilibrium([s1,b1])[1:5]
	(1, 1, 5, 250)
	>>> walrasianEquilibrium([s1,b2])[1:5]
	(1, 1, 3, 450)
	>>> walrasianEquilibrium([b1,s2])[1:5]
	(1, 1, 4, 600)
	>>> walrasianEquilibrium([b1,b2,s1,s2])[1:5]
	(2, 2, 8, 1100)
	"""
	(virtualBuyers,virtualSellers) = virtualTraders(traders)
	virtualBuyers.sort(key=itemgetter(1), reverse=False)   # last buyer has highest value
	virtualSellers.sort(key=itemgetter(1), reverse=False)  # last seller has highest value
	price = math.inf  # the price decreases until equilibrium is found
	demand = 0
	buyersValue = 0
	numOfBuyers = 0
	supply = sum ([s[0] for s in virtualSellers])
	sellersValue = sum([s[0]*s[1]for s in virtualSellers])
	numOfSellers = len(virtualSellers)
	totalUnitsTraded = 0
	while demand < supply:
		(currentDemand,currentDemandValue) = virtualBuyers[-1] if virtualBuyers else (0,0)
		(currentSupply,currentSupplyValue) = virtualSellers[-1] if virtualSellers else (0,0)
		if currentDemandValue >= currentSupplyValue:  # a buyer enters the room
			numOfBuyers += 1
			price = currentDemandValue
			if demand+currentDemand > supply:
		 		units = supply-demand
			else:
				units = currentDemand
			buyersValue += units*currentDemandValue
			demand += units
			totalUnitsTraded += units
			virtualBuyers.pop()
		else:  # a seller exits the room
			price = currentSupplyValue
			if demand > supply-currentSupply:
		 		units = supply-demand
			else:
				units = currentSupply
				numOfSellers -= 1
			sellersValue -= units*currentSupplyValue
			supply -= units
			virtualSellers.pop()

	return (price, numOfBuyers, numOfSellers, totalUnitsTraded, buyersValue-sellersValue)
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
	
	
############## RANDOM TRADE #################	

def randomTradeWithExogeneousPrice(traders:list, price:float)->tuple:
	"""
	Calculates the trade in the given market, when the price is determined exogeneously.
	Excess demand/supply is settled using a random permutation.
	
	INPUT: a list of Trader objects, and an exogeneous price.
	OUTPUT: (totalUnitsTraded, gainFromTrade)
	
	TODO: if a trader's value exactly equals the price, 
	we should choose for him how many units he trades, to improve gain-from-trade.
	
	>>> randomTradeWithExogeneousPrice.LOG = False
	>>> b1 = Trader.Buyer([[5,250]])
	>>> b2 = Trader.Buyer([[4,150],[3,350]])
	>>> s1 = Trader.Seller([[5,200]])
	>>> s2 = Trader.Seller([[4,100],[3,300]])
	>>> random.seed(2)
	>>> randomTradeWithExogeneousPrice([b1,b2,s1,s2],51)
	(0, 0)
	>>> randomTradeWithExogeneousPrice([b1,b2,s1,s2],101)
	(4, 800)
	>>> randomTradeWithExogeneousPrice([b1,b2,s1,s2],151)
	(4, 900)
	>>> randomTradeWithExogeneousPrice([b1,b2,s1,s2],201)
	(8, 1100)
	"""	
	activeBuyers =  [t.abovePrice(price) for t in traders if t.isBuyer]
	random.shuffle(activeBuyers)
	activeSellers = [t.belowPrice(price) for t in traders if not t.isBuyer]
	random.shuffle(activeSellers)

	virtualBuyers  = virtualTradersWithIndices(activeBuyers)
	virtualSellers = virtualTradersWithIndices(activeSellers)
	totalDemand = sum([v[0] for v in virtualBuyers])
	totalSupply = sum([v[0] for v in virtualSellers])

	if randomTradeWithExogeneousPrice.LOG:
		print("totalDemand:", totalDemand, "activeBuyers:",activeBuyers)
		print("totalSupply:", totalSupply, "activeSellers:",activeSellers)

	if totalDemand < totalSupply:    # buyers are short
		totalUnitsTraded = totalDemand
		buyersGain = sum([v[0]*(v[1]-price) for v in virtualBuyers])
		candidates = virtualSellers
		(winners,losers) = winningAndLosingTraders(candidates, totalUnitsTraded)
		sellersGain = sum([v[0]*(price-v[1]) for v in winners])
		totalGain = buyersGain+sellersGain
	else:    # sellers are short
		totalUnitsTraded = totalSupply
		sellersGain = sum([v[0]*(price-v[1]) for v in virtualSellers])
		candidates = virtualBuyers
		(winners,losers) = winningAndLosingTraders(candidates, totalUnitsTraded)
		buyersGain = sum([v[0]*(v[1]-price) for v in winners])
		totalGain = buyersGain+sellersGain

	return (totalUnitsTraded, totalGain)
randomTradeWithExogeneousPrice.LOG = False



################# UTILITIES FOR VICKREY-MUDA

def unitsByIndex(traders:list)->dict:
	units = defaultdict(int)
	for t in traders:
		curIndex = t[2]
		curUnits = t[0]
		units[curIndex] += curUnits
	return units
	
	
def winnerPayment(winnerIndex:int, winnerUnits:int, losers:list)->float:
	"""
	Calculate Vickrey payments for a single winner in a multi-unit auction.
	
	>>> losers = [(2, 200, 0), (6, 400, 1), (999999, 500, -1)]
	>>> winnerPayment(0, 5, losers)
	2000
	>>> winnerPayment(1, 5, losers)
	1900
	"""
	payment = 0
	for (loserUnits,loserValue,loserIndex) in losers:
		if loserIndex==winnerIndex:
			continue
		if winnerUnits >= loserUnits:
			payment += loserUnits*loserValue
			winnerUnits -= loserUnits
		else: # winnerUnits < loserUnits
			payment += winnerUnits*loserValue
			return payment
	

RESERVE_AGENT = -1
def VickreyTradeWithExogeneousPrice(traders:list, price:float)->tuple:
	"""
	Calculates the trade in the given market, when the price is determined exogeneously.
	Excess demand/supply is settled using a Vickrey auction.
	
	INPUT: a list of Trader objects, and an exogeneous price.
	OUTPUT: (numOfBuyers, numOfSellers, totalUnitsTraded, tradersGain, totalGain)
	
	>>> b1 = Trader.Buyer([[5,250]])
	>>> b2 = Trader.Buyer([[4,150],[3,350]])
	>>> s1 = Trader.Seller([[5,200]])
	>>> s2 = Trader.Seller([[4,100],[3,300]])
	>>> VickreyTradeWithExogeneousPrice([b1,b2,s1,s2],51) # supply=0
	(0, 0, 0, 0)
	>>> VickreyTradeWithExogeneousPrice([b1,b2,s1,s2],101) # supply=4
	(4, 404, 496, 900)
	>>> VickreyTradeWithExogeneousPrice([b1,b2,s1,s2],151) # supply=4
	(4, 603, 297, 900)
	>>> VickreyTradeWithExogeneousPrice([b1,b2,s1,s2],201) # supply=9
	(8, 1099, 1, 1100)
	"""
	activeBuyers =  [t.abovePrice(price) for t in traders if t.isBuyer]
	activeSellers = [t.belowPrice(price) for t in traders if not t.isBuyer]
	if (VickreyTradeWithExogeneousPrice.LOG):
		print("activeBuyers",activeBuyers)
		print("activeSellers",activeSellers)
	
	virtualBuyers  = virtualTradersWithIndices(activeBuyers)
	virtualSellers = virtualTradersWithIndices(activeSellers)
	
	totalDemand = sum([v[0] for v in virtualBuyers])
	totalSupply = sum([v[0] for v in virtualSellers])

	if totalDemand < totalSupply:    # buyers are short
		totalUnitsTraded = totalDemand
		buyersGain = sum([v[0]*(v[1]-price) for v in virtualBuyers])
		virtualSellers = sorted(virtualSellers, key=itemgetter(1), reverse=False)   # sort virtual-sellers in ascending order
		if (VickreyTradeWithExogeneousPrice.LOG):
			print("virtualSellers",virtualSellers)
		(winners,losers) = winningAndLosingTraders(virtualSellers, totalUnitsTraded)
		unitsPerWinner = unitsByIndex(winners)
		losers.append( (999999999,price,RESERVE_AGENT) )  # add dummies in reserve price
		if (VickreyTradeWithExogeneousPrice.LOG):
			print("\twinners",winners)
			print("\tlosers",losers)
			print("\tunitsPerWinner",unitsPerWinner)
			print("\tbuyers gain",buyersGain)
		managerGain = 0
		for winnerIndex,winnerUnits in unitsPerWinner.items():  # calculate the payment per winners
			payment = winnerPayment(winnerIndex,winnerUnits,losers)
			managerGain += (price*winnerUnits - payment)
		totalGain = buyersGain + sum([v[0]*(price-v[1]) for v in winners])

	else:    # sellers are short
		totalUnitsTraded = totalSupply
		sellersGain = sum([v[0]*(price-v[1]) for v in virtualSellers])
		virtualBuyers = sorted(virtualBuyers, key=itemgetter(1), reverse=True)   # sort virtual-buyers in descending order
		if (VickreyTradeWithExogeneousPrice.LOG):
			print("virtualBuyers",virtualBuyers)
		(winners,losers) = winningAndLosingTraders(virtualBuyers, totalUnitsTraded)
		unitsPerWinner = unitsByIndex(winners)
		losers.append( (999999999,price,RESERVE_AGENT) )  # add dummies in reserve price
		if (VickreyTradeWithExogeneousPrice.LOG):
			print("\twinners",winners)
			print("\tlosers",losers)
			print("\tunitsPerWinner",unitsPerWinner)
			print("\tsellers gain",sellersGain)
		managerGain = 0
		for winnerIndex,winnerUnits in unitsPerWinner.items():  # calculate the payment per winners
			payment = winnerPayment(winnerIndex,winnerUnits,losers)
			managerGain += (payment - price*winnerUnits)
		totalGain = sellersGain + sum([v[0]*(v[1]-price) for v in winners])

	tradersGain = totalGain - managerGain
	return (totalUnitsTraded, tradersGain, managerGain, totalGain)
VickreyTradeWithExogeneousPrice.LOG = False



#### Implementation of mechanisms

def MUDA(traders:list, Lottery=True, Vickrey=False) -> (int,float):
	"""
	Run the Multi-Item-Double-Auction mechanism.
	INPUT: a list of Trader objects, each of which represents valuations with decreasing marginal returns.
		* Lottery - handle excess demand/supply using a lottery.
		* Vickrey - handle excess demand/supply using a Vickrey auction.
	OUTPUT: (totalUnitsTraded, tradersGain, totalGain)
	
	>>> b1 = Trader.Buyer([[5,250]])
	>>> b2 = Trader.Buyer([[4,150],[3,350]])
	>>> s1 = Trader.Seller([[5,200]])
	>>> s2 = Trader.Seller([[4,100],[3,300]])
	>>> MUDA.LOG = randomTradeWithExogeneousPrice.LOG = False
	>>> random.seed(7)
	>>> MUDA([b1,b2,s1,s2], Lottery=True, Vickrey=True)
	(4, 900, 900, 4, 750, 900)
	"""
	(tradersLeft,tradersRight) = randomPartition(traders)
	priceLeft  = walrasianEquilibrium(tradersLeft)[0]
	priceRight = walrasianEquilibrium(tradersRight)[0]
	result = ()
	if Lottery:
		if MUDA.LOG: 
			print ("Left sub-market: pR=", priceRight, "traders=",tradersLeft)
		(sizeLeft, gainLeft) = randomTradeWithExogeneousPrice(tradersLeft, priceRight)
		if MUDA.LOG: 
			print ("Right sub-market: pL=", priceLeft, "traders=",tradersRight)
		(sizeRight, gainRight) = randomTradeWithExogeneousPrice(tradersRight, priceLeft)
		result += (sizeRight+sizeLeft, gainRight+gainLeft, gainRight+gainLeft)
	if Vickrey:
		(sizeLeft, tradersGainLeft, managerGainLeft, totalGainLeft) = VickreyTradeWithExogeneousPrice(tradersLeft, priceRight)
		(sizeRight, tradersGainRight, managerGainRight, totalGainRight) = VickreyTradeWithExogeneousPrice(tradersRight, priceLeft)
		result += (sizeRight+sizeLeft, tradersGainRight+tradersGainLeft, totalGainRight+totalGainLeft)
	if MUDA.LOG: 
		print(result)
	return result
MUDA.LOG = False

def WALRAS(traders:list) -> (int, int, int, float):
	"""
	Run the Walrasian-equilibrium mechanism.
	INPUT: a list of Trader objects, each of which represents valuations with decreasing marginal returns.
	OUTPUT: (numOfBuyers, numOfSellers, totalUnitsTraded, gainFromTrade)
	"""
	(price, numOfBuyers, numOfSellers, totalUnitsTraded, gainFromTrade) = walrasianEquilibrium(traders)
	return (numOfBuyers, numOfSellers, totalUnitsTraded, gainFromTrade)


if __name__ == "__main__":
	if True: # False: # 
		import doctest
		walrasianEquilibrium.LOG=False
		doctest.testmod()
		print("Doctest OK!\n")
	else:
		b1 = Trader.Buyer([[4,150],[3,350]])
		b2 = Trader.Buyer([[5,250]])
		s2 = Trader.Seller([[5,100],[3,300]])
		s1 = Trader.Seller([[5,200]])

		#walrasianEquilibrium.LOG=True
		#print(walrasianEquilibrium([b1,b2,s1,s2]))

		#randomTradeWithExogeneousPrice.LOG = True
		#print(randomTradeWithExogeneousPrice([b1,b2,s1,s2],51))
		#print(randomTradeWithExogeneousPrice([b1,b2,s1,s2],101))
		#print(randomTradeWithExogeneousPrice([b1,b2,s1,s2],151))
		#print(randomTradeWithExogeneousPrice([b1,b2,s1,s2],201))
		#print(randomTradeWithExogeneousPrice([b1,b2,s1,s2],225))  # demand=8 and supply=9; competition between a 100 seller and a 200 seller.

		#walrasianEquilibrium.LOG=False
		#randomTradeWithExogeneousPrice.LOG = False
		#MUDA.LOG = True
		#print(MUDA([b1,b2,s1,s2]))
		
		#VickreyTradeWithExogeneousPrice.LOG = True
		#print(VickreyTradeWithExogeneousPrice([b1,b2,s1,s2],51))
		#print(VickreyTradeWithExogeneousPrice([b1,b2,s1,s2],101))
		#print(VickreyTradeWithExogeneousPrice([b1,b2,s1,s2],151))
		#print(VickreyTradeWithExogeneousPrice([b1,b2,s1,s2],201))
		#print(VickreyTradeWithExogeneousPrice([b1,b2,s1,s2],225))
