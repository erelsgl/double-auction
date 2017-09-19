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
	'Total buyers', 'Total sellers', 'Total traders', 'Min total traders', 'Total units', 
	'Max units per trader', 'Min units per trader', 'Normalized max units per trader', 'stddev',
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


def simulateAuctions(auctions:list, resultsFilename:str, keyColumns:list):
	"""
	Simulate the auctions in the given generator.
	"""
	columns = keyColumns+COLUMNS
	results = DataFrame(columns=columns)
	print("\t{}".format(columns))
	resultsFilenameTemp = resultsFilename+".temp"
	for auctionID,traders in auctions:
		print("Simulating auction {} with {} traders".format(auctionID,len(traders)))
		totalBuyers = sum([t.isBuyer for t in traders])
		totalSellers = len(traders)-totalBuyers
		unitsPerTrader = [t.totalUnits() for t in traders]
		maxUnitsPerTrader = max(unitsPerTrader)
		minUnitsPerTrader = min(unitsPerTrader)
		stddev = np.sqrt(sum([t.totalUnits()**2 for t in traders]))
		(buyersWALRAS, sellersWALRAS, sizeWALRAS, gainWALRAS) = WALRAS(traders)
		(sizeMIDALottery, gainMIDALottery, gainMIDALottery, sizeMIDAVickrey, tradersGainMIDAVickrey, totalGainMIDAVickrey) = MIDA(traders, Lottery=True, Vickrey=True)
		resultsRow = [
			*auctionID,
			totalBuyers, totalSellers, totalBuyers+totalSellers, min(totalBuyers,totalSellers), sum(unitsPerTrader),
			maxUnitsPerTrader, minUnitsPerTrader, maxUnitsPerTrader/max(1,minUnitsPerTrader), stddev,
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
		resultsFilename, keyColumns=("symbol","date"))

def torqSimulateBySymbol(filename, combineByOrderDate=False, agentNums=[100]):
	"""
	Treat all bidders for the same symbol, in ALL dates, as a distribution of values for that symbol.
	"""
	datasetFilename = "datasets/"+filename+".CSV"
	resultsFilename = "results/"+filename+("-combined" if combineByOrderDate else "")+"-s"+str(max(agentNums))+".csv" 
	return simulateAuctions(sampleAuctions(agentNums,
		torq.auctionsBySymbol(datasetFilename, combineByOrderDate)),
		resultsFilename, keyColumns=("symbol",))


YLABEL = 'MIDA GFT divided by maximum GFT'


def plotBins(filename, resultsFilename=None, combineByOrderDate=False, replicaNums=None, agentNums=None, numOfBins=10, ax=None, title=None):
	if not ax:
		ax = plt.subplot(1, 1, 1)
	if resultsFilename:
		pass
	elif replicaNums:
		resultsFilename = "results/"+\
			filename+\
			("-combined" if combineByOrderDate else "")+\
			"-x"+str(max(replicaNums))+\
			".csv"
	elif agentNums:
		resultsFilename = "results/"+\
			filename+\
			("-combined" if combineByOrderDate else "")+\
			"-s"+str(max(agentNums))+\
			".csv"
	else:
		raise(Error("cannot calculate resultsFilename"))
	if not title:
		title = resultsFilename

	results = pd.read_csv(resultsFilename)
	results['Optimal market size'] = (results['Optimal buyers']+results['Optimal sellers']) / 2
	results['Normalized market size'] = results['Optimal units'] / (results['Max units per trader'])
	print(len(results), " auctions")
	results = results[results['Optimal gain']>0]
	print(len(results), " auctions with positive optimal gain")
	
	for field in ['MIDA-lottery', 'MIDA-Vickrey traders', 'MIDA-Vickrey total']:
		results[field+' ratio'] = results[field+' gain'] / results['Optimal gain']


	ys = ['MIDA-Vickrey traders ratio', 'MIDA-Vickrey total ratio',  'MIDA-lottery ratio']
	x = 'Optimal units' # 'Min total traders' #
	results_bins = results.groupby(pd.cut(results[x],numOfBins)).mean()

	results_bins.plot(kind='scatter', x=x, y='MIDA-Vickrey total ratio', marker="^", color='b', ax=ax, legend=True, title=title)
	results_bins.plot(kind='scatter', x=x, y='MIDA-Vickrey traders ratio', marker="v",  color='g', ax=ax, legend=True, title=title)
	results_bins.plot(kind='scatter', x=x, y='MIDA-lottery ratio', color='r', marker="o",  ax=ax, legend=True, title=title)
	plt.ylabel(YLABEL); 

