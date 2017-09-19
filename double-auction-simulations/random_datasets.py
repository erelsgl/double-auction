#!python3 

"""
Functions for creating random valuations for double auctions.

Author: Erel Segal-Halevi
Since : 2017-09
"""

import numpy as np
import pandas as pd
from pandas import DataFrame
from pandas.tools import plotting
import matplotlib.pyplot as plt
import math
import os
from collections import defaultdict

from doubleauction import Trader
		
def randomValuations(minNumOfUnits:int, maxNumOfUnits:int, meanValue:float, maxNoiseSize:float)->list:
	numOfBundles = maxNumOfUnits // minNumOfUnits
	return [(minNumOfUnits, meanValue+np.random.uniform(-maxNoiseSize,+maxNoiseSize)) for i in range(numOfBundles)]

def randomAuction(numOfTraders:int, minNumOfUnitsPerTrader:int, maxNumOfUnitsPerTrader:int, meanValue:float, maxNoiseSize:float,fixedNumOfVirtualTraders=False)->list:
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
	for i in range(numOfAuctions):
		for numOfTraders in numOfTraderss:
			for maxNumOfUnitsPerTrader in maxNumOfUnitsPerTraders:
				for maxNoiseSize in maxNoiseSizes:
					auctionID = (numOfTraders,minNumOfUnitsPerTrader, maxNumOfUnitsPerTrader,maxNoiseSize)
					yield(auctionID, randomAuction(numOfTraders, minNumOfUnitsPerTrader, maxNumOfUnitsPerTrader, meanValue, maxNoiseSize, fixedNumOfVirtualTraders))

### MAIN PROGRAM ###

if __name__ == "__main__":
	print(randomValuations(2, 10,      500, 100))
	print(randomAuction(5, 10, 30,     100, 40))
	print(randomAuction(500, 100, 300,   100, 40,fixedNumOfVirtualTraders=True))
	print(randomAuction(5000, 1000, 3000, 100, 40,fixedNumOfVirtualTraders=True))
	print(list(randomAuctions(2, [3], 10, [20,50], 100, [20,40])))
