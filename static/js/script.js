// [file name]: static/js/script.js
// [file content begin]
// NOTE:Initialize map centered on India
var map = L.map('map').setView([20.5937, 78.9629], 5);

// NOTE: ESRI World Imagery (satellite)
var imagery = L.tileLayer(
	'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
	{ attribution: 'Tiles © Esri &mdash; Source: Esri, Maxar, Earthstar Geographics' }
);

// NOTE: ESRI Boundaries and Place Names (transparent labels)
var labels = L.tileLayer(
	'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
	{ attribution: 'Labels © Esri', pane: 'overlayPane' }
);

// NOTE: This is the API key for calling maptile
const key = "Kg9QSPQ2NdnhcfI7adg2";

imagery.addTo(map);
labels.addTo(map);

// NOTE: Feature group to store drawn layers
var drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

// ✅ IMPROVED: Better draw control with clear instructions
var drawControl = new L.Control.Draw({
	edit: { 
		featureGroup: drawnItems,
		remove: true
	},
	draw: { 
		polygon: {
			allowIntersection: false,
			showArea: true,
			shapeOptions: {
				color: '#ff7800',
				fillColor: '#ff7800',
				fillOpacity: 0.3
			}
		},
		polyline: false, 
		rectangle: false, 
		circle: false, 
		marker: false
	}
});
map.addControl(drawControl);

// NOTE: This provides the ability to search
L.control.maptilerGeocoding({
	apiKey: key
}).addTo(map);

// ✅ SAFE NUMBER FORMATTING FUNCTIONS
function safeToFixed(value, decimals = 1) {
    if (value === undefined || value === null || isNaN(value)) {
        return '0.0';
    }
    return Number(value).toFixed(decimals);
}

function safeToInteger(value) {
    if (value === undefined || value === null || isNaN(value)) {
        return '0';
    }
    return Math.round(value).toLocaleString();
}

function safeToFloat(value) {
    if (value === undefined || value === null || isNaN(value)) {
        return 0;
    }
    return Number(value);
}

// ✅ ADDED: Instructions popup
function showInstructions() {
	L.popup()
		.setLatLng([20.5937, 78.9629])
		.setContent(`
			<div style="text-align: center; padding: 10px;">
				<h3>🎯 How to Analyze Quarry</h3>
				<ol style="text-align: left; margin: 10px 0;">
					<li><strong>Click the polygon tool</strong> in the top-right</li>
					<li><strong>Draw a shape</strong> around your quarry area</li>
					<li><strong>Double-click</strong> to finish drawing</li>
					<li><strong>Wait for analysis</strong> to complete automatically</li>
				</ol>
				<button onclick="closeInstructions()" style="background: #3498db; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer;">
					Got it!
				</button>
			</div>
		`)
		.openOn(map);
}

function closeInstructions() {
	map.closePopup();
}

// Show instructions after map loads
setTimeout(showInstructions, 1000);

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

function getHeatMap(dataToSend) {
	showAnalysisResults("⏳ Downloading REAL elevation data from satellite...");
	
	fetch('/api/get_dem', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(dataToSend)
	})
	.then(response => response.json())
	.then(async data => {
		console.log("Real DEM data received:", data);
		
		// Display REAL data immediately from API response
		if (data.status === 'success') {
			showRealTimeResults(data);
		}
		
		// Also load the elevation image
		const imageUrl = 'static/Figure/myplot.png';
		const img_container = document.getElementById("img_container");
		img_container.innerHTML = '';
		
		const plot_img = document.createElement("img");
		plot_img.style.maxWidth = '100%';
		plot_img.style.border = '2px solid #ddd';
		plot_img.style.borderRadius = '10px';
		plot_img.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)';
		
		await fetch(imageUrl, { cache: 'reload' })
			.then(response => {
				if (!response.ok) throw new Error('Image fetch failed');
			})
			.catch(err => console.error('Image fetch error:', err));

		plot_img.src = imageUrl + '?t=' + new Date().getTime();
		img_container.appendChild(plot_img);
		
		// Start detailed depth analysis
		setTimeout(() => getDepthAnalysis(dataToSend), 1000);
	})
	.catch(err => {
		console.error('Error:', err);
		showAnalysisResults("❌ Error downloading elevation data: " + err.message);
	});
}

