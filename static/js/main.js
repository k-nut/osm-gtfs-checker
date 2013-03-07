function initmap() {
	map = new L.Map('map_picker').setView([52.52, 13.41], 10);

	// create the tile layer with correct attribution
	var osmUrl='http://{s}.tile2.opencyclemap.org/transport/{z}/{x}/{y}.png';
	var osmAttrib='Map data © OpenStreetMap contributors';
	var osm = new L.TileLayer(osmUrl, {minZoom: 3, maxZoom: 18, attribution: osmAttrib});

	map.addLayer(osm);
}

function radiusmap(lat, lon) {
	if (map_exists === false){
		map_exists = true;
		radius_map = new L.Map('radius_map').setView([lat, lon], 16);

		// create the tile layer with correct attribution
		var osmUrl='http://{s}.tile2.opencyclemap.org/transport/{z}/{x}/{y}.png';
		var osmAttrib='Map data © OpenStreetMap contributors';
		var osm = new L.TileLayer(osmUrl, {minZoom: 3, maxZoom: 18, attribution: osmAttrib});
		radius_map.addLayer(osm);
		radius_map.on("moveend", function(){change_link_for_remote_edit();});
	}
	var circle = L.circle([lat, lon], 250, {
		color: 'blue',
		fillColor: 'lightblue',
		fillOpacity: 0.75
	}).addTo(radius_map);
	var marker = new L.marker([lat, lon]).addTo(radius_map);
	radius_map.panTo([lat, lon]);

	$("#search_radius").modal();
	setTimeout(function(){
		L.Util.requestAnimFrame(radius_map.invalidateSize, radius_map, !1, radius_map._container);
	}, 500);
}
function hiderows(element){
	if (element.attr("checked")){
		$("."+element.attr("name")).each(function(){
			$(this).css("display", "table-row");
		});
	}
	else{
		$("."+element.attr("name")).each(function(){
			$(this).css("display", "none");
		});
	}
	count();
}

function count(){
	var total_stops = $("tr").length-1;
	var missing_stops = $(".nomatch").length;
	$("#total").text(total_stops);
	$("#nomatch_total").text(missing_stops);
}

function search(){
	var query = $("#search").val();
	window.location = "/search/" + query;
}

function change_landkreis(){
	var landkreis = $("#landkreis-picker").val();
	window.location = "/city/" + landkreis + "/page/1";
}

function own_area(showOnly){
	var box = map.getBounds();
	window.location = "/stops/" + showOnly + "/" +
		box._northEast.lat + "/" +
		box._northEast.lng + "/" + 
		box._southWest.lat + "/" +
		box._southWest.lng; 
}

			function get_parameters(){
				if (window.location.toString().indexOf("?") < 0){
					return false
				}
				var parampart = window.location.toString().split("?")[1];
				var params = parampart.split("&");
				var values = {};
				$.each(params, function(index, value){
					var parts = value.split("=");
					values[parts[0]] = parts[1];
				})
				return values
			}

			function change_links(){
				var parampart = "?";
				if ($("#nomatch").attr("checked") == "checked"){
					parampart += "nomatch=true&";
				}
				if ($("#match").attr("checked") == "checked"){
					parampart += "match=true";
				}
				$(".pagination a").each(function(){
					var old_url = $(this).attr("href");
					if (old_url.indexOf("?") > -1){
						var new_url = old_url.split("?")[0];
					}
					else{
						var new_url = old_url;
					}
					new_url += parampart;
					$(this).attr("href", new_url);
				});
			}

			function change_link_for_remote_edit(){
				var lat = radius_map.getCenter().lat;
				var lon = radius_map.getCenter().lng;
				var zoom = radius_map.getZoom();
				var url = "http://www.openstreetmap.org/edit?editor=remote&lat=" + lat + "&lon=" + lon + "&zoom=" + zoom;
				$("#remote_edit_link").attr("href", url);
			}
