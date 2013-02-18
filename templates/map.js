function initmap() {
	// set up the map
	map = new L.Map('map');

	// create the tile layer with correct attribution
	var osmUrl='http://{s}.tile2.opencyclemap.org/transport/{z}/{x}/{y}.png';
	var osmAttrib='Map data © OpenStreetMap contributors';
	var osm = new L.TileLayer(osmUrl, {minZoom: 8, maxZoom: 18, attribution: osmAttrib});

	// start the map in South-East England
	map.setView(new L.LatLng(52.52, 13.41),13);
	map.addLayer(osm);
}

function get_markers() {
	var box = map.getBounds();
	$.getJSON("/api/jsonstops/problemsonly/" +
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
	} else {
		this_marker = new L.marker(
				[stop.lat, stop.lon],
				{ icon: new BusIcon({iconUrl: './static/img/bus-red.png'}) }
				);
	}
	this_marker.bindPopup(stop.name);
	this_marker.addTo(map);
}

$(document).ready(function(){
	"use strict";
	$(".nav li").eq(2).attr("class", "active");
	initmap();
	get_markers();
	map.on('moveend', function(){get_markers();});
});