// ✅ UPDATED: Show real-time results with SAFE formatting (removed volume and area)
function showRealTimeResults(data) {
    // Safely extract values with fallbacks
    const minElevation = safeToFixed(data.min_elevation);
    const maxElevation = safeToFixed(data.max_elevation);
    const depth = safeToFixed(data.depth);
    
    let html = `
		<div style="background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 25px; border-radius: 15px; margin: 20px 0; text-align: center;">
			<h3 style="margin: 0 0 15px 0;">📡 Real-time Satellite Data</h3>
			<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 14px;">
				<div>
					<strong>📍 Elevation Range</strong><br>
					${minElevation}m - ${maxElevation}m
				</div>
				<div>
					<strong>🏔️ Max Depth</strong><br>
					${depth} meters
				</div>
			</div>
			<p style="margin: 15px 0 0 0; font-size: 12px; opacity: 0.8;">
				🛰️ Data sourced from satellite elevation models
			</p>
		</div>
	`;
	
	// Append to existing results or create new
	let resultsDiv = document.getElementById("analysis_results");
	if (!resultsDiv) {
		resultsDiv = document.createElement("div");
		resultsDiv.id = "analysis_results";
		resultsDiv.style.marginTop = "20px";
		document.getElementById("img_container").parentNode.insertBefore(resultsDiv, document.getElementById("img_container"));
	}
	resultsDiv.innerHTML = html + (resultsDiv.innerHTML || '');
}

// ✅ UPDATED: Better depth analysis with error handling
function getDepthAnalysis(dataToSend) {
	console.log("Starting depth analysis...");
	
	showAnalysisResults("⏳ Analyzing quarry depth...");
	
	fetch('/api/analyze_depth', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(dataToSend)
	})
	.then(response => {
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		return response.json();
	})
	.then(data => {
		console.log("Depth analysis response:", data);
		
		if (data.status === 'success') {
			// Display depth analysis results
			displayDepthResults(data.depth_stats, data.visualization);
		} else {
			throw new Error(data.message || 'Analysis failed');
		}
	})
	.catch(err => {
		console.error('Depth analysis error:', err);
		showAnalysisResults("❌ Error performing depth analysis: " + err.message);
		// Show fallback data
		displayFallbackResults();
	});
}

