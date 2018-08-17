#!python3 

"""
Functions for creating random valuations for double auctions.

Author: Erel Segal-Halevi
Since : 2017-09
"""

import numpy as np
from doubleauction import Trader


def randomValuations(minNumOfUnits:int, maxNumOfUnits:int, meanValue:float, maxNoiseSize:float, round:bool=False, index:int=None)->list:
	"""
	Creates a list of tuples (num-of-units, value) that represents a multi-unit valuation function.
	Each marginal value is selected at random from [meanValue +- maxNoiseSize].

	:param minNumOfUnits: min num of units with the same marginal valuation.
	:param maxNumOfUnits: num of units overall.
	:param meanValue:     average marginal value per unit.
	:param maxNoiseSize:  deviation in marginal value per unit.
	:param round: if True, round valuations to nearest integer.
	:param index: if given, add this index to each virtual-valuation, for tracking purposes.
	:return:

	"""
	numOfBundles = maxNumOfUnits // minNumOfUnits
	result = []
	for i in range(numOfBundles):
		val = meanValue + np.random.uniform(-maxNoiseSize,+maxNoiseSize)
		if round: val = int(np.round(val))
		tupleToAdd = (minNumOfUnits, val, index) if index is not None else (minNumOfUnits, val)
		result.append(tupleToAdd)
	return result

def randomAuction(numOfTraders:int, minNumOfUnitsPerTrader:int, maxNumOfUnitsPerTrader:int, meanValue:float, maxNoiseSize:float, fixedNumOfVirtualTraders=False)->list:
	"""
	Creates a set of n buyers and n sellers with random valuations, for simulating a double-auction.

	:param numOfTraders: the number n (number of buyers and number of sellers).
	:param minNumOfUnitsPerTrader:  min num of units with the same marginal valuation.
	:param maxNumOfUnitsPerTrader:  total num of units overall.
	:param meanValue:     average marginal value per unit.
	:param maxNoiseSize:  deviation in marginal value per unit.
	:param fixedNumOfVirtualTraders: If false (default) - numOfTraders is the number of real traders, and the number of virtual traders (units) might be larger.
	                                 If true - fixes the total number of units and determines the number of real traders accordingly.
	:return: a list of Trader objects
	"""
	traders = []
	if fixedNumOfVirtualTraders:
		for i in range(numOfTraders // maxNumOfUnitsPerTrader):
			traders.append ( Trader.Buyer( randomValuations(minNumOfUnitsPerTrader, maxNumOfUnitsPerTrader,meanValue,maxNoiseSize) ) )
			traders.append ( Trader.Seller( randomValuations(minNumOfUnitsPerTrader, maxNumOfUnitsPerTrader,meanValue,maxNoiseSize) ) )
		if numOfTraders%maxNumOfUnitsPerTrader>=minNumOfUnitsPerTrader:
			traders.append ( Trader.Buyer( randomValuations(minNumOfUnitsPerTrader,numOfTraders%maxNumOfUnitsPerTrader,meanValue,maxNoiseSize) ) )
			traders.append ( Trader.Seller( randomValuations(minNumOfUnitsPerTrader,numOfTraders%maxNumOfUnitsPerTrader,meanValue,maxNoiseSize) ) )
	else:   # fixed num of real traders
		for i in range(numOfTraders):
			traders.append ( Trader.Buyer( randomValuations(minNumOfUnitsPerTrader, maxNumOfUnitsPerTrader,meanValue,maxNoiseSize) ) )
			traders.append ( Trader.Seller( randomValuations(minNumOfUnitsPerTrader, maxNumOfUnitsPerTrader,meanValue,maxNoiseSize) ) )
	return traders


def randomAuctions(numOfAuctions:int, numOfTraderss:int, minNumOfUnitsPerTrader:int, maxNumOfUnitsPerTraders:int, meanValue:float, maxNoiseSizes:float, fixedNumOfVirtualTraders=False):
	"""
	A generator, generates a sequence of numOfAuctions random auctions using randomAuction.
	The parameters after numOfAuctions are passed to randomAuction.
	"""
	for i in range(numOfAuctions):
		for numOfTraders in numOfTraderss:
			for maxNumOfUnitsPerTrader in maxNumOfUnitsPerTraders:
				for maxNoiseSize in maxNoiseSizes:
					auctionID = (numOfTraders,minNumOfUnitsPerTrader, maxNumOfUnitsPerTrader,maxNoiseSize)
					yield(auctionID, randomAuction(numOfTraders, minNumOfUnitsPerTrader, maxNumOfUnitsPerTrader, meanValue, maxNoiseSize, fixedNumOfVirtualTraders))

### MAIN PROGRAM ###

if __name__ == "__main__":
	print("randomValuations demo:")
	print(randomValuations(minNumOfUnits=2, maxNumOfUnits=10,      meanValue=500, maxNoiseSize=100))
	print(randomValuations(minNumOfUnits=2, maxNumOfUnits=10,      meanValue=500, maxNoiseSize=100, round=True))
	print(randomValuations(minNumOfUnits=2, maxNumOfUnits=10,      meanValue=500, maxNoiseSize=100, round=True, index=99))

	print("\nrandomAuction demo:")
	print(randomAuction(numOfTraders=5, minNumOfUnitsPerTrader=10, maxNumOfUnitsPerTrader=30, meanValue=100, maxNoiseSize=40, fixedNumOfVirtualTraders=False))
	print(randomAuction(500, 100, 300,   100, 40,fixedNumOfVirtualTraders=True))
	print(randomAuction(5000, 1000, 3000, 100, 40,fixedNumOfVirtualTraders=True))

	print("\nrandomAuctions demo:")
	for auctionID,traders in randomAuctions(2, [3], 10, [20,50], 100, [20,40]):
		print("auctionID: ", auctionID)
		print("traders: ", traders)
		print()
