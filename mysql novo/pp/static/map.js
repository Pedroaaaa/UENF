//initialize map
var map = L.map('map', {
  center: [-21.76260735578972, -41.29081863108122],
  zoom: 17
});
//load geojson via AJAX
var buildings = $.ajax({
  url:"https://raw.githubusercontent.com/Pedroaaaa/pelo-amor-de-Deus/main/a.geojson",
  dataType: "json",
  success: console.log("building data successfully loaded."),
});
//load basemap tiles
L.tileLayer('https://api.maptiler.com/maps/outdoor/{z}/{x}/{y}.png?key=2bUB5fNNtM0pJ6eb3aWl',{
  attribution:'<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap contributors</a>'
}).addTo(map);

//load geojson onto map
$.when(buildings).done(function() {
  //color for normal polygon
  var crimson = {
    fillColor: '#A41034',
    color: '#A41034',
    weight: 1,
    opacity: 1.0,
    fillOpacity: 1,
  };
  //color for highlighted
  var highlight = {
      fillColor: 'red',
      color: 'red',
      fillOpacity: 1,
      opacity: 1
    };
  //call modal on the page
  var BuildingDetails = new bootstrap.Modal(document.getElementById("BuildingDetails"), {});
  //function for clicking a shape
  function whenClicked(feature, layer) {
    layer.on("click", function (e) {
      //reset everything to normal color
      build.setStyle(crimson);
      //set clicked item to highlight
      layer.setStyle(highlight);
      //get building id via geojson
      id = feature.properties.id;
      //request building detail from SQL database
      $.get('/search?q=' + id, function(e) {
        bldg = e[0];
        //building name
        name = bldg.name;
        if (name != 'null'){
          document.getElementById('ModalHeader').innerHTML = name;
        }
        else
        {
          document.getElementById('ModalHeader').innerHTML = 'Unnamed';
        }
        //image
        image = bldg.image;
        if (image!= null){
          document.getElementById('buildingimage').innerHTML = '<img src='+image+' style="width:100%"/>';
        }
        //if no image allow upload via url
        else
        {
          document.getElementById('buildingimage').innerHTML ='<form action="/addimage" method="POST"><div class="form-group"><div class="row"><label for="cover">Add a cover photo via URL</label></div><div class="row"><input type="text" class="form-control" name="cover_url" id="cover" required></div></div></form>';
        }
        //get keys to iterate through
        keys = Object.keys(bldg);
        //reset modal html
        document.getElementById('building_info').innerHTML = '';
        document.getElementById('description').innerHTML = '';
        //add information via html
        for (i = 0; i < keys.length; i++) {
          if (bldg[keys[i]] != null && bldg[keys[i]] != '' && keys[i] != 'image' && keys[i] != 'name' && keys[i] != 'description'){
            headhtml='<div class="row align-items-center justify-content-center"><div class="col-sm-3 text-capitalize"><b>';
            middlehtml=': </b></div><div class="col-sm-9"><p style="margin: auto;" id=';
            endhtml='</p></div></div>';
            document.getElementById('building_info').innerHTML += headhtml+keys[i]+middlehtml+keys[i]+'>'+bldg[keys[i]]+endhtml;
          }
        }
        if (bldg["description"] != null){
          document.getElementById('description').innerHTML = '<hr>' + bldg["description"];
        }
      });
      //reset modal comment
      document.getElementById('comments').innerHTML = '';
      //retrieve comments
      $.get('/comment?q=' + id, function(comment){
        for(i=0; i < comment.length; i++){
          buildingID = comment[i]["building_id"];
          type = comment[i]["type"];
          content = comment[i]["comment"];
          time = comment[i]["time"];
          id = comment[i]["commentID"];
          if (content != null){
            //parse different types of comments
          if(type == 'ASK'){
            //add form html
            h1 = '<hr><div class="container-fluid"><div class="row" style="padding-bottom:0px;"> <div class="col"><b>Question</b></div><div class = "col"><p style="color: gainsboro">';
            h2 = '</p></div></div><div class="row"><p>';
            h3 = '</p></div><form action="/postanswer" method="POST" id="submitAnswer_';
            h4 = '"><input name="building_id" style="display: none;" value =”';
            h5 = '”><input name="qid" id = "qid" style="display: none;" value = "';
            h6 = '"><input name="type" style="display: none;" value = "ANS"><div class="form-group" style="padding-bottom:10px;" id = "answer_form_';
            h7 = '"></div></form><div class="row"><div class="col"><button id = "answer_btn" class="btn btn-primary" onclick="answer(this.value)" value="';
            h8 = '">Answer</button></div></div></div>';
            document.getElementById('comments').innerHTML += h1 + time + h2 + content + h3 + id + h4 + buildingID + h5 + id + h6 + id + h7 + id + h8;
          }
          else if(type == 'ANS')
          {
            document.getElementById('comments').innerHTML += '<hr><div class="container-fluid"><div class="row" style="padding-bottom:0px;"> <div class="col"><b>Answer</b></div><div class = "col"><p style="color: gainsboro">'+ time +'</p></div></div><div class="row"><p>'+ content +'</p></div>';
          }
          else
          {
            document.getElementById('comments').innerHTML += '<hr><div class="container-fluid"><div class="row" style="padding-bottom:0px;"> <div class="col"><b>Comment</b></div><div class = "col"><p style="color: gainsboro">'+ time +'</p></div></div><div class="row"><p>'+ content +'</p></div>';
          }
        }

        }
      });
      //show modal
      BuildingDetails.show();
    });
  }
//add shapes to map
  var build = L.geoJSON(buildings.responseJSON, {
    style: crimson,
    //call click function
    onEachFeature: whenClicked
  }).addTo(map);
});