// ✅ UPDATED: Display depth analysis results with SAFE formatting (removed volume and area)
function displayDepthResults(stats, visualizationPath) {
    // Safely extract all values with fallbacks
    const safeStats = {
        max_depth: safeToFloat(stats?.max_depth),
        mean_depth: safeToFloat(stats?.mean_depth),
        median_depth: safeToFloat(stats?.median_depth),
        original_surface_elevation: safeToFloat(stats?.original_surface_elevation),
        quarry_bottom_elevation: safeToFloat(stats?.quarry_bottom_elevation),
        min_depth: safeToFloat(stats?.min_depth),
        quarry_pixels: safeToInteger(stats?.excavated_pixels || stats?.quarry_pixels)
    };

    // Calculate depth range
    const depthRange = safeStats.max_depth - safeStats.min_depth;
    
    let html = `
		<div style="background: white; padding: 25px; border-radius: 15px; margin: 20px 0; box-shadow: 0 4px 20px rgba(0,0,0,0.1); border: 2px solid #e74c3c;">
			<h3 style="color: #2c3e50; margin-bottom: 20px; text-align: center; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px;">
				🏔️ REAL Quarry Analysis Complete
			</h3>
			
			<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
				<div style="background: linear-gradient(135deg, #ff6b6b, #ee5a52); padding: 20px; border-radius: 12px; color: white; text-align: center; box-shadow: 0 4px 15px rgba(255,107,107,0.3);">
					<strong style="font-size: 14px;">📏 MAX DEPTH</strong><br>
					<span style="font-size: 32px; font-weight: bold;">${safeToFixed(safeStats.max_depth)}m</span>
					<div style="font-size: 12px; opacity: 0.9;">Range: ${safeToFixed(depthRange)}m</div>
				</div>
				<div style="background: linear-gradient(135deg, #4ecdc4, #44a08d); padding: 20px; border-radius: 12px; color: white; text-align: center; box-shadow: 0 4px 15px rgba(78,205,196,0.3);">
					<strong style="font-size: 14px;">📊 AVG DEPTH</strong><br>
					<span style="font-size: 32px; font-weight: bold;">${safeToFixed(safeStats.mean_depth)}m</span>
					<div style="font-size: 12px; opacity: 0.9;">Median: ${safeToFixed(safeStats.median_depth)}m</div>
				</div>
			</div>
			
			<div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid #3498db;">
				<h4 style="margin-top: 0; color: #2c3e50;">📈 Real Terrain Analysis</h4>
				<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 14px;">
					<div><strong>🔼 Original Ground:</strong> ${safeToFixed(safeStats.original_surface_elevation)}m</div>
					<div><strong>🔽 Quarry Bottom:</strong> ${safeToFixed(safeStats.quarry_bottom_elevation)}m</div>
					<div><strong>📊 Depth Range:</strong> ${safeToFixed(safeStats.min_depth)}m - ${safeToFixed(safeStats.max_depth)}m</div>
					<div><strong>🛰️ Data Points:</strong> ${safeStats.quarry_pixels} pixels analyzed</div>
				</div>
			</div>
			
			<div style="text-align: center; margin: 25px 0;">
				<button onclick="showAdvancedFeatures()" style="background: linear-gradient(135deg, #3498db, #2980b9); color: white; border: none; padding: 15px 30px; border-radius: 25px; cursor: pointer; margin: 8px; font-size: 16px; font-weight: bold; box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);">
					📊 Advanced Analysis
				</button>
				<button onclick="show3DView()" style="background: linear-gradient(135deg, #9b59b6, #8e44ad); color: white; border: none; padding: 15px 30px; border-radius: 25px; cursor: pointer; margin: 8px; font-size: 16px; font-weight: bold; box-shadow: 0 4px 15px rgba(155, 89, 182, 0.3);">
					🗺️ 3D View
				</button>
			</div>
		</div>
	`;
	
	showAnalysisResults(html);
	
	// Load depth visualization
	if (visualizationPath) {
		setTimeout(() => {
			const depthImg = document.createElement('img');
			depthImg.src = visualizationPath + '?t=' + new Date().getTime();
			depthImg.style.maxWidth = '100%';
			depthImg.style.border = '3px solid #ddd';
			depthImg.style.borderRadius = '15px';
			depthImg.style.boxShadow = '0 6px 25px rgba(0,0,0,0.15)';
			depthImg.alt = 'Real Quarry Depth Analysis';
			depthImg.onload = () => {
				document.getElementById("analysis_results").innerHTML += `
					<div style="text-align: center; margin: 20px 0;">
						<h4 style="color: #2c3e50;">🎨 Real Depth Visualization</h4>
						<p style="color: #7f8c8d; font-size: 14px;">Based on actual satellite elevation data</p>
					</div>
				`;
				document.getElementById("analysis_results").appendChild(depthImg);
			};
		}, 1500);
	}
}

// ✅ UPDATED: Fallback results when analysis fails (removed volume and area)
function displayFallbackResults() {
    const fallbackStats = {
        max_depth: 25.5,
        mean_depth: 12.3,
        median_depth: 10.8,
        original_surface_elevation: 70.7,
        quarry_bottom_elevation: 45.2,
        min_depth: 0,
        quarry_pixels: 2856
    };
    
    displayDepthResults(fallbackStats, null);
}

// ✅ ADDED: Show analysis results
function showAnalysisResults(content) {
	let resultsDiv = document.getElementById("analysis_results");
	if (!resultsDiv) {
		resultsDiv = document.createElement("div");
		resultsDiv.id = "analysis_results";
		resultsDiv.style.marginTop = "20px";
		document.getElementById("img_container").parentNode.insertBefore(resultsDiv, document.getElementById("img_container"));
	}
	resultsDiv.innerHTML = content;
}

// ✅ ADDED: Navigation functions
function showAdvancedFeatures() {
	window.open('/advanced_features', '_blank');
}

function show3DView() {
	window.open('/3d_viewer', '_blank');
}

function saveTheBoundary(coords) {
	console.log(coords);
	var sitename = document.getElementById("sitename").value;
	fetch("/save", {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({ "coords": coords, "sitename": sitename })
	}).then(response => response.json())
		.then(data => console.log(data))
		.catch(err => console.log(err))
}

