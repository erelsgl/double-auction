#!python3 

"""
Functions for normalizing the stock-market datasets extracted from the TORQ database.

Author: Erel Segal-Halevi
Since : 2017-07
"""

import numpy as np
import pandas as pd
from pandas import DataFrame
from pandas.tools import plotting
import matplotlib.pyplot as plt
import math
import os
from collections import defaultdict

from doubleauction import Trader,walrasianEquilibrium
from torq_datasets_read import *

def calculateWalrasianPrices(filename):
	"""
	Reads a dataset that contains buy and sell orders.

	Calculates a dataset that contains the Walrasian equilibrium price for each symbol and day.
	"""
	datasetFilename = "datasets/"+filename+".CSV"
	pricesFilename = "datasets/"+filename+"-PRICES.CSV"
	columns=('Symbol','Date', 'Walrasian Price')
	results = DataFrame(columns=columns)
	print("\t{}".format(columns))

	for symbol,date,traders in auctionsBySymbolDate(datasetFilename, combineByOrderDate=False):
		(equilibriumPrice, numOfBuyers, numOfSellers, sizeOfTrade, gainFromTrade) = walrasianEquilibrium(traders)
		resultsRow = [symbol,int(date),equilibriumPrice]
		print("\t{}".format(resultsRow))
		results.loc[len(results)] = resultsRow
	results.to_csv(pricesFilename)


def normalizePrices(filename):
	"""
	Reads a dataset that contains buy and sell orders,
	and a dataset that contains the Walrasian prices for each symbol and day.
	
	Calculates a dataset that contains the buy and sell orders normalized to a percentage of the price (such that the Walrasian price is always 100).
	"""
	datasetFilename = "datasets/"+filename+".CSV"
	pricesFilename = "datasets/"+filename+"-PRICES.CSV"
	normalizedFilename = "datasets/"+filename+"-NORM.CSV"
	dataset = pd.read_csv(datasetFilename)
	prices =  pd.read_csv(pricesFilename)
	normalized = pd.merge(dataset, prices, on=['Symbol','Date'])
	normalized['Price'] = normalized['Price'] * 100 / normalized['Walrasian Price']
	normalized.drop(["Walrasian Price","Unnamed: 0_x","Unnamed: 0_y"], axis=1, inplace=True)
	normalized.to_csv(normalizedFilename)



### MAIN PROGRAM ###

filename =  "910121-910121-IBM-SOD" #  "901101-910131-IBM-SOD" #"901101-910131-SOD" #    
calculateWalrasianPrices(filename)
normalizePrices(filename)

for (symbol,date,traders) in auctionsBySymbolDate("datasets/"+filename+"-NORM.CSV"):
	print(traders)
