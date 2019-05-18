"use strict";

var page = require('webpage').create();
var fs = require('fs');
var classnames = ["Accidental","Arpeggio","Articulation","BarLine","Beam","Bracket","Breath","ChordLine","Clef","Dynamic","Fingering",
"FretDiagram","GlissandoSegment","HairpinSegment","Harmony","Hook","InstrumentChange","InstrumentName","Jump","KeySig","LedgerLine",
"Lyrics","LyricsLineSegment","Marker","Note","NoteDot","OttavaSegment","Page","PedalSegment","RehearsalMark","Rest","SlurSegment","StaffLines","StaffText"
,"Stem","StemSlash","Symbol","Tempo","Text","TextLineSegment","TimeSig","Tremolo","TrillSegment","Tuplet","VoltaSegment"];


function listDir(dirname) {
	var filenames = [];
	var all_svg = fs.list('svg');
	for (var idx = 0; idx < all_svg.length; ++idx) {
		var filename = all_svg[idx];
		if (filename.length > 5) {
			filenames.push(filename);
		}
	}
	return filenames;
}


function pprintBBox(boxes, filename) {
	var lines = [];
	for (var i = 0; i < boxes.length; ++i) {
		lines.push(boxes[i].join(','));
	}
	var content = lines.join('\n');
	fs.write('txt/' + filename.replace('.svg', '.txt'), content)
	//console.log(content)
}

function measureBBox(filename, classnames) {
	page.open('http://localhost:8888/' + filename, function() {
		var bbox = page.evaluate(function(classnames) {
			var boxes = [];	
			var client = document.documentElement.getClientRects()[0];
			var height = client.height
			var width =client.width
			for (var idx = 0; idx < classnames.length; ++idx) {
				var classname = classnames[idx];
				console.debug(classname)
				var all_path = document.documentElement.getElementsByClassName(classname);
				for (var i = 0; i < all_path.length; ++i) {
					var box = all_path[i].getBBox();
					boxes.push([[classname, (box.x+box.width/2)/width, (box.y+box.height/2)/height, box.width/width, box.height/height]]);
				}
			}
			return boxes;
		}, classnames);
		pprintBBox(bbox, filename);
		next()
	})
}


var __counter__ = 0;
var __all__ = listDir('svg')
console.log(__all__)

function next() {
	console.log(__all__, __counter__)
	if (__counter__ < __all__.length) {
		measureBBox(__all__[__counter__++], classnames)
	} else {
		phantom.exit()
	}
}

next()
