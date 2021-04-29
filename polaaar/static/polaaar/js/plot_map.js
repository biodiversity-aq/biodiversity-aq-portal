function map_init(map, options) {
    let geojsonFeature = JSON.parse(document.getElementById('geojson-feature').textContent)

    let geojsonMarkerOptions = {
        radius: 3,
        fillColor: "#FF0080",
        color: "#FF0080",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.3
    };

    let tileLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
        attribution: ''
    })
    tileLayer.addTo(map);
    L.geoJSON(geojsonFeature, {
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, geojsonMarkerOptions);
        },
    }).addTo(map);
}