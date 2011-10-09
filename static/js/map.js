(function(){
  var map = new L.Map('map'),
    insetMap = new L.Map('inset-map', { zoomControl:false });

  var cloudmadeAttribution = 'Map data &copy; 2011 OpenStreetMap contributors, Imagery &copy; 2011 CloudMade',
    cloudmadeOutUrl = 'http://{s}.tile.cloudmade.com/BC9A493B41014CAABB98F0471D759707/45008/256/{z}/{x}/{y}.png',
    cloudmadeOut = new L.TileLayer(cloudmadeOutUrl, {minZoom: 15, maxZoom: 15, attribution: cloudmadeAttribution}),
    cloudmadeInUrl = 'http://{s}.tile.cloudmade.com/BC9A493B41014CAABB98F0471D759707/46246/256/{z}/{x}/{y}.png',
    cloudmadeIn = new L.TileLayer(cloudmadeInUrl, {minZoom: 15, maxZoom: 15, attribution: false}),
    initCenter = new L.LatLng(39.952335,-75.163789),
    initZoom = 15;
  
  var syncMap = function() {
    map.setView(insetMap.getCenter(), insetMap.getZoom());  
  };
  
  var syncInsetMap = function() {
    insetMap.setView(map.getCenter(), map.getZoom());
  };
  
  var initMap = function(mapToInit, layer, center, zoom, syncFunc) {
    mapToInit
      .setView(center, zoom)
      .addLayer(layer)
      .on('drag', syncFunc)
      .on('zoomend', syncFunc);
  };

  initMap(map, cloudmadeOut, initCenter, initZoom, syncInsetMap);
  initMap(insetMap, cloudmadeIn, initCenter, initZoom, syncMap);
})();
