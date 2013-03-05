var map;

function addConstituency(constituency, constituency_info, mapProj) {
    var pt = OpenLayers.Geometry.Point;
    var proj = new OpenLayers.Projection("EPSG:4326");
    var arr = [];
    for (var i = 0; i < constituency['exterior_coordinates'].length; i++) {
        arr.push(new pt(constituency['exterior_coordinates'][i][0], constituency['exterior_coordinates'][i][1]));
    }

    var constit = new OpenLayers.Geometry.Polygon(
            new OpenLayers.Geometry.LinearRing(arr));
    constit = constit.transform(proj, mapProj);
    return new OpenLayers.Feature.Vector(constit, {'colour': constituency_info['colour'], 'text': constituency_info['text']} , null);
}

function init() {
    map = new OpenLayers.Map({
        div: "map",
        allOverlays: true,
        controls: [
        new OpenLayers.Control.PanZoom(),
        new OpenLayers.Control.Navigation(),
      new OpenLayers.Control.ArgParser(),
        new OpenLayers.Control.Attribution()
        ]
    });

    var gmap = new OpenLayers.Layer.OSM("Google Streets", null, {
        sphericalMercator: true,
        attribution: null
        //       'maxExtent': new OpenLayers.Bounds(-20037508.34, -20037508.34, 20037508.34, 20037508.34)
    });
    var pointLayer = new OpenLayers.Layer.Vector("Point Layer", 
            {styleMap: new OpenLayers.StyleMap({
                                                   'fillColor' : '${colour}', 
            'fillOpacity' : 0.6, 
            'strokeColor': '${colour}'
                                               }, {"extendDefault": "true"}),
            eventListeners:{
                'featureselected':function(evt){
                    var feature = evt.feature;
                    var popup = new OpenLayers.Popup.FramedCloud("popup",
                        OpenLayers.LonLat.fromString(feature.geometry.getCentroid().toShortString()),
                        new OpenLayers.Size(400,800),
                        feature.attributes.text,
                        null,
                        true,
                        null);
                    popup.autoSize = true;
                    popup.maxSize = new OpenLayers.Size(400,800);
                    popup.size = new OpenLayers.Size(400,800);
                    popup.fixedRelativePosition = true;
                    feature.popup = popup;
                    map.addPopup(popup);
                },
                'featureunselected': function(evt){
                    var feature = evt.feature;
                    map.removePopup(feature.popup);
                    feature.popup.destroy();
                    feature.popup = null;
                }
            }           
            });

    map.addLayers([gmap, pointLayer]);
    var lonlat = new OpenLayers.LonLat(-0.0967921427372, 51.654736906);
    var proj = new OpenLayers.Projection("EPSG:4326");
    lonlat.transform(proj, map.getProjectionObject());
    map.setCenter(lonlat, 7);

    var featarray = [];
    for (var key in constituencies) {
    if (constituencies_info[key].count > 0) {
    featarray.push(addConstituency(constituencies[key], constituencies_info[key], map.getProjectionObject()));
    }
}
 var control = new OpenLayers.Control.SelectFeature(pointLayer);
 control.handlers.feature.stopDown = false; 
 map.addControl(control);
 control.activate();
    pointLayer.addFeatures(featarray);
}

init();
