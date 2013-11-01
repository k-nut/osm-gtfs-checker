missingStops = new L.LayerGroup();
foundStops = new L.LayerGroup();

function initmap() {
	// set up the map
	map = new L.Map('map', {layers: [missingStops, foundStops]});

	// create the tile layer with correct attribution
	var osmUrl='http://{s}.tile2.opencyclemap.org/transport/{z}/{x}/{y}.png';
	var osmAttrib='Map data © OpenStreetMap contributors';
	var osm = new L.TileLayer(osmUrl, {minZoom: 4, maxZoom: 18, attribution: osmAttrib});

	// start the map in South-East England
	map.setView(new L.LatLng(52.52, 13.41),13);
	map.addLayer(osm);
	var markers = { "Fehlende Haltestellen" : missingStops, "Vorhandene Haltestellen" : foundStops};
	L.control.layers(null, markers).addTo(map);
}

function get_markers() {
	var box = map.getBounds();
	$.getJSON("/api/jsonstops/all/" +
		box._northEast.lat + "/" + 
		box._northEast.lng + "/" +
		box._southWest.lat + "/" +
		box._southWest.lng ,
	function(data) {
		if (data.stops == "Too many"){
			$("#toomuch").fadeIn(750,function(){$("#toomuch").fadeOut(2000);}); 
		}
		else{
			$.each(data.stops, function(){
				new_marker(this);
			});
		}
	});
}

var BusIcon = L.Icon.extend({
	options: {
		iconUrl: './static/img/bus-black.png',
		iconSize: [24, 24]
	}
});

function new_marker(stop){
	var this_marker;
	if(stop.matches >= 1) {
		this_marker = new L.marker(
			[stop.lat, stop.lon],
			{ icon: new BusIcon() }
		);
		this_marker.addTo(foundStops);
	} else {
		this_marker = new L.marker(
			[stop.lat, stop.lon],
			{ icon: new BusIcon({iconUrl: './static/img/bus-red.png'}) }
		);
		this_marker.addTo(missingStops);
	}
	this_marker.bindPopup(stop.name);
}

$(document).ready(function(){
	"use strict";
	$(".nav li").eq(2).attr("class", "active");
	initmap();
	get_markers();
	map.on('moveend', function(){get_markers();});
});

