
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
