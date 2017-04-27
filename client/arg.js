/* A simple module for handling query arguments. 
  Based on the arg.js.v1.1.min.js library. 
	
	Author: Erel Segal-Halevi.
	License: Public domain.
*/
	
function ArgFromField(argName) {
	var argValue = decodeURIComponent(Arg(argName)).replace(/[+]/g," ")
	var field = $("#"+argName)
	var defaultValue = field.val()
	//console.log(argValue)
	if (argValue != 'undefined') {
		//console.log("defined")
		field.val(argValue)
		return argValue
	} else {
		//console.log("undefined")
		return defaultValue;
	}
}
