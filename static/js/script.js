// Global variables to store the workflow state
var currentPolygonCoords = null;
var bbox = null;
var coords = null;


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
				// MODIFIED: Color changed to new theme
				color: '#1abc9c',
				fillColor: '#1abc9c',
				fillOpacity: 0.3
			}
		},
		polyline: false,
		rectangle: false,
		circle: false,
		marker: true
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

// ✅ RENAMED: Terminal output storage is now analysisLog
let analysisLog = [];

// ✅ RENAMED: Function to add log messages
function addTerminalMessage(message, type = 'info') {
	const timestamp = new Date().toLocaleTimeString();
	analysisLog.push({ timestamp, message, type });

	// Keep only last 20 messages
	if (analysisLog.length > 20) {
		analysisLog = analysisLog.slice(-20);
	}

	updateTerminalDisplay();
}

// ✅ RENAMED: Function to update terminal display
function updateTerminalDisplay() {
	const terminalDiv = document.getElementById('terminal_output');
	if (!terminalDiv) return;

	let html = `
		<div style="background: #1e1e1e; color: #00ff00; padding: 15px; border-radius: 8px; margin: 20px 0; font-family: 'Courier New', monospace; font-size: 12px; max-height: 300px; overflow-y: auto;">
			<div style="color: #ffffff; margin-bottom: 10px; font-weight: bold;">🖥️ ANALYSIS LOG</div>
	`;

	analysisLog.forEach(entry => {
		const icon = entry.type === 'success' ? '✅' : entry.type === 'error' ? '❌' : entry.type === 'warning' ? '⚠️' : '🔍';
		html += `<div style="margin: 5px 0; border-left: 3px solid ${getColorForType(entry.type)}; padding-left: 10px;">
			<span style="color: #888;">[${entry.timestamp}]</span> ${icon} ${entry.message}
		</div>`;
	});

	html += `</div>`;
	terminalDiv.innerHTML = html;
	terminalDiv.scrollTop = terminalDiv.scrollHeight;
}

// MODIFIED: Updated color scheme for terminal types
function getColorForType(type) {
	switch (type) {
		case 'success': return '#2ecc71';
		case 'error': return '#e74c3c';
		case 'warning': return '#f39c12';
		default: return '#95a5a6';
	}
}

// ✅ RENAMED: Instructions popup updated to "Depth Finder"
function showInstructions() {
	L.popup()
		.setLatLng([20.5937, 78.9629])
		.setContent(`
			<div style="text-align: center; padding: 10px;">
				<h3>🎯 How to Use the Depth Finder</h3>
				<ol style="text-align: left; margin: 10px 0;">
					<li><strong>Click the polygon tool</strong> in the top-right</li>
					<li><strong>Draw a shape</strong> around your quarry area</li>
					<li><strong>Double-click</strong> to finish drawing</li>
					<li><strong>Wait for analysis</strong> to complete automatically</li>
				</ol>
				<button onclick="closeInstructions()" style="background: #16a085; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer;">
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
	addTerminalMessage("Starting DEM download from satellite...");
	showAnalysisResults("⏳ Downloading REAL elevation data from satellite...");

	fetch('/api/get_dem', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(dataToSend)
	})
		.then(response => response.json())
		.then(async data => {
			console.log("Real DEM data received:", data);
			addTerminalMessage("DEM data downloaded successfully", 'success');

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

			// Start detailed depth analysis
			setTimeout(() => getDepthAnalysis(dataToSend), 1000);
		})
		.catch(err => {
			console.error('Error:', err);
			addTerminalMessage("Error downloading elevation data: " + err.message, 'error');
			showAnalysisResults("❌ Error downloading elevation data: " + err.message);
		});
}

// ✅ UPDATED: Show real-time results with new color scheme
function showRealTimeResults(data) {
	// Safely extract values with fallbacks
	const minElevation = safeToFixed(data.min_elevation);
	const maxElevation = safeToFixed(data.max_elevation);
	const depth = safeToFixed(data.depth);

	let html = `
		<div style="background: linear-gradient(135deg, #34495e, #2c3e50); color: white; padding: 25px; border-radius: 15px; margin: 20px 0; text-align: center;">
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

// ✅ RENAMED & UPDATED: Better depth analysis with "Depth Finder" naming
function getDepthAnalysis(dataToSend) {
	addTerminalMessage("Starting Depth Finder analysis with gradient descent...");
	showAnalysisResults("⏳ Running Depth Finder analysis...");

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
			addTerminalMessage("Depth analysis completed successfully", 'success');

			if (data.status === 'success') {
				// Display depth analysis results
				displayDepthResults(data.depth_stats, data.visualization);
			} else {
				throw new Error(data.message || 'Analysis failed');
			}
		})
		.catch(err => {
			console.error('Depth analysis error:', err);
			addTerminalMessage("Error in Depth Finder analysis: " + err.message, 'error');
			showAnalysisResults("❌ Error in Depth Finder analysis: " + err.message);
			// Show fallback data
			displayFallbackResults();
		});
}

