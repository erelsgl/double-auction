#!python3 

"""
Functions for reading the stock-market datasets extracted from the TORQ database.

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

from doubleauction import Trader




def _tradersByIndices(dataset:DataFrame, indices:list, combineByOrderDate=False):
	if combineByOrderDate:
		#print ("\tcombineByOrderDate!")
		orderDateToBids = {
			"BUY":  defaultdict(list),
			"SEL":  defaultdict(list)
		}
		for i in indices:
			bidRow = dataset.loc[i]
			side = bidRow["Side"]
			orderDate = bidRow['Order date']
			bid = (bidRow["Quantity"], bidRow["Price"])
			orderDateToBids[side][orderDate].append(bid)
		traders = []
		for bids in orderDateToBids["BUY"].values():
			trader = Trader(True, bids) # add a buyer
			traders.append(trader)
		for bids in orderDateToBids["SEL"].values():
			trader = Trader(False, bids) # add a seller
			traders.append(trader)
	else:
		print ("\tadditive!")
		traders = []
		for i in indices:
			bidRow = dataset.loc[i]
			isBuyer = (bidRow["Side"]=="BUY")
			bid = (bidRow["Quantity"], bidRow["Price"])
			bids = [bid]
			trader = Trader(isBuyer, bids)
			traders.append(trader)
	return traders
	

def auctionsBySymbolDate(filename:str, combineByOrderDate=False):
	"""
	INPUT: 
	  *  filename - name of a CSV file that contains order-book data (TORQ SOD format), e.g, 901101-910131-SOD.CSV.
	  *  combineByOrderDate - if true, will assume that different orders from the same day belong to the same trader.
	OUTPUT: a generator that yields, for each (symbol,date) combination in the file, a tuple (symbol,date,traders) where "traders" is list of buyers and sellers.
	"""
	dataset = pd.read_csv(filename)
	grouped = dataset.groupby(['Symbol','Date'])
	for (symbol,date),indices in grouped.groups.items():
		traders = _tradersByIndices(dataset, indices, combineByOrderDate=combineByOrderDate)
		yield ((symbol,date), traders)


def auctionsBySymbol(filename:str, combineByOrderDate=False):
	"""
	INPUT: 
	  *  filename - name of a CSV file that contains order-book data, where the prices are normalized (such that the Walrasian equiilbrium price is always 100). E.g, 901101-910131-SOD-NORM.CSV.
	  *  combineByOrderDate - if true, will assume that different orders from the same day belong to the same trader.
	OUTPUT: a generator that yields, for each symbol in the file, a tuple (symbol,traders) where "traders" is list of buyers and sellers from all dates.
	"""
	dataset = pd.read_csv(filename)
	grouped = dataset.groupby(['Symbol'])
	for symbol,indices in grouped.groups.items():
		traders = _tradersByIndices(dataset, indices, combineByOrderDate=combineByOrderDate)
		yield ((symbol,), traders)



### MAIN PROGRAM ###

if __name__ == "__main__":
	filename =  "910121-910121-IBM-SOD" #  "901101-910131-IBM-SOD" #"901101-910131-SOD" #    
	for (symbolDate,traders) in auctionsBySymbolDate("datasets/"+filename+"-NORM.CSV", combineByOrderDate=False):
		print("Not combined: {} traders".format(len(traders)))
		print(traders)
	for (symbolDate,traders) in auctionsBySymbolDate("datasets/"+filename+"-NORM.CSV", combineByOrderDate=True):
		print("Combined: {} traders".format(len(traders)))
		print(traders)