def plotRandom(resultsFilename=None, xColumn='Min total traders', numOfBins=10, ax=None, title=None):
	if not ax:
		ax = plt.subplot(1, 1, 1)
	if not title:
		title = resultsFilename
	results = pd.read_csv(resultsFilename)
	results['Optimal market size'] = (results['Optimal buyers']+results['Optimal sellers']) / 2
	results['Normalized market size'] = results['Optimal units'] / (results['Max units per trader'])
	print(len(results), " auctions")
	results = results[results['Optimal gain']>0]
	print(len(results), " auctions with positive optimal gain")
	
	for field in ['MIDA-lottery', 'MIDA-Vickrey traders', 'MIDA-Vickrey total']:
		results[field+' ratio'] = results[field+' gain'] / results['Optimal gain']

	results_bins = results.groupby(pd.cut(results[xColumn],numOfBins)).mean()

	ys = ['MIDA-Vickrey traders ratio', 'MIDA-Vickrey total ratio',  'MIDA-lottery ratio']
	results_bins.plot(kind='scatter', x=xColumn, y='MIDA-Vickrey total ratio', marker="^", color='b', ax=ax, legend=True, title=title)
	results_bins.plot(kind='scatter', x=xColumn, y='MIDA-Vickrey traders ratio', marker="v",  color='g', ax=ax, legend=True)
	results_bins.plot(kind='scatter', x=xColumn, y='MIDA-lottery ratio', color='r', marker="o", ax=ax, legend=True)
	plt.ylabel(YLABEL); 
	print(ax.legend())


### MAIN PROGRAM ###

MIDA.LOG = randomTradeWithExogeneousPrice.LOG = False

def torqSimulation():
	numOfTraderss=list(range(100,1000,100))*10
	filename = "901101-910131-SOD" #"910121-910121-IBM-SOD" #  "901101-910131-SOD" #   "901101-910131- SOD-NORM" # 
	if createResults:
		#torqSimulateBySymbol(filename, combineByOrderDate=False, agentNums=agentNums)
		torqSimulateBySymbol(filename, combineByOrderDate=True, agentNums=numOfTraderss)
		torqSimulateBySymbol(filename+"-NORM", combineByOrderDate=True, agentNums=numOfTraderss)
	numOfBins = 10
	#plotBins(filename=filename, combineByOrderDate=False, agentNums=numOfTraderss, numOfBins=numOfBins)
	plotBins(filename=filename, combineByOrderDate=True, agentNums=numOfTraderss, numOfBins=numOfBins,
			ax = plt.subplot(2,1,1))
	plt.xlabel("")
	plotBins(filename=filename+"-NORM", combineByOrderDate=True, agentNums=numOfTraderss, numOfBins=numOfBins,
			ax = plt.subplot(2,1,2))
	plt.show()

