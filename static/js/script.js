// NOTE:Initialize map centered on India
var map = L.map('map').setView([20.5937, 78.9629], 5);

//  NOTE: ESRI World Imagery (satellite)
var imagery = L.tileLayer(
	'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
	{ attribution: 'Tiles © Esri &mdash; Source: Esri, Maxar, Earthstar Geographics' }
);

//  NOTE: ESRI Boundaries and Place Names (transparent labels)
var labels = L.tileLayer(
	'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
	{ attribution: 'Labels © Esri', pane: 'overlayPane' }
);



// NOTE: This is the API key for calling maptile
const key = "Kg9QSPQ2NdnhcfI7adg2";


imagery.addTo(map);
labels.addTo(map);




//  NOTE: Feature group to store drawn layers
var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

//  NOTE: Add draw control for polygons
var drawControl = new L.Control.Draw({
	edit: { featureGroup: drawnItems },
	draw: { polygon: true, polyline: false, rectangle: false, circle: false, marker: false }
});
map.addControl(drawControl);


// NOTE: This provides the ability to search
L.control.maptilerGeocoding({
	apiKey: key
}).addTo(map);


// NOTE: It returns the minimum and maximum lat and lng
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

// NOTE: This function is called everytime a shape is drawn
map.on(L.Draw.Event.CREATED, function(e) {
	var layer = e.layer;
	drawnItems.addLayer(layer);

	var coords = layer.getLatLngs()[0];  // Outer ring coords of polygon

	var bbox = getBoundingBox(coords);

	console.log('Bounding Box:', bbox);


	const dataToSend = {
		dem: "COP",
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
			// NOTE: It displays the image of the heatmap.
			const imageUrl = 'static/Figure/myplot.png';
			const img_container = document.getElementById("img_container");
			const plot_img = document.createElement("img");
			// NOTE: This prevents the web browser from the fetching the previous image from cache. Instead it makes it reload and re-fetch the image from the backend.
			await fetch(imageUrl, { cache: 'reload' })
				.then(response => {
					if (!response.ok) throw new Error('Image fetch failed');
				})
				.catch(err => console.error('Image fetch error:', err));

			plot_img.src = imageUrl;
			img_container.appendChild(plot_img);
		})

		.catch(err => console.error('Error:', err));


	// NOTE: This is for the popup that is shown when we click on the map
	layer.on('click', function(event) {



		window.saveTheBoundary = function() {
			fetch("/save", {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ "coords": coords })
			}).then(response => response.json())
				.then(data => console.log(data))
				.catch(err => console.log(err))
		}

		const coords = layer.getLatLngs()[0].map(pt => [pt.lat.toFixed(4), pt.lng.toFixed(4)]);
		const popup = L.popup()
			.setLatLng(event.latlng)
			.setContent(`<b>Polygon clicked!</b><br>Coordinates:<br>${JSON.stringify(coords)}<br><a href="#" onclick='saveTheBoundary()'>Save</a>`)
			.openOn(map);

	});
});