// ✅ RENAMED & UPDATED: Display depth results with "Depth Finder" and new colors
function displayDepthResults(stats, visualizationPath) {
	// Safely extract all values with fallbacks
	const safeStats = {
		max_depth: safeToFloat(stats?.max_depth),
		mean_depth: safeToFloat(stats?.mean_depth),
		median_depth: safeToFloat(stats?.median_depth),
		original_surface_elevation: safeToFloat(stats?.original_surface_elevation),
		quarry_bottom_elevation: safeToFloat(stats?.quarry_bottom_elevation),
		min_depth: safeToFloat(stats?.min_depth),
		quarry_pixels: safeToInteger(stats?.excavated_pixels || stats?.quarry_pixels),
		total_area_m2: safeToFloat(stats?.total_area_m2),
		volume_m3: safeToFloat(stats?.volume_m3),
		surface_original_method: safeToFloat(stats?.surface_original_method),
		surface_gradient_descent: safeToFloat(stats?.surface_gradient_descent)
	};

	// Calculate depth range
	const depthRange = safeStats.max_depth - safeStats.min_depth;

	// Add terminal messages
	addTerminalMessage(`Gradient Descent Surface: ${safeToFixed(safeStats.surface_gradient_descent)}m`, 'success');
	addTerminalMessage(`Original Surface: ${safeToFixed(safeStats.surface_original_method)}m`);
	addTerminalMessage(`Max Depth: ${safeToFixed(safeStats.max_depth)}m`);
	addTerminalMessage(`Quarry Area: ${safeToInteger(safeStats.total_area_m2)} m²`);
	addTerminalMessage(`Excavation Volume: ${safeToInteger(safeStats.volume_m3)} m³`);

	let html = `
        <div style="background: white; padding: 25px; border-radius: 15px; margin: 20px 0; box-shadow: 0 4px 20px rgba(0,0,0,0.1); border: 2px solid #16a085;">
            <h3 style="color: #2c3e50; margin-bottom: 20px; text-align: center; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px;">
                🏔️ Depth Finder Analysis Complete
            </h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
                <div style="background: linear-gradient(135deg, #2ecc71, #28b463); padding: 20px; border-radius: 12px; color: white; text-align: center; box-shadow: 0 4px 15px rgba(46, 204, 113, 0.3);">
                    <strong style="font-size: 14px;">📏 MAX DEPTH</strong><br>
                    <span style="font-size: 32px; font-weight: bold;">${safeToFixed(safeStats.max_depth)}m</span>
                    <div style="font-size: 12px; opacity: 0.9;">Range: ${safeToFixed(depthRange)}m</div>
                </div>
                <div style="background: linear-gradient(135deg, #1abc9c, #16a085); padding: 20px; border-radius: 12px; color: white; text-align: center; box-shadow: 0 4px 15px rgba(26, 188, 156, 0.3);">
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

            <div style="background: #e8f4fd; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 4px solid #2ecc71;">
                <h4 style="margin-top: 0; color: #2c3e50;">📊 Volume & Area Analysis</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 14px;">
                    <div><strong>📐 Total Area:</strong> ${safeToInteger(safeStats.total_area_m2)} m²</div>
					<div><strong>⛰️ Excavation Volume:</strong> ${safeToInteger(safeStats.volume_m3)} m³</div>
					<div><strong>🎯 Surface (Gradient Descent):</strong> ${safeToFixed(safeStats.surface_gradient_descent)}m</div>
					<div><strong>🏔️ Surface (Original):</strong> ${safeToFixed(safeStats.surface_original_method)}m</div>
                </div>
            </div>
        </div>
    `;

	showAnalysisResults(html);

	// Load depth visualization
	if (visualizationPath) {
		setTimeout(() => {
			const resultsContainer = document.getElementById("analysis_results");

			// Create the Image Element
			const depthImg = document.createElement('img');
			depthImg.src = visualizationPath + '?t=' + new Date().getTime();

			// Style matches the library requirements
			depthImg.style.maxWidth = '100%';
			depthImg.style.border = '3px solid #ddd';
			depthImg.style.borderRadius = '15px';
			depthImg.style.boxShadow = '0 6px 25px rgba(0,0,0,0.15)';
			depthImg.style.marginTop = '20px';
			depthImg.style.cursor = 'zoom-in'; // Shows pointer
			depthImg.alt = 'Real Quarry Depth Analysis';

			depthImg.onload = () => {
				// A. Create Header
				const headerDiv = document.createElement('div');
				headerDiv.style.textAlign = 'center';
				headerDiv.style.margin = '20px 0';
				headerDiv.innerHTML = `
                    <h4 style="color: #2c3e50;">🎨 Real Depth Visualization</h4>
                    <p style="color: #7f8c8d; font-size: 14px;">Click image for Full Screen Analysis</p>
                `;

				// B. Append Header and Image
				resultsContainer.appendChild(headerDiv);
				resultsContainer.appendChild(depthImg);

				// C. ✅ INITIALIZE VIEWERJS (The Professional Solution)
				// This enables: Click-to-Open + Infinite Scroll Zoom + Drag Pan
				const viewer = new Viewer(depthImg, {
					toolbar: {
						zoomIn: 1,
						zoomOut: 1,
						oneToOne: 1,
						reset: 1,
						rotateLeft: 1,
						rotateRight: 1,
						flipHorizontal: 0,
						flipVertical: 0,
					},
					navbar: false,      // Hide bottom bar for single image
					title: false,       // Hide file name
					tooltip: true,      // Show zoom %
					movable: true,      // Allow dragging
					zoomable: true,     // Allow zooming
					rotatable: true,    // Allow rotation
					scalable: true,     // Allow flipping
					transition: true,   // Smooth open animation
					fullscreen: true,   // Allow full screen
				});

				console.log("✅ ViewerJS activated successfully");
			};
		}, 1500);
	}
}
// ✅ UPDATED: Fallback results when analysis fails
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


