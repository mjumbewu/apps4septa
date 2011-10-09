(function(){
  var initCenter = new L.LatLng(39.952335,-75.163789),
    initZoom = 14,
    map = new L.Map('map', { zoomControl:false }),
    insetMap = new L.Map('inset-map', { zoomControl:false }),
    cloudmadeAttribution = 'Map data &copy; 2011 OpenStreetMap contributors, Imagery &copy; 2011 CloudMade',
    cloudmadeOutUrl = 'http://{s}.tile.cloudmade.com/9f6894100760403498e3b47fdbdbcdef/45008/256/{z}/{x}/{y}.png',
    cloudmadeOut = new L.TileLayer(cloudmadeOutUrl, {minZoom: initZoom, maxZoom: initZoom, attribution: cloudmadeAttribution}),
    cloudmadeInUrl = 'http://{s}.tile.cloudmade.com/9f6894100760403498e3b47fdbdbcdef/46246/256/{z}/{x}/{y}.png',
    cloudmadeIn = new L.TileLayer(cloudmadeInUrl, {minZoom: initZoom, maxZoom: initZoom, attribution: false}),
    transitImageLayer,
    $routeDetails = $('#route-details');
  
  var syncMap = function() {
    map.setView(insetMap.getCenter(), insetMap.getZoom());  
  };
  
  var syncInsetMap = function() {
    insetMap.setView(map.getCenter(), map.getZoom());
  };
  
  var updateRouteMap = function(imageUrl) {
    if (imageUrl) {
      map.removeLayer(cloudmadeOut);
      if (transitImageLayer) {
        map.removeLayer(transitImageLayer);
      }
      
      transitImageLayer = new L.ImageOverlay(imageUrl, map.getBounds(), {attribution: cloudmadeAttribution});
      map.addLayer(transitImageLayer);
    } else {
      map.removeLayer();
    }
  };
  
  var updateRouteDetails = function(routes) {
    var html = '';
    if (routes && routes.length > 0) {
      $.each(routes, function(i, r) {
        html += '<h5><div class="swatch swatch-'+i+'"><div>Route '+r.label+'</h5>';
      });
    } else {
      html = '<div class="alert-message block-message warning"><strong>No routes were found.</strong> No worries, just drag the map around and you\'ll find some.</div>';
    }
    
    $routeDetails.html(html);
  };
  
  var updateRoutes = function(evt) {
    var bbox = insetMap.getBounds(),
      left = bbox.getSouthWest().lng,
      bottom = bbox.getSouthWest().lat,
      right = bbox.getNorthEast().lng,
      top = bbox.getNorthEast().lat,
      size = map.getSize();
          
    $.ajax({
      url: '/routes/' + left + ',' + bottom + ',' + right + ',' + top,
      data: {
        width: size.x,
        height: size.y
      },
      dataType: 'json',
      success: function(data, textStatus, jqXHR) {
        console.log(data, textStatus, jqXHR);
        updateRouteDetails(data.routes);
        updateRouteMap(data.map_url);
      },
      error: function(jqXHR, textStatus, errorThrown) {
        console.log(jqXHR, textStatus, errorThrown);
        updateRouteDetails(false);
        updateRouteMap('/static/images/map283.png');
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
  
  updateRoutes();
})();