def randomSimulation():
	numOfTraderss = range(20000, 420000, 20000)
	numOfUnitsPerTraders = [1,10,100,10000,100000,1000000,1000]
	meanValue = 500
	maxNoiseSizes = [50,100,150,200,300,350,400,450,500,250]
	numOfAuctions = 10
	filenameTraders = "results/random-traders-{}units-{}noise.csv".format(numOfUnitsPerTraders[-1],maxNoiseSizes[-1])
	filenameUnitsFixedTraders   = "results/random-units-{}traders-{}noise.csv".format(numOfTraderss[-1],maxNoiseSizes[-1])
	filenameUnitsFixedVirtual   = "results/random-units-{}virtual-{}noise.csv".format(numOfTraderss[-1],maxNoiseSizes[-1])
	filenameNoise   = "results/random-noise-{}traders-{}units.csv".format(numOfTraderss[-1],numOfUnitsPerTraders[-1])
	# filenameTradersAdd = "results/random-traders-{}units-{}noise-additive.csv".format(numOfUnitsPerTraders[-1],maxNoiseSizes[-1])
	# filenameUnitsAdd   = "results/random-units-{}traders-{}noise-additive.csv".format(numOfTraderss[-1],maxNoiseSizes[-1])
	# filenameNoiseAdd   = "results/random-noise-{}traders-{}units-additive.csv".format(numOfTraderss[-1],numOfUnitsPerTraders[-1])
	if createResults:
		keyColumns=("numOfTraders","numOfUnitsPerTrader","maxNoiseSize","isAdditive")
		# simulateAuctions(randomAuctions(
		# 	numOfAuctions, numOfTraderss, numOfUnitsPerTraders[-1:], meanValue, maxNoiseSizes[-1:], isAdditive=False, fixedNumOfVirtualTraders=True),
		# 	filenameTraders, keyColumns=keyColumns)
		# simulateAuctions(randomAuctions(
		# 	numOfAuctions, numOfTraderss[-1:], numOfUnitsPerTraders, meanValue, maxNoiseSizes[-1:], isAdditive=False, fixedNumOfVirtualTraders=True),
		# 	filenameUnitsFixedVirtual, keyColumns=keyColumns)
		simulateAuctions(randomAuctions(
			numOfAuctions, [100], numOfUnitsPerTraders, meanValue, maxNoiseSizes[-1:], isAdditive=False, fixedNumOfVirtualTraders=False),
			filenameUnitsFixedTraders, keyColumns=keyColumns)
		simulateAuctions(randomAuctions(
			numOfAuctions, numOfTraderss[-1:], numOfUnitsPerTraders[-1:], meanValue, maxNoiseSizes, isAdditive=False, fixedNumOfVirtualTraders=True),
			filenameNoise, keyColumns=keyColumns)
		# simulateAuctions(randomAuctions(
		# 	numOfAuctions, numOfTraderss, numOfUnitsPerTraders[-1:], meanValue, maxNoiseSizes[-1:],isAdditive=True, fixedNumOfVirtualTraders=True),
		# 	filenameTradersAdd, keyColumns=keyColumns)
		# simulateAuctions(randomAuctions(
		# 	numOfAuctions, numOfTraderss[-1:], numOfUnitsPerTraders, meanValue, maxNoiseSizes[-1:],isAdditive=True, fixedNumOfVirtualTraders=True),
		# 	filenameUnitsAdd, keyColumns=keyColumns)
		# simulateAuctions(randomAuctions(
		# 	numOfAuctions, numOfTraderss[-1:], numOfUnitsPerTraders[-1:], meanValue, maxNoiseSizes,isAdditive=True, fixedNumOfVirtualTraders=True),
		# 	filenameNoiseAdd, keyColumns=keyColumns)
	numOfBins = 10
	plotRandom(filenameTraders,"numOfTraders",numOfBins, plt.subplot(1,1,1), 
		title="m={}, noise={}".format(numOfUnitsPerTraders[-1],maxNoiseSizes[-1]))
	# plt.ylabel(YLABEL); plt.xlabel('')
	plt.show()
	# plotRandom(filenameTraders,"Optimal units",numOfBins, plt.subplot(2,4,2), 
	# 	title="m={}, noise={}".format(numOfUnitsPerTraders[-1],maxNoiseSizes[-1]))
	# plt.ylabel(''); plt.xlabel('')
	# plt.show()
	plotRandom(filenameUnitsFixedVirtual,"numOfUnitsPerTrader",numOfBins, plt.subplot(1,1,1), 
		title="total units={}, noise={}".format(numOfTraderss[-1],maxNoiseSizes[-1]))
	# plt.ylabel(''); plt.xlabel('')
	plt.show()
	plotRandom(filenameUnitsFixedTraders,"numOfUnitsPerTrader",numOfBins, plt.subplot(1,1,1), 
		title="traders={}, noise={}".format(numOfTraderss[-1],maxNoiseSizes[-1]))
	# plt.ylabel(''); plt.xlabel('')
	plt.show()
	plotRandom(filenameNoise,"maxNoiseSize",numOfBins, plt.subplot(1,1,1), 
		title="traders={}, m={}".format(numOfTraderss[-1],numOfUnitsPerTraders[-1]))
	# plt.ylabel(''); plt.xlabel('')
	plt.show()
	
	# plotRandom(filenameTradersAdd,"numOfTraders",numOfBins, plt.subplot(2,4,5), 
	# 	title="m={}, noise={}, additive".format(numOfUnitsPerTraders[-1],maxNoiseSizes[-1]))
	# plt.ylabel(YLABEL)
	# plotRandom(filenameTradersAdd,"Optimal units",numOfBins, plt.subplot(2,4,6), 
	# 	title="m={}, noise={}, additive".format(numOfUnitsPerTraders[-1],maxNoiseSizes[-1]))
	# plt.ylabel('')
	# plotRandom(filenameUnitsAdd,"numOfUnitsPerTrader",numOfBins, plt.subplot(2,4,7), 
	# 	title="agents={}, noise={}, additive".format(numOfTraderss[-1],maxNoiseSizes[-1]))
	# plt.ylabel('')
	# plotRandom(filenameNoiseAdd,"maxNoiseSize",numOfBins, plt.subplot(2,4,8), 
	# 	title="agents={}, m={}, additive".format(numOfTraderss[-1],numOfUnitsPerTraders[-1]))
	# plt.ylabel('')


createResults = True # False # 

#torqSimulation()
randomSimulation()