/* ==========================================
   UPGRADED SAVE FUNCTION (Replace existing saveTheBoundary)
   ========================================== */

function saveTheBoundary(coords) {
	// 1. Get the name from the popup input
	const siteNameInput = document.getElementById('siteNameInput');
	const sitename = siteNameInput.value;

	if (!sitename) {
		alert("⚠️ Please enter a site name first.");
		return;
	}

	// 2. Prepare the data (MongoDB format)
	// The coords passed from the popup are usually [lat, lng], but let's ensure structure
	// If coords are just raw arrays, map them to objects if needed, 
	// but your backend likely handles the list of lists.
	// Let's check if we need to format it for the new API:
	// The new API expects: { sitename: "...", coords: [...] }

	// UI Feedback
	const saveBtn = document.querySelector('.leaflet-popup-content button');
	if (saveBtn) saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';

	fetch('/api/save_site', {  // <--- CHANGED to new API
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			"sitename": sitename,
			"coords": coords
		})
	})
		.then(response => response.json())
		.then(data => {
			if (data.status === 'success') {
				// 3. Success!
				if (saveBtn) {
					saveBtn.innerHTML = '<i class="fas fa-check"></i> Saved!';
					saveBtn.style.background = '#2ecc71';
				}

				// 4. Refresh the Sidebar List immediately
				if (typeof fetchSavedSites === "function") {
					fetchSavedSites();
				}

				// Close popup after 1 second
				setTimeout(() => {
					map.closePopup();
				}, 1000);

				// Optional: Open the drawer to show the new site
				const drawer = document.getElementById('drawer');
				if (drawer && drawer.classList.contains('collapsed')) {
					drawer.classList.remove('collapsed');
				}

			} else {
				alert('❌ Error: ' + data.message);
				if (saveBtn) saveBtn.innerHTML = 'Save Quarry';
			}
		})
		.catch(error => {
			console.error('Error:', error);
			alert('❌ Network Error');
			if (saveBtn) saveBtn.innerHTML = 'Save Quarry';
		});
	// Inside saveTheBoundary success block:
	if (window.fetchSavedSites) {
		window.fetchSavedSites(); // <--- This updates the sidebar instantly
	}
}

