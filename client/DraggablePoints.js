/**
 * Defines an array of points that can be dragged.
 * Uses svg.js and svg.draggable.js
 * @author Erel Segal-Halevi
 * @since 2013-12-28
 */

var RADIUS = 10;

function DraggablePoints(svgpaper, onDragEnd) {
	if (!svgpaper)
		throw new Error("svgpaper is "+svgpaper)
	var points = [];
	points.byColor = {};
	

	// Add a new point ({x,y})
	points.add = function(point, color) {
		points.push(point);
		if (!points.byColor[color]) {
			points.byColor[color] = [];
			points.byColor[color].color = color;
		}
		points.byColor[color].push(point);
		point.color = color;
		
		point.drawOnPaper = function() {
			var attr = {
				stroke: this.color||'blue',
				fill: this.color||'blue',
			}
			this.circle = svgpaper.circle(RADIUS).attr('cx',this.x).attr('cy',this.y).attr(attr);
		};

		point.drawOnPaper();
		
		point.removeFromPaper = function() {
			this.circle.remove();
			delete this.circle;
		}

		point.remove = function() {
			this.removeFromPaper();
			var index = points.indexOf(this);
			if (index>=0)
				points.splice(index,1);
			index = points.byColor[this.color].indexOf(this);
			if (index>=0) {
				points.byColor[this.color].splice(index,1);
				if (points.byColor[this.color].length==0)
					delete points.byColor[this.color];
			}
		};

		point.move = function (x,y) {
			this.x = x;
			this.y = y;
			this.circle.attr('cx', x);
			this.circle.attr('cy', y);
		}
		
		if (!point.circle) {
			console.dir(point);
			throw new Error("point.circle not defined")
		}

		point.circle.draggable();

		point.circle.dragend = function(delta, event) {
			point.x = point.circle.attr('cx');
			point.y = point.circle.attr('cy');
			if (point.x<0 || point.y<0)
				point.remove();
			onDragEnd();
		};
	}
	
	// Re-draw all the points
	points.redraw = function() {
		for (var p=0; p<this.length; ++p)
			this[p].removeFromPaper();
		for (var p=0; p<this.length; ++p)
			this[p].drawOnPaper();
	}
	
	points.randomize = function(width, height) {
		for (var i=0; i<this.length; ++i) {
			var p = this[i];
			p.move(Math.floor(Math.random()*width), Math.floor(Math.random()*height)); 
		}
		onDragEnd();
	}
	
	points.shuffleYValues = function(width, height) {
		yvalues = _.chain(points).pluck("y").shuffle().value();
		for (var i=0; i<yvalues.length; ++i) {
			var p = points[i];
			p.move(p.x, yvalues[i]);
		}
		onDragEnd();
	}
	
	points.refresh = function() {
		onDragEnd();
	}

	//remove all points from the SVG paper:
	points.clear = function() {
		for (var p=0; p<this.length; ++p)
			this[p].removeFromPaper();
		this.length = 0;
		this.byColor = {};
		onDragEnd();
	}

	// Return a string representation of the x,y values of the points
	points.toString = function() {
		var s = "";
		for (var p=0; p<points.length; ++p) {
			if (s.length>0)
				s+=":";
			s += points[p].x + "," + points[p].y+","+points[p].color;
		}
		return s;
	}

	// Fill the points array from the given string (created by toString)
	//     or a default (if there is no string).
	points.fromString = function(s) {
		var pointsStrings = s.split(/:/);
		for (var i=0; i<pointsStrings.length; ++i) {
			var xyc = pointsStrings[i].replace(/\s*/g,"").split(/,/);
			if (xyc.length<2) continue;
			if (!xyc[2] || xyc[2]=='undefined') xyc[2]="blue";
			points.add({x:parseFloat(xyc[0]), y:parseFloat(xyc[1])}, xyc[2]);
		}
	}

	return points;
}

