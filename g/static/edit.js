//get building id
id = parseInt(document.getElementById('buildingID').innerHTML, 10);
//load geojson
var buildings = $.ajax({
  url:"https://raw.githubusercontent.com/Pedroaaaa/pelo-amor-de-Deus/main/a.geojson",
  dataType: "json",
  success: console.log("building data successfully loaded."),
});
//initialize map
var map = L.map('map', {
  center: [-21.76260735578972, -41.29081863108122],
  zoom: 17
});
//add basemape tiles
L.tileLayer('https://api.maptiler.com/maps/outdoor/{z}/{x}/{y}.png?key=2bUB5fNNtM0pJ6eb3aWl',{
  attribution:'<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap contributors</a>'
}).addTo(map);

$.when(buildings).done(function() {
  //hightlight color
  var highlight = {
      fillColor: 'red',
      color: 'red',
      fillOpacity: 1,
      opacity: 1
    };
  //parse geojson into a variable
  var build = L.geoJSON(buildings.responseJSON, {
  });
  //select the polygon of the building whose info is being edited
  var match = build.eachLayer(function(layer) {
    if (layer.feature.properties.id == id) {
      layer.setStyle(highlight);
      layer.addTo(map);
      map.fitBounds(layer.getBounds());
    }
  });
});