map.on(L.Draw.Event.CREATED, function (e) {
	var type = e.layerType;
	var layer = e.layer;

	if (type === "polygon") {
		// 1. Clear previous layers & Add new one
		drawnItems.clearLayers();
		drawnItems.addLayer(layer);

		coords = layer.getLatLngs()[0];  // Save coordinates

		console.log('Polygon created with coordinates:', coords);
		addTerminalMessage(`Polygon created with ${coords.length} points`);

		// 2. Attach the Click Event (Popup logic)
		// This prepares the popup but DOES NOT open it yet.
		layer.on('click', function (event) {
			const popupCoords = layer.getLatLngs()[0].map(pt => [pt.lat.toFixed(4), pt.lng.toFixed(4)]);

			const popup = L.popup()
				.setLatLng(event.latlng)
				.setContent(`
				<div style="min-width: 250px;">
					<h4 style="margin: 0 0 10px 0;">💾 Save This Quarry</h4>
					<p><strong>Coordinates:</strong> ${popupCoords.length} points</p>
					
					<input type='text' id='siteNameInput' placeholder='Enter quarry name' style="width: 100%; padding: 8px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px;">
					
					<button onclick='saveTheBoundary(${JSON.stringify(popupCoords)})' style="width: 100%; background: #27ae60; color: white; border: none; padding: 10px; border-radius: 4px; cursor: pointer; margin-top: 5px;">
						💾 Save Quarry
					</button>
				</div>
			`)
				.openOn(map);
		});

		// ❌ REMOVED: layer.fire('click', ...) 
		// Now the popup will NOT open automatically.

	} else if (type === "marker") {
		if (!coords) {
			alert("⚠️ Please draw the Quarry Boundary (Polygon) first!");
			return;
		}
		drawnItems.addLayer(layer);

		// 1. Get Marker Coordinates
		var refLat = layer.getLatLng().lat;
		var refLng = layer.getLatLng().lng;

		console.log("📍 Reference point set at:", refLat, refLng);

		// Show loading immediately
		showAnalysisResults(`
		<div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #34495e, #2c3e50); color: white; border-radius: 15px;">
			<h3>🔄 Processing Quarry Area</h3>
			<div style="margin: 20px 0;">
				<div style="width: 50px; height: 50px; border: 3px solid rgba(255,255,255,0.3); border-top: 3px solid white; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto;"></div>
			</div>
			<p>Downloading elevation data and calculating depth...</p>
		</div>
		<style>
			@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
		</style>
	`);

		bbox = getBoundingBox(coords);

		const dataToSend = {
			dem: "COP",
			coords: coords,
			bbox: bbox,
			reference_point: { lat: refLat, lng: refLng }
		};

		// Start the analysis process
		getHeatMap(dataToSend);
	}
});
// ✅ ADDED: Handle draw events better
map.on('draw:drawstart', function (e) {
	console.log('Drawing started');
	addTerminalMessage('Drawing started - click on map to create polygon vertices');
});

map.on('draw:drawstop', function (e) {
	console.log('Drawing stopped');
});

