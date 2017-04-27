/**
 * @param demand
 * @param supply
 * @returns {String} a description of whether we have excess demand or supply.
 */
function excessString(demand,supply) {
	if (demand>supply)
		return "excess demand";
	else if (demand<supply)
		return "excess supply";
	else
		return "equilibrium";
}


function demandSupplyString(demand,supply) {
	return 	"<b>"+excessString(demand,supply)+"</b>: "+
		"demand="+demand+", supply="+supply;
}


/**
 * @param priceX
 * @param priceY
 * @param buyersUtilities {Array} utility vectors of buyers [{x:,y:},...].
 * @returns {Array} [demandForX, demandForY, welfareFromX, welfareFromY];
 */
function demandsOfGivenBuyers(buyersUtilities, priceX, priceY) {
	var demandForX = 0, demandForY = 0, welfareFromX = 0, welfareFromY = 0;
	for (var i=0; i<buyersUtilities.length; ++i) {
		var utility=buyersUtilities[i];
		var netUtilityX = utility.x-priceX;
		var netUtilityY = utility.y-priceY;
		if (netUtilityX >= 0 && netUtilityX >= netUtilityY) {
			demandForX++;
			welfareFromX += utility.x;
		} else if (netUtilityY >= 0 && netUtilityY > netUtilityX) {
			demandForY++;
			welfareFromY += utility.y;
		}
	}
	return [demandForX, demandForY, welfareFromX, welfareFromY];
}

/**
 * @param priceX
 * @param priceY
 * @param sellersUtilities {Array} utility vectors of unit-demand sellers [{x:,y:},...].
 * @returns {Array} [supplyOfX, supplyOfY, welfareFromX, welfareFromY];
 */
function suppliesOfGivenSellers(sellersUtilities, priceX, priceY) {
	var supplyOfX = 0, supplyOfY = 0, welfareFromX = 0, welfareFromY = 0;
	for (var i=0; i<sellersUtilities.length; ++i) {
		var sellX = true, sellY = true;
		var utility=sellersUtilities[i];
		var netUtilityX = utility.x-priceX;
		var netUtilityY = utility.y-priceY;
		if (netUtilityX >= 0 && netUtilityX >= netUtilityY) 
			sellX=false;
		else if (netUtilityY >= 0 && netUtilityY > netUtilityX) 
			sellY=false;
		
		var utilityAfterX = utility.x;
		var utilityAfterY = utility.y;
		if (sellX) 	supplyOfX++;
		if (sellY) 	supplyOfY++;
		
		if (sellX&&sellY) {
			if (utility.x>utility.y) welfareFromX -= utility.x;
			else                     welfareFromY -= utility.y;
		} 
		else if (sellX)            welfareFromX -= Math.min(0,utility.x-utility.y);
		else if (sellY)            welfareFromY -= Math.min(0,utility.y-utility.x);
	}
	return [supplyOfX, supplyOfY, welfareFromX, welfareFromY];
}

/**
 * @returns {Array} [supplyOfX, supplyOfY, gainFromSellX, gainFromSellY];
 */
function suppliesOfThresholdSellers(maxSupplyOfX,maxSupplyOfY,supplyValueX,supplyValueY,priceX,priceY) {
	return [
		(priceX>=supplyValueX? maxSupplyOfX: 0),
		(priceY>=supplyValueY? maxSupplyOfY: 0),
		(priceX>=supplyValueX? -supplyValueX*maxSupplyOfX: 0),
		(priceY>=supplyValueY? -supplyValueY*maxSupplyOfY: 0)
		];
}


/**
 * @returns {Array} [demandForX, demandForY, gainFromBuyX, gainFromBuyY];
 */
function demandsOfThresholdBuyers(demandForX,demandForY,demandValueX,demandValueY,priceX,priceY) {
	return [
		(priceX<=demandValueX? demandForX: 0),
		(priceY<=demandValueY? demandForY: 0),
		(priceX<=demandValueX? demandValueX*demandForX: 0),
		(priceY<=demandValueY? demandValueY*demandForY: 0),
		];
}


/**
 * @param demandsAtGivenPrices - function that accepts (priceX,priceY) and returns an array [demandX,demandY] at these prices.
 * @param suppliesAtGivenPrices - function that accepts (priceX,priceY) and returns an array [supplyX,supplyY] at these prices.
 * @returns {Array} [priceX,priceY]
 */
function calcMinWalrasianPrice(demandsAtGivenPrices,suppliesAtGivenPrices) {
// Implement the English auction (Gul & Staccheti, 2000).
	var priceX = 0
	  , priceY = 0;
	for (;;) {
		var demands = demandsAtGivenPrices(priceX,priceY);
		var supplies = suppliesAtGivenPrices(priceX,priceY)
		var incPriceX = (demands[0]>supplies[0]);
		var incPriceY = (demands[1]>supplies[1]);
		if (!incPriceX && !incPriceY) break;
		priceX += incPriceX;
		priceY += incPriceY;
	}
	return [priceX,priceY];
}

