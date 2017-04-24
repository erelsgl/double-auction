/**
 * Some event handlers common to all webapps in this folder
 */


var setStatus = function(text) {
	$("#status").html(text);
}


$(document).ready(function() {

	window.canvas = document.getElementById("canvas"); // for export
	window.canvas.width  = 400;
	window.canvas.height = 400;

	window.svgpaper = SVG('svg');
	window.svgpaper.size(canvas.width,canvas.height);
	
	/**
	 * From a gist by OTM: https://gist.github.com/otm/379a3cdb572ac81d8c19#file-svg-to-img
	 */
	$(".export").click(function() {
		var data = new XMLSerializer().serializeToString(document.getElementById('svg'));
		var ctx = window.canvas.getContext("2d");
	
		var DOMURL = self.URL || self.webkitURL || self;
		var img = new Image();
		var svg = new Blob([data], {type: "image/svg+xml;charset=utf-8"});
		var url = DOMURL.createObjectURL(svg);
		img.onload = function() {
			ctx.drawImage(img, 0, 0);
			DOMURL.revokeObjectURL(url);
		};
		img.src = url;
	});

	$(".interrupt").click(function() {
		window.solver.interrupt();
	});
	
	window.updatePermaLink = function(queryString) {
		var permalink = location.host+"/" + location.pathname+"?" + queryString;
		permalink = permalink.replace(/[?]+/g,"?");
		permalink = permalink.replace(/[/]+/g,"/");
		permalink = location.protocol+"//"+permalink;
		document.getElementById('permalink').href = permalink;
	}
	
})