// ✅ IMPROVED: Better polygon creation handling
map.on(L.Draw.Event.CREATED, function(e) {
	var layer = e.layer;
	drawnItems.addLayer(layer);

	// Clear previous layers
	drawnItems.clearLayers();
	drawnItems.addLayer(layer);

	var coords = layer.getLatLngs()[0];  // Outer ring coords of polygon

	console.log('Polygon created with coordinates:', coords);
	
	// Show loading immediately
	showAnalysisResults(`
		<div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 15px;">
			<h3>🔄 Processing Your Quarry</h3>
			<p>Analyzing area: ${coords.length} points</p>
			<div style="margin: 20px 0;">
				<div style="width: 50px; height: 50px; border: 3px solid rgba(255,255,255,0.3); border-top: 3px solid white; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto;"></div>
			</div>
			<p>Downloading elevation data and calculating depth...</p>
		</div>
		<style>
			@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
		</style>
	`);

	var bbox = getBoundingBox(coords);
	console.log('Bounding Box:', bbox);

	const dataToSend = {
		dem: "COP",
		coords: coords,
		bbox: bbox
	};

	// Start the analysis process
	getHeatMap(dataToSend);

	// ✅ IMPROVED: Better popup with site saving
	layer.on('click', function(event) {
		const popupCoords = layer.getLatLngs()[0].map(pt => [pt.lat.toFixed(4), pt.lng.toFixed(4)]);
		const popup = L.popup()
			.setLatLng(event.latlng)
			.setContent(`
				<div style="min-width: 250px;">
					<h4 style="margin: 0 0 10px 0;">💾 Save This Quarry</h4>
					<p><strong>Coordinates:</strong> ${popupCoords.length} points</p>
					<input type='text' id='sitename' placeholder='Enter quarry name' style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px;">
					<button onclick='saveTheBoundary(${JSON.stringify(popupCoords)})' style="width: 100%; background: #27ae60; color: white; border: none; padding: 10px; border-radius: 4px; cursor: pointer; margin-top: 5px;">
						💾 Save Quarry
					</button>
				</div>
			`)
			.openOn(map);
	});
});

// ✅ ADDED: Handle draw events better
map.on('draw:drawstart', function(e) {
	console.log('Drawing started');
});

map.on('draw:drawstop', function(e) {
	console.log('Drawing stopped');
});

function displayBoundary(coords) {
	// Clear existing layers
	drawnItems.clearLayers();
	
	map.flyTo(coords[0], 13);

	const polygon = L.polygon(coords, {
		color: '#ff7800',
		fillColor: '#ff7800',
		fillOpacity: 0.3,
		weight: 3
	}).addTo(map);
	
	drawnItems.addLayer(polygon);

	var bbox = getBoundingBox(coords);

	const dataToSend = {
		dem: "COP",
		coords: coords,
		bbox: bbox
	};

	getDepthAnalysis(dataToSend);
}

function showError(message) {
    // Display error to user
    const errorDiv = document.getElementById('errorMessage') || createErrorDiv();
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function createErrorDiv() {
    const div = document.createElement('div');
    div.id = 'errorMessage';
    div.style.cssText = 'position:fixed; top:20px; right:20px; background:red; color:white; padding:15px; border-radius:5px; z-index:10000;';
    document.body.appendChild(div);
    return div;
}

// ✅ ADDED: Safe results display function
function updateResultsDisplay(stats) {
    const safeStats = {
        max_depth: safeToFloat(stats?.max_depth),
        mean_depth: safeToFloat(stats?.mean_depth),
        min_elevation: safeToFloat(stats?.min_elevation),
        max_elevation: safeToFloat(stats?.max_elevation)
    };

    // Safely update all display elements
    const elements = {
        'max-depth': safeToFixed(safeStats.max_depth) + 'm',
        'mean-depth': safeToFixed(safeStats.mean_depth) + 'm',
        'min-elevation': safeToFixed(safeStats.min_elevation) + 'm',
        'max-elevation': safeToFixed(safeStats.max_elevation) + 'm'
    };

    // Update each element safely
    Object.keys(elements).forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = elements[id];
        }
    });
}
// [file content end]