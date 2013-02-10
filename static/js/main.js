function initmap() {
	map = new L.Map('map_picker').setView([52.52, 13.41], 10);

	// create the tile layer with correct attribution
	var osmUrl='http://{s}.tile2.opencyclemap.org/transport/{z}/{x}/{y}.png';
	var osmAttrib='Map data © OpenStreetMap contributors';
	var osm = new L.TileLayer(osmUrl, {minZoom: 3, maxZoom: 18, attribution: osmAttrib});

	map.addLayer(osm);
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
