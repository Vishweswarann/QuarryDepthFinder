// Initialize map centered on India
var map = L.map('map').setView([20.5937, 78.9629], 5);

// ESRI World Imagery (satellite)
var imagery = L.tileLayer(
	'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
	{ attribution: 'Tiles © Esri &mdash; Source: Esri, Maxar, Earthstar Geographics' }
);

// ESRI Boundaries and Place Names (transparent labels)
var labels = L.tileLayer(
	'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
	{ attribution: 'Labels © Esri', pane: 'overlayPane' }
);



const key = "Kg9QSPQ2NdnhcfI7adg2";


imagery.addTo(map);
labels.addTo(map);




// Feature group to store drawn layers
var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

// Add draw control for polygons
var drawControl = new L.Control.Draw({
	edit: { featureGroup: drawnItems },
	draw: { polygon: true, polyline: false, rectangle: false, circle: false, marker: false }
});
map.addControl(drawControl);

L.control.maptilerGeocoding({
	apiKey: key
}).addTo(map);


// Utility: get bounding box from polygon latlngs
function getBoundingBox(coords) {
	const lats = coords.map(p => p.lat);
	const lngs = coords.map(p => p.lng);

	return {
		minLat: Math.min(...lats),
		maxLat: Math.max(...lats),
		minLng: Math.min(...lngs),
		maxLng: Math.max(...lngs)
	};
}

// On polygon draw created
map.on(L.Draw.Event.CREATED, function(e) {
	var layer = e.layer;
	drawnItems.addLayer(layer);

	var coords = layer.getLatLngs()[0];  // Outer ring coords of polygon

	var bbox = getBoundingBox(coords);

	console.log('Bounding Box:', bbox);


	const dataToSend = {
		coords: coords,
		bbox: bbox
	};

	// Send bbox JSON to Flask bPI
	fetch('/api/get_dem', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(dataToSend)
	})
		.then(response => response.json())
		.then(async data => {
			const imageUrl = 'static/Figure/myplot.png';
			const img_container = document.getElementById("img_container");
			const plot_img = document.createElement("img");
			await fetch(imageUrl, { cache: 'reload' })
				.then(response => {
					if (!response.ok) throw new Error('Image fetch failed');
				})
				.catch(err => console.error('Image fetch error:', err));

			plot_img.src = imageUrl;
			img_container.appendChild(plot_img);
		})

		.catch(err => console.error('Error:', err));


});