/**
 * Extract one or two numbers from a given string, ignoring other chars inside.
 */
var regexp = /(\d+)[a-z ]*(\d*)/i;
function numPair(string, defaultFirstValue) {
	var matches = regexp.exec(string);
	if (!matches) {
		return [defaultFirstValue,defaultFirstValue]
	}
	if (matches[2]) {
		return [parseInt(matches[1]),parseInt(matches[2])]
	} else {
		return [defaultFirstValue, parseInt(matches[1])]
	}
}

/**
 * @param string a comma-separated string of agents' valuations  with quantities. E.g: "99 of 100, 1 of 1" means "99 buyers of value $100 and one buyer of value $1".
 * @param noise how much noise to add to the valuations. Default = 0
 * @return an array
 */
function valuesFromString(string, noise) {
	if (!noise) noise = 0;
	var parts = string.split(",");
	var values = []
	for (i in parts) {
		var [quantity,value] = numPair(parts[i], /*default quantity=*/1);
		for (j=0;  j<quantity;  j++) {
			var actualValue = value + j*noise;
			values.push(actualValue);
		}
	}
	return values
}

/**
 * randomly create the given array to two arrays: [left, right], such that each item has probability 1/2 to be in each side.
 */
function randomHalving(array) {
	var left = [], right = [];
	for (i=0; i<array.length; i++) {
		if (Math.random() > 0.5) {
			left.push(array[i])
		} else {
			right.push(array[i])
		}
	}
	return [left,right]
}

// From http://stackoverflow.com/a/2450976/827927
function shuffle(array) {
  var currentIndex = array.length, temporaryValue, randomIndex;

  // While there remain elements to shuffle...
  while (0 !== currentIndex) {

    // Pick a remaining element...
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex -= 1;

    // And swap it with the current element.
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }

  return array;
}

/**
 * Calculate an equilibrium-price in a single-item-type single-unit market.
 */
var ascending = function(a,b){return a-b}
var descending = function(a,b){return b-a}
function equilibriumPrice1D (buyers, sellers) {
	buyers.sort(descending);
	sellers.sort(ascending); // sort sellers by ascending order
	if (buyers.length==0 && sellers.length==0) {
		return 0;  // arbitrary default value
	}
	buyers.unshift(Infinity); buyers.push(0);  // dummy last value
	sellers.unshift(0);       sellers.push(Infinity);  // dummy last value
	var i=0; 
	while (buyers[i] > sellers[i]) i++;
	// HERE: buyers[i] <= sellers[i]
	var maxPrice = Math.min(sellers[i],buyers[i-1])
	var minPrice = Math.max(sellers[i-1],buyers[i])
	return 0.999 * minPrice + 0.001 * maxPrice  // slightly above min price
}

/**
 * The gain-from-trade with the given buyers, sellers and price,
 *  where excess demand/supply is handled by random permutation.
 */
function gainFromTrade(buyers, sellers, price)  {
	var interestedBuyers = []
	var interestedSellers = []
	for (var i in buyers) {
		if (buyers[i] > price)
			interestedBuyers.push(buyers[i])
	}
	for (var i in sellers) {
		if (sellers[i] < price)
			interestedSellers.push(sellers[i])
	}
	shuffle(interestedSellers)
	shuffle(interestedBuyers)
	var gain = 0
	for (var i = 0 ; i<interestedSellers.length && i<interestedBuyers.length; i++) {
		gain += (interestedBuyers[i] - interestedSellers[i])
	}
	return gain
}

function MIDA(buyers, sellers) {
	[leftBuyers,rightBuyers] = randomHalving(buyers);
	[leftSellers,rightSellers] = randomHalving(sellers);
}

//try {
	if (!module.parent) {
		console.log(numPair("a  20 of 1000  d",1))
		console.log(numPair(" 1000 ",1))
		
		var agents = valuesFromString("20 of 100, 1 of 99, 98", 0.000001)
		//console.log(agents)
		//console.log(randomHalving(agents))
		//console.log(randomHalving(agents))
		//console.log(randomHalving(agents))
		
		console.log(equilibriumPrice1D([7,8,9], [1,2,3]))  // 3+
		console.log(equilibriumPrice1D([7,8,9,10], [1,2,3]))  // 7+ 	
		console.log(equilibriumPrice1D([6,7,8,9], [1,2,3]))  // 6+ 	
		console.log(equilibriumPrice1D([3,7,8,9], [1,2,3]))  // 3+ 	
		console.log(equilibriumPrice1D([2,3,7,8,9], [1,2,3]))  // 3+ 	
		console.log(equilibriumPrice1D([9], [1,2,3]))  // 1+ 
		console.log(equilibriumPrice1D([2], [1,2,3]))  // 1+ 
		console.log(equilibriumPrice1D([1,2,3],[7,8,9]))  // 3+
		console.log(equilibriumPrice1D([1,2,100],[99,200,201]))  // 3+
	}
//} catch (e) {}