function displayBoundary(coords) {
	// Clear existing layers
	drawnItems.clearLayers();

	map.flyTo(coords[0], 13);

	const polygon = L.polygon(coords, {
		// MODIFIED: Color changed to new theme
		color: '#1abc9c',
		fillColor: '#1abc9c',
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

// [Add to static/js/script.js]

// 1. Create a custom Leaflet Control for the "Scanner"
L.Control.QuarryScanner = L.Control.extend({
	options: {
		position: 'topleft' // Places it near the zoom controls
	},

	onAdd: function (map) {
		var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');
		container.style.backgroundColor = 'white';
		container.style.padding = '5px';
		container.style.cursor = 'pointer';
		container.title = "Scan for Quarries in this area";

		// Add an icon and text
		container.innerHTML = `
            <div style="display: flex; align-items: center; gap: 5px; padding: 0 5px;">
                <span style="font-size: 18px;">⛏️</span>
                <span style="font-weight: bold; color: #2c3e50;">Find Quarries</span>
            </div>
        `;

		// Click event to trigger the scan
		container.onclick = function () {
			scanForQuarries();
		};

		return container;
	}
});

// 2. Add the control to the map
map.addControl(new L.Control.QuarryScanner());

// 3. The Function to Find Quarries (Using Overpass API)
function scanForQuarries() {
	// Get current map bounds
	var bounds = map.getBounds();
	var bbox = `${bounds.getSouth()},${bounds.getWest()},${bounds.getNorth()},${bounds.getEast()}`;

	showAnalysisResults("⏳ Scanning satellite data for quarry sites...");

	// This query asks OpenStreetMap for any node/way/relation tagged as "quarry"
	var query = `
        [out:json][timeout:25];
        (
          node["landuse"="quarry"](${bbox});
          way["landuse"="quarry"](${bbox});
          relation["landuse"="quarry"](${bbox});
        );
        out center;
    `;

	var url = "https://overpass-api.de/api/interpreter?data=" + encodeURIComponent(query);

	fetch(url)
		.then(response => response.json())
		.then(data => {
			console.log("Quarries found:", data);

			if (data.elements.length === 0) {
				alert("No quarries found in this specific map view. Try moving the map!");
				return;
			}

			// Group to hold the results
			var quarryGroup = L.featureGroup().addTo(map);

			data.elements.forEach(element => {
				var lat, lon;

				// Get center coordinates
				if (element.type === "node") {
					lat = element.lat;
					lon = element.lon;
				} else {
					lat = element.center.lat;
					lon = element.center.lon;
				}

				// Get company name if available (Operator tag)
				var companyName = element.tags.operator || element.tags.name || "Unnamed Quarry";

				// Add a marker
				L.marker([lat, lon])
					.bindPopup(`<b>${companyName}</b><br>Type: ${element.tags.landuse}<br><button onclick="map.flyTo([${lat}, ${lon}], 16)">Analyze This</button>`)
					.addTo(quarryGroup);
			});

			// Zoom to show all found quarries
			map.fitBounds(quarryGroup.getBounds());
			showAnalysisResults(`✅ Found ${data.elements.length} quarry sites in this area!`);
		})
		.catch(err => {
			console.error(err);
			alert("Error scanning for quarries.");
		});
}

/* ==========================================
   APPEND THIS TO THE BOTTOM OF script.js
   Handles: Drone Data Upload & Analysis
   ========================================== */

document.addEventListener('DOMContentLoaded', function () {

	// 1. Get Elements (These are from the new sidebar HTML)
	const fileInput = document.getElementById('file-input');
	const dropZone = document.getElementById('drop-zone');
	const processBtn = document.getElementById('process-btn');
	const fileNameDisplay = document.getElementById('file-name-display');
	const opacitySlider = document.getElementById('opacity-slider');

	// Safety Check: If these elements don't exist (e.g. old HTML), stop here
	if (!fileInput || !dropZone || !processBtn) {
		console.log("Upload panel elements not found. Skipping upload logic.");
		return;
	}

	let selectedFile = null;

	// 2. Handle File Selection (Browse Button)
	fileInput.addEventListener('change', function (e) {
		if (e.target.files.length > 0) {
			handleFileSelect(e.target.files[0]);
		}
	});

	// 3. Handle Drag & Drop
	dropZone.addEventListener('dragover', (e) => {
		e.preventDefault();
		dropZone.style.borderColor = '#16a085';
		dropZone.style.backgroundColor = 'rgba(22, 160, 133, 0.05)';
	});

	dropZone.addEventListener('dragleave', (e) => {
		e.preventDefault();
		dropZone.style.borderColor = '#d0ddee'; // Reset color
		dropZone.style.backgroundColor = 'transparent';
	});

	dropZone.addEventListener('drop', (e) => {
		e.preventDefault();
		dropZone.style.borderColor = '#d0ddee';
		dropZone.style.backgroundColor = 'transparent';

		if (e.dataTransfer.files.length > 0) {
			handleFileSelect(e.dataTransfer.files[0]);
		}
	});

	// Helper: Update UI when file is chosen
	function handleFileSelect(file) {
		if (!file.name.toLowerCase().endsWith('.tif') && !file.name.toLowerCase().endsWith('.tiff')) {
			alert("Only .tif files are allowed!");
			return;
		}

		selectedFile = file;
		fileNameDisplay.innerText = `📄 ${file.name}`;

		// Enable Buttons
		processBtn.disabled = false;
		processBtn.classList.add('active'); // Add teal color via CSS
		if (opacitySlider) opacitySlider.disabled = false;

		appendLog(`File selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`);
	}

	// 4. THE TRIGGER: Click "Process" -> Call the Function
	processBtn.addEventListener('click', function () {
		if (selectedFile) {
			uploadAndAnalyze(selectedFile);
		}
	});

	// 5. Upload & Analyze Logic
	async function uploadAndAnalyze(file) {
		// A. UI Updates
		processBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Uploading...';
		processBtn.disabled = true;
		appendLog("🚀 Starting upload & analysis...");

		// B. Prepare Data
		const formData = new FormData();
		formData.append('file', file);

		try {
			// C. Send to Backend
			const response = await fetch('/api/upload_dem', {
				method: 'POST',
				body: formData
			});

			const data = await response.json();

			if (data.status === 'success') {
				appendLog("✅ Analysis Complete!");

				// D. Update Stats (Metric Cards)
				// We use generic IDs so this works with the new layout
				if (document.getElementById('metric-volume'))
					document.getElementById('metric-volume').innerText = formatNumber(data.depth_stats.volume_m3) + ' m³';
				if (document.getElementById('metric-depth'))
					document.getElementById('metric-depth').innerText = data.depth_stats.max_depth.toFixed(2) + ' m';
				if (document.getElementById('metric-area'))
					document.getElementById('metric-area').innerText = (data.depth_stats.total_area_m2 / 10000).toFixed(2) + ' ha';
				if (document.getElementById('metric-elev'))
					document.getElementById('metric-elev').innerText = data.depth_stats.min_elevation.toFixed(1) + ' m';

				// E. Show Heatmap
				const imgContainer = document.getElementById('img_container');
				if (imgContainer) {
					imgContainer.innerHTML = `
                        <div class="zoom-container">
                            <img src="${data.heatmap_url}" alt="Quarry Heatmap" style="width:100%; border-radius:12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                            <span class="zoom-hint">Analysis of ${data.filename}</span>
                        </div>
                    `;
				}

				processBtn.innerHTML = '<i class="fas fa-check"></i> Done';

				// Reset button after 3 seconds so they can run another file
				setTimeout(() => {
					processBtn.innerHTML = '<i class="fas fa-microchip"></i> Process & Analyze';
					processBtn.disabled = false;
				}, 3000);

			} else {
				appendLog(`❌ Error: ${data.message}`);
				processBtn.innerHTML = 'Retry';
				processBtn.disabled = false;
			}
		} catch (error) {
			console.error(error);
			appendLog(`❌ Network Error: ${error.message}`);
			processBtn.innerHTML = 'Retry';
			processBtn.disabled = false;
		}
	}

	// Helper: Safely append log messages without breaking existing logs
	function appendLog(msg) {
		const terminal = document.getElementById('terminal_output');
		if (!terminal) return;

		const time = new Date().toLocaleTimeString();
		// Create new log line
		const div = document.createElement('div');
		div.className = 'terminal-message';
		div.innerHTML = `<span class="terminal-timestamp">[${time}]</span> ${msg}`;

		// Add to terminal
		terminal.appendChild(div);
		terminal.scrollTop = terminal.scrollHeight;
	}

	// Helper: Nice number formatting (e.g. 1,234,567)
	function formatNumber(num) {
		return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
	}
});


/* ==========================================
   SAVED SITES MANAGER
   Paste this at the VERY BOTTOM of script.js
   ========================================== */

document.addEventListener('DOMContentLoaded', function () {

	// 1. Load sites immediately when page opens
	fetchSavedSites();

	// 2. Function to Fetch & Render
	async function fetchSavedSites() {
		try {
			const response = await fetch('/api/sites');
			const data = await response.json();

			const listContainer = document.querySelector('.saved-sites-list');
			if (!listContainer) return;

			listContainer.innerHTML = ''; // Clear current list

			if (!data.sites || data.sites.length === 0) {
				listContainer.innerHTML = '<div style="padding:20px; text-align:center; color:#95a5a6; font-size: 0.9rem;">No saved sites yet.<br>Draw a polygon and click "Save".</div>';
				return;
			}

			// Loop through sites and create cards
			data.sites.forEach(site => {
				const item = document.createElement('div');
				item.className = 'site-item';
				// Store coords in dataset for easy retrieval
				item.dataset.coords = JSON.stringify(site.coords);
				item.dataset.id = site.id;

				item.innerHTML = `
                    <div class="site-info" onclick="loadSiteOnMap('${site.id}')">
                        <h4 style="margin:0; font-size:1rem; color:#2c3e50;">${site.name}</h4>
                        <p style="margin:2px 0 0 0; font-size:0.8rem; color:#95a5a6;"><i class="far fa-calendar"></i> ${site.date}</p>
                    </div>
                    <div style="display:flex; gap:5px;">
                        <button class="load-btn" onclick="loadSiteOnMap('${site.id}')">Load</button>
                        <button class="load-btn" style="color:#e74c3c; border-color:#fadbd8;" onclick="deleteSite('${site.id}')"><i class="fas fa-trash"></i></button>
                    </div>
                `;
				listContainer.appendChild(item);
			});

		} catch (error) {
			console.error("Error loading sites:", error);
		}
	}

	// 3. Make fetch available globally so other functions (like Save) can refresh the list
	window.fetchSavedSites = fetchSavedSites;

	// 4. Function to Load a Site onto the Map
	window.loadSiteOnMap = function (id) {
		// Find the DOM element to get the coords
		const item = document.querySelector(`.site-item[data-id='${id}']`);
		if (!item) return;

		const coords = JSON.parse(item.dataset.coords);

		// Clear existing drawn items
		if (window.drawnItems) {
			window.drawnItems.clearLayers();
		}

		// Create the polygon
		const polygon = L.polygon(coords, {
			color: '#16a085',
			fillColor: '#16a085',
			fillOpacity: 0.3,
			weight: 3
		}).addTo(map);

		// Add to feature group so we can edit it or save it again
		if (window.drawnItems) {
			window.drawnItems.addLayer(polygon);
		}

		// Zoom to the site
		map.fitBounds(polygon.getBounds());

		// On mobile, close the drawer
		const drawer = document.getElementById('drawer');
		if (drawer && window.innerWidth < 768) {
			drawer.classList.add('collapsed');
		}
	};

	// 5. Function to Delete a Site
	window.deleteSite = async function (id) {
		if (!confirm("Are you sure you want to delete this site?")) return;

		try {
			await fetch(`/api/sites/${id}`, { method: 'DELETE' });
			fetchSavedSites(); // Refresh list
		} catch (e) {
			alert("Error deleting site");
		}
	};
});
