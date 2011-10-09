(function(){
  var map = new L.Map('map'),
    insetMap = new L.Map('inset-map', { zoomControl:false });

  var cloudmadeAttribution = 'Map data &copy; 2011 OpenStreetMap contributors, Imagery &copy; 2011 CloudMade',
    cloudmadeOutUrl = 'http://{s}.tile.cloudmade.com/BC9A493B41014CAABB98F0471D759707/45008/256/{z}/{x}/{y}.png',
    cloudmadeOut = new L.TileLayer(cloudmadeOutUrl, {minZoom: 11, maxZoom: 14, attribution: cloudmadeAttribution}),
    cloudmadeInUrl = 'http://{s}.tile.cloudmade.com/BC9A493B41014CAABB98F0471D759707/22677/256/{z}/{x}/{y}.png',
    cloudmadeIn = new L.TileLayer(cloudmadeInUrl, {minZoom: 11, maxZoom: 14, attribution: false});

  map.setView(new L.LatLng(39.952335,-75.163789), 12).addLayer(cloudmadeOut);
  insetMap.setView(new L.LatLng(39.952335,-75.163789), 12).addLayer(cloudmadeIn);
  
})();
