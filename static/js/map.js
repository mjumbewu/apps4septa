(function(){
  var map = new L.Map('map'),
    insetMap = new L.Map('inset-map', { zoomControl:false });

  var cloudmadeAttribution = 'Map data &copy; 2011 OpenStreetMap contributors, Imagery &copy; 2011 CloudMade',
    cloudmadeOutUrl = 'http://{s}.tile.cloudmade.com/9f6894100760403498e3b47fdbdbcdef/45008/256/{z}/{x}/{y}.png',
    cloudmadeOut = new L.TileLayer(cloudmadeOutUrl, {minZoom: 15, maxZoom: 15, attribution: cloudmadeAttribution}),
    cloudmadeInUrl = 'http://{s}.tile.cloudmade.com/9f6894100760403498e3b47fdbdbcdef/46246/256/{z}/{x}/{y}.png',
    cloudmadeIn = new L.TileLayer(cloudmadeInUrl, {minZoom: 15, maxZoom: 15, attribution: false}),
    initCenter = new L.LatLng(39.952335,-75.163789),
    initZoom = 15;
  
  var syncMap = function() {
    map.setView(insetMap.getCenter(), insetMap.getZoom());  
  };
  
  var syncInsetMap = function() {
    insetMap.setView(map.getCenter(), map.getZoom());
  };
  
  var updateRoutes = function(evt) {
    var bbox = insetMap.getBounds(),
      left = bbox.getSouthWest().lng,
      bottom = bbox.getSouthWest().lat,
      right = bbox.getNorthEast().lng,
      top = bbox.getNorthEast().lat,
      size = map.getSize();
      
    console.log(bbox, size);
    
    $.ajax({
      url: '/routes/' + left + ',' + bottom + ',' + right + ',' + top,
      data: {
        width: size.x,
        height: size.y
      },
      dataType: 'json',
      success: function(data, textStatus, jqXHR) {
        console.log(data, textStatus, jqXHR);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.log(jqXHR, textStatus, errorThrown);
      }
    });
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
  
  insetMap.on('dragend', updateRoutes);
})();
