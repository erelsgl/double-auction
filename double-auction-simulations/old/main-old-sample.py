#!python3 

"""
Simulation of single-type multi-unit double-auction mechanisms.

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
import random

from doubleauction import MIDA,WALRAS,walrasianEquilibrium,randomTradeWithExogeneousPrice
import torq_datasets_read as torq
from random_datasets import randomAuctions

COLUMNS=(
	'Key', 
	'Total buyers', 'Total sellers', 'Total traders', 'Min total traders', 'Total units', 
	'Max units per trader', 'stddev',
	'Optimal buyers', 'Optimal sellers', 'Optimal units',
	'Optimal gain', 'MIDA-lottery gain', 'MIDA-Vickrey traders gain', 'MIDA-Vickrey total gain')

def replicaAuctions(replicaNums:list, auctions:list):
	"""
	INPUT: auctions - list of m auctions;  
	       replicaNums - list of n integers.
	OUTPUT: generator of m*n auctions, where in each auction, each agent is replicated i times.
	"""
	for auctionID,auctionTraders in auctions:
		for replicas in replicaNums:
			traders = replicas * auctionTraders 
			yield auctionID,traders

def sampleAuctions(agentNums:list, auctions:list):
	"""
	INPUT: auctions - list of m auctions;  
	       agentNums - list of n integers.
	OUTPUT: generator of m*n auctions, where in each auction, i agents are sampled from the empirical distribution
	"""
	for auctionID,auctionTraders in auctions:
		for agentNum in agentNums:
			traders = [random.choice(auctionTraders) for i in range(agentNum)]
			yield auctionID,traders


def simulateAuctions(auctions:list, resultsFilename:str, replicaNums=[1]):
	"""
	Simulate the auctions in the given generator.
	"""
	results = DataFrame(columns=COLUMNS)
	print("\t{}".format(COLUMNS))
	resultsFilenameTemp = resultsFilename+".temp"
	for auctionID,auctionTraders in auctions:
		print("Simulating auction {} with {} traders".format(auctionID,len(traders)))
		totalBuyers = sum([t.isBuyer for t in traders])
		totalSellers = len(traders)-totalBuyers
		totalUnits = sum([t.totalUnits() for t in traders])
		maxUnitsPerTrader = max([t.totalUnits() for t in traders])
		stddev = np.sqrt(sum([t.totalUnits()**2 for t in traders]))
		(buyersWALRAS, sellersWALRAS, sizeWALRAS, gainWALRAS) = WALRAS(traders)
		(sizeMIDALottery, gainMIDALottery, gainMIDALottery, sizeMIDAVickrey, tradersGainMIDAVickrey, totalGainMIDAVickrey) = MIDA(traders, Lottery=True, Vickrey=True)
		resultsRow = [
			auctionID,
			totalBuyers, totalSellers, totalBuyers+totalSellers, min(totalBuyers,totalSellers), totalUnits,
			maxUnitsPerTrader, stddev,
			buyersWALRAS, sellersWALRAS, sizeWALRAS,
			gainWALRAS, gainMIDALottery, tradersGainMIDAVickrey, totalGainMIDAVickrey]
		print("\t{}".format(resultsRow))
		results.loc[len(results)] = resultsRow
		results.to_csv(resultsFilenameTemp)
	results.to_csv(resultsFilename)
	os.remove(resultsFilenameTemp)
	return results


def torqSimulationBySymbolDate(filename, combineByOrderDate=False, replicaNums=[1]):
	"""
	Treat each (symbol,date) combination as a separate auction.
	"""
	datasetFilename = "datasets/"+filename+".CSV"
	resultsFilename = "results/"+filename+("-combined" if combineByOrderDate else "")+"-x"+str(max(replicaNums))+".csv" 
	return simulateAuctions(replicaAuctions(replicaNums,
		torq.auctionsBySymbolDate(datasetFilename, combineByOrderDate)),
		resultsFilename)

def simulateBySymbol(filename, combineByOrderDate=False, agentNums=[100]):
	"""
	Treat all bidders for the same symbol, in ALL dates, as a distribution of values for that symbol.
	"""
	datasetFilename = "datasets/"+filename+".CSV"
	resultsFilename = "results/"+filename+("-combined" if combineByOrderDate else "")+"-r"+str(max(agentNums))+".csv" 
	resultsFilenameTemp = "results/"+filename+"-temp.csv" 
	results = DataFrame(columns=COLUMNS)
	print("\t{}".format(COLUMNS))

	for symbol,allTimeTraders in torq.auctionsBySymbol(datasetFilename, combineByOrderDate):
		date = 0
		for agentNum in agentNums:
			traders = [random.choice(allTimeTraders) for i in range(agentNum)]
			print("Simulating auction {}-{} with {} traders".format(symbol,date,len(traders)))
			totalBuyers = sum([t.isBuyer for t in traders])
			totalSellers = len(traders)-totalBuyers
			totalUnits = sum([t.totalUnits() for t in traders])
			maxUnitsPerTrader = max([t.totalUnits() for t in traders])   # maxUnitsPerTrader is denoted in the paper by m.
			stddev = np.sqrt(sum([t.totalUnits()**2 for t in traders]))
			(buyersWALRAS, sellersWALRAS, sizeWALRAS, gainWALRAS) = WALRAS(traders) # sizeWALRAS is denoted in the paper by k. 
			(sizeMIDALottery, gainMIDALottery, gainMIDALottery, sizeMIDAVickrey, tradersGainMIDAVickrey, totalGainMIDAVickrey) = MIDA(traders, Lottery=True, Vickrey=True)
			resultsRow = [
				(symbol,date),
				totalBuyers, totalSellers, totalBuyers+totalSellers, min(totalBuyers,totalSellers), totalUnits,
				maxUnitsPerTrader, stddev,
				buyersWALRAS, sellersWALRAS, sizeWALRAS,
				gainWALRAS, gainMIDALottery, tradersGainMIDAVickrey, totalGainMIDAVickrey]
			print("\t{}".format(resultsRow))
			results.loc[len(results)] = resultsRow
			results.to_csv(resultsFilenameTemp)
		results.to_csv(resultsFilename)
		os.remove(resultsFilenameTemp)
	return results

def plotBins(resultsFilename=None, filename=None, results=None, combineByOrderDate=False, replicaNums=[1]):
	if not results:
		if filename:
			resultsFilename = "results/"+\
				filename+\
				("-combined" if combineByOrderDate else "")+\
				"-x"+str(max(replicaNums))+\
				".csv"
		results = pd.read_csv(resultsFilename)
	results['Optimal market size'] = (results['Optimal buyers']+results['Optimal sellers']) / 2
	results['Normalized market size'] = results['Optimal units'] / (results['Max units per trader'])
	print(len(results), " auctions")
	results = results[results['Optimal gain']>0]
	print(len(results), " auctions with positive optimal gain")
	
	for field in ['MIDA-lottery', 'MIDA-Vickrey traders', 'MIDA-Vickrey total']:
		results[field+' ratio'] = results[field+' gain'] / results['Optimal gain']

	results_bins = results.groupby(pd.cut(results['Min total traders'],100)).mean()

	ys = ['MIDA-Vickrey traders ratio', 'MIDA-Vickrey total ratio',  'MIDA-lottery ratio']
	x = 'Optimal units' # 'Min total traders' #
	ax = plt.subplot(1, 1, 1)
	results_bins.plot(kind='scatter', x=x, y='MIDA-Vickrey total ratio', marker="^", color='b', ax=ax, legend=True)
	#ax = plt.subplot(2, 2, 2)
	results_bins.plot(kind='scatter', x=x, y='MIDA-Vickrey traders ratio', marker="v",  color='g', ax=ax, legend=True)
	#ax = plt.subplot(2, 2, 3)
	results_bins.plot(kind='scatter', x=x, y='MIDA-lottery ratio', color='r', marker="o",  ax=ax, legend=True)

	#ax = plt.subplot(1, 3, 2)
	#results_bins.plot(kind='scatter', x='Optimal units',y='MIDA total ratio', color='r', ax=ax)

	#ax = plt.subplot(1, 3, 3)
	#results_bins.plot(kind='scatter', x='Normalized market size',y='MIDA total ratio', color='r', ax=ax)

	#ax.legend().set_visible(False)
	plt.show()
	
def plotRandom(resultsFilename=None, xColumn='Min total traders', numOfAuctionsPerBin=1):
	results = pd.read_csv(resultsFilename)
	results['Optimal market size'] = (results['Optimal buyers']+results['Optimal sellers']) / 2
	results['Normalized market size'] = results['Optimal units'] / (results['Max units per trader'])
	print(len(results), " auctions")
	results = results[results['Optimal gain']>0]
	print(len(results), " auctions with positive optimal gain")
	
	for field in ['MIDA-lottery', 'MIDA-Vickrey traders', 'MIDA-Vickrey total']:
		results[field+' ratio'] = results[field+' gain'] / results['Optimal gain']

	results_bins = results.groupby(pd.cut(results[xColumn],numOfAuctionsPerBin)).mean()

	ys = ['MIDA-Vickrey traders ratio', 'MIDA-Vickrey total ratio',  'MIDA-lottery ratio']
	ax = plt.subplot(1, 1, 1)
	results_bins.plot(kind='scatter', x=xColumn, y='MIDA-Vickrey total ratio', marker="^", color='b', ax=ax, legend=True, title=resultsFilename)
	results_bins.plot(kind='scatter', x=xColumn, y='MIDA-Vickrey traders ratio', marker="v",  color='g', ax=ax, legend=True)
	results_bins.plot(kind='scatter', x=xColumn, y='MIDA-lottery ratio', color='r', marker="o", ax=ax, legend=True)
	print(ax.legend())
	plt.show()


### MAIN PROGRAM ###

createResults = False # True # 
replicaNums=[1]
MIDA.LOG = randomTradeWithExogeneousPrice.LOG = False

def torqSimulation():
	filename = "901101-910131-IBM-SOD" #"910121-910121-IBM-SOD" #  "901101-910131-SOD" #   "901101-910131-SOD-NORM" # 
	if createResults:
		#results1 = torqSimulationBySymbolDate(filename, combineByOrderDate=False,replicaNums=replicaNums)
		results2 = torqSimulationBySymbolDate(filename, combineByOrderDate=True,replicaNums=replicaNums)
		#results1 = simulateBySymbol(filename, combineByOrderDate=False, agentNums=range(300,30000,300))
		#results2 = simulateBySymbol(filename, combineByOrderDate=True, agentNums=range(300,30000,300))
		#plot(results=results1)
		plotBins(results=results2)
	else:
		#plot(filename=filename, combineByOrderDate=False,replicaNums=replicaNums)
		plotBins(filename=filename, combineByOrderDate=True,replicaNums=replicaNums)

def randomSimulation():
	numOfTraderss = range(100, 1000, 100)
	numOfUnitsPerTraders = range(1, 10, 1)
	meanValue = 500
	maxNoiseSizes = range(50, 500, 50)
	numOfAuctions = 10
	filenameTraders = "results/random-traders-{}units-{}noise.csv".format(numOfUnitsPerTraders[-1],maxNoiseSizes[-1])
	filenameUnits   = "results/random-units-{}traders-{}noise.csv".format(numOfTraderss[-1],maxNoiseSizes[-1])
	filenameNoise   = "results/random-noise-{}traders-{}units.csv".format(numOfTraderss[-1],numOfUnitsPerTraders[-1])
	filenameTradersAdd = "results/random-traders-{}units-{}noise-additive.csv".format(numOfUnitsPerTraders[-1],maxNoiseSizes[-1])
	filenameUnitsAdd   = "results/random-units-{}traders-{}noise-additive.csv".format(numOfTraderss[-1],maxNoiseSizes[-1])
	filenameNoiseAdd   = "results/random-noise-{}traders-{}units-additive.csv".format(numOfTraderss[-1],numOfUnitsPerTraders[-1])
	if createResults:
		simulateAuctions(randomAuctions(
			numOfAuctions, numOfTraderss, numOfUnitsPerTraders[-1:], meanValue, maxNoiseSizes[-1:]),
			filenameTraders)
		simulateAuctions(randomAuctions(
			numOfAuctions, numOfTraderss[-1:], numOfUnitsPerTraders, meanValue, maxNoiseSizes[-1:]),
			filenameUnits)
		simulateAuctions(randomAuctions(
			numOfAuctions, numOfTraderss[-1:], numOfUnitsPerTraders[-1:], meanValue, maxNoiseSizes),
			filenameNoise)
		simulateAuctions(randomAuctions(
			numOfAuctions, numOfTraderss, numOfUnitsPerTraders[-1:], meanValue, maxNoiseSizes[-1:],isAdditive=True),
			filenameTradersAdd)
		simulateAuctions(randomAuctions(
			numOfAuctions, numOfTraderss[-1:], numOfUnitsPerTraders, meanValue, maxNoiseSizes[-1:],isAdditive=True),
			filenameUnitsAdd)
		simulateAuctions(randomAuctions(
			numOfAuctions, numOfTraderss[-1:], numOfUnitsPerTraders[-1:], meanValue, maxNoiseSizes,isAdditive=True),
			filenameNoiseAdd)
	plotRandom(filenameTraders,"Optimal units",numOfAuctions)
	plotRandom(filenameUnits,"Max units per trader",numOfAuctions)
	plotRandom(filenameNoise,"Optimal units",numOfAuctions)
	plotRandom(filenameTradersAdd,"Optimal units",numOfAuctions)
	plotRandom(filenameUnitsAdd,"Max units per trader",numOfAuctions)
	plotRandom(filenameNoiseAdd,"Optimal units",numOfAuctions)

#torqSimulation()
randomSimulation()
