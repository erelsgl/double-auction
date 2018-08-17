#!python3

"""
Experiments with a new multi-unit double-auction mechanism.
"""

from random_datasets import randomValuations, randomAuction
from traders import Trader, virtualTraders, virtualTradersWithIndices, winningAndLosingTraders
from operator import itemgetter
from collections import defaultdict

import numpy as np

def newMUDA(buyers:list, numOfItems:int):
    (vbuyers,vsellers) = virtualTraders(buyers)
    # print("vbuyers",vbuyers)
    vbuyers_sorted_by_1 = sorted(vbuyers, key=itemgetter(1), reverse=True)
    print("vbuyers_sorted_by_1",vbuyers_sorted_by_1)
    vbuyers_winning = vbuyers_sorted_by_1[0:numOfItems]
    print("vbuyers_winning",vbuyers_winning)
    mapIndexToQuantity = defaultdict(int)
    for (_, value, index) in vbuyers_winning:
        mapIndexToQuantity[index] += 1

    print("mapIndexToQuantity",mapIndexToQuantity)
    buyers_sorted_by_2 = sorted(buyers, key=lambda t:t.valueOf(numBundles=2), reverse=True)
    print("buyers_sorted_by_2",buyers_sorted_by_2)

    # calculate price for 2 units:
    price_2 = 0
    for b in buyers_sorted_by_2:
        if mapIndexToQuantity.get(b.index,0)==0:
            price_2 = b.valueOf(numBundles=2)
            break
    print("price_2", price_2)

    # calculate price for 1 units:
    price_1 = 0
    for b in vbuyers_sorted_by_1:
        if mapIndexToQuantity.get(b[2],0)==0:
            price_1 = b[1]
            break
    print("price_1", price_1)

    for (index,quantity) in mapIndexToQuantity.items():
        b = buyers[index]
        value_1 = b.valueOf(1)
        utility_1 = value_1 - price_1
        value_2 = b.valueOf(2)
        utility_2 = value_2 - price_2
        print(index,":   ","quantity",quantity,"  value_1",value_1,"utility_1",utility_1,"  value_2",value_2,"utility_2",utility_2)
        if utility_1 < utility_2 and quantity==1:
            print("  WARNING: utility_1<utility_2 but quantity=1")
        if utility_1 > utility_2 and quantity==2:
            print("  WARNING: utility_1>utility_2 but quantity=2")

    return "In construction"




if __name__ == "__main__":
    # seed = 47585  # bad for "<1,<2"
    # seed = 464410 # bad for "!=1,!=2"
    # seed = 50193  # bad for ">0,>0"
    seed = int(np.round(np.random.random()*1000000))
    print("seed",seed)
    np.random.seed(seed)
    numOfTraders = 6
    traders = []
    for i in range(numOfTraders):
        traders.append(Trader.Buyer(randomValuations(
            minNumOfUnits=1, maxNumOfUnits=2, meanValue=10, maxNoiseSize=10, round=True, index=i), index=i))
    print("traders",traders)
    print(newMUDA(traders, numOfItems=5))

