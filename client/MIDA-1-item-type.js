
/**
 * Extract one or two numbers from a given string, ignoring other chars inside.
 */
var regexp = /(\d+)[^0-9]*(\d*)/i;
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
 * @param bias will be added to each valuation.  Default = 0
 * @param noise*i will be added to each valuation i. Default = 0
 * @return an array of values.
 */
function valuesFromString(string, bias, noise) {
	if (!bias) bias = 0;
	if (!noise) noise = 0;
	var parts = string.split(",");
	var values = []
	for (i in parts) {
		var [quantity,value] = numPair(parts[i], /*default quantity=*/1);
		for (j=0;  j<quantity;  j++) {
			var actualValue = value + bias + j*noise;
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
	buyers.shift();  buyers.pop();
	sellers.shift(); sellers.pop();
	//return 0.999 * minPrice + 0.001 * maxPrice  // slightly above min price
	return minPrice
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
	var [leftBuyers,rightBuyers] = randomHalving(buyers)
	var [leftSellers,rightSellers] = randomHalving(sellers)
	var optimalPrice = equilibriumPrice1D(buyers,sellers)
	var leftPrice = equilibriumPrice1D(leftBuyers,leftSellers)
	var rightPrice = equilibriumPrice1D(rightBuyers,rightSellers)
	var optimalGain = gainFromTrade(buyers, sellers, optimalPrice)
	var leftGain = gainFromTrade(leftBuyers,leftSellers,rightPrice)
	var rightGain = gainFromTrade(rightBuyers,rightSellers,leftPrice)
	var totalGain = leftGain+rightGain
	
	return {
		leftMarket:    {buyers: leftBuyers.join(" "), sellers: leftSellers.join(" "), price: leftPrice, otherPrice: rightPrice, gain: leftGain}
		,
		rightMarket: {buyers: rightBuyers.join(" "), sellers: rightSellers.join(" "), price: rightPrice, otherPrice: leftPrice, gain: rightGain}
		,
		optimalMarket: {price: optimalPrice, gain: optimalGain}
		,
		gain: totalGain, 
		competitiveRatio: totalGain/optimalGain
	}
}

/**
 * Run MIDA several iterations. Return the median result, in terms of competitive ratio.
 */
function MIDA_median(buyers, sellers, iterations) {
	results = []
	for (var i=0; i<iterations; i++) {
		results.push(MIDA(buyers,sellers));
	}
	results.sort(function(a,b){a.competitiveRatio-b.competitiveRatio});
	var medianIndex = (iterations/2)|0
	return results[medianIndex];
}

//if (typeof module != 'undefined' && !module.parent) {
if (typeof require != 'undefined' && require.main==module) {
	/*
	console.log(numPair("a  20 of 1000  d",1))
	console.log(numPair(" 1000 ",1))
	*/
	
	console.log(valuesFromString("a  20 of 1000  d", 1, 2))
	
	var buyers = valuesFromString("10 of 100", 0.000001)
	var sellers = valuesFromString("1 of 1, 99 of 99", 0.000001)
	console.log(MIDA(buyers,sellers))
	console.log(MIDA(buyers,sellers))
	console.log(MIDA(buyers,sellers))
	console.log(MIDA(buyers,sellers))
	console.log(MIDA(buyers,sellers))
	console.log("median:")
	console.log(MIDA_median(buyers,sellers,100))
	
	/*
	console.log(randomHalving(agents))
	console.log(randomHalving(agents))
	console.log(randomHalving(agents))
	*/
	
	/*
	console.log(equilibriumPrice1D([7,8,9], [1,2,3]))  // 3+
	console.log(equilibriumPrice1D([7,8,9,10], [1,2,3]))  // 7+ 	
	console.log(equilibriumPrice1D([6,7,8,9], [1,2,3]))  // 6+ 	
	console.log(equilibriumPrice1D([3,7,8,9], [1,2,3]))  // 3+ 	
	console.log(equilibriumPrice1D([2,3,7,8,9], [1,2,3]))  // 3+ 	
	console.log(equilibriumPrice1D([9], [1,2,3]))  // 1+ 
	console.log(equilibriumPrice1D([2], [1,2,3]))  // 1+ 
	console.log(equilibriumPrice1D([1,2,3],[7,8,9]))  // 3+
	console.log(equilibriumPrice1D([1,2,100],[99,200,201]))  // 3+
	*/
}
