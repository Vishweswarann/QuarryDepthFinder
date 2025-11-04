# [file name]: advanced_routes.py
# [file content begin]
from flask import Blueprint, jsonify, request, send_file, render_template
import os
from datetime import datetime
import json
import tempfile

def create_advanced_routes(app, mongo):
    # ✅ FIX: Correct blueprint definition
    advanced_bp = Blueprint("advanced_bp", __name__)
    
    @advanced_bp.route("/advanced_features")
    def advanced_features():
        """Page to access all advanced features"""
        feature_status = {
            "Depth Analysis": True,
            "Volume Calculation": True, 
            "Slope Analysis": True,
            "3D Visualization": True,
            "Report Generation": False
        }
        
        status_html = ""
        for feature, available in feature_status.items():
            status = "✅ Available" if available else "❌ Not Available"
            status_html += f"<li><strong>{feature}:</strong> {status}</li>"
        
        return f"""
        <html>
        <head>
            <title>Advanced Quarry Features</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .feature-list {{ background: #f5f5f5; padding: 20px; border-radius: 10px; }}
                button {{ padding: 10px 15px; margin: 5px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }}
                button:disabled {{ background: #cccccc; cursor: not-allowed; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 Advanced Quarry Analysis Features</h1>
                
                <div class="feature-list">
                    <h2>Feature Status:</h2>
                    <ul>
                        {status_html}
                    </ul>
                </div>
                
                <div>
                    <h2>Available Features:</h2>
                    <button onclick="analyzeDepth()">🔍 Depth Analysis</button>
                    <button onclick="calculateVolume()">📊 Volume Calculation</button>
                    <button onclick="analyzeSlope()">🏔️ Slope Analysis</button>
                    <a href="/3d_viewer" target="_blank"><button>🗺️ 3D Visualization</button></a>
                    <a href="/test_depth" target="_blank"><button>🧪 Test Depth</button></a>
                    <a href="/" target="_blank"><button>🗺️ Main Map</button></a>
                </div>
                
                <div id="results" style="margin-top: 20px; padding: 15px; background: #f0f0f0; border-radius: 5px; min-height: 100px;">
                    <p>Click buttons above to see results...</p>
                </div>
                
                <script>
                async function analyzeDepth() {{
                    showLoading("Analyzing depth...");
                    const response = await fetch('/api/analyze_depth', {{method: 'POST', headers: {{'Content-Type': 'application/json'}}}});
                    const data = await response.json();
                    displayResults('Depth Analysis', data);
                }}
                
                async function calculateVolume() {{
                    showLoading("Calculating volume...");
                    const response = await fetch('/api/calculate_volume', {{method: 'POST', headers: {{'Content-Type': 'application/json'}}}});
                    const data = await response.json();
                    displayResults('Volume Calculation', data);
                }}
                
                async function analyzeSlope() {{
                    showLoading("Analyzing slope...");
                    const response = await fetch('/api/analyze_slope', {{method: 'POST', headers: {{'Content-Type': 'application/json'}}}});
                    const data = await response.json();
                    displayResults('Slope Analysis', data);
                }}
                
                function displayResults(title, data) {{
                    let html = `<h3>${{title}}:</h3>`;
                    if (data.status === 'success') {{
                        html += '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                    }} else {{
                        html += '<p style="color: red;">❌ Error: ' + data.message + '</p>';
                    }}
                    document.getElementById('results').innerHTML = html;
                }}
                
                function showLoading(message) {{
                    document.getElementById('results').innerHTML = '<p>⏳ ' + message + '</p>';
                }}
                </script>
            </div>
        </body>
        </html>
        """
    
    @advanced_bp.route("/api/analyze_depth", methods=["POST"])
    def analyze_depth():
        """Analyze quarry depth from DEM data"""
        try:
            from depth_analysis import calculate_quarry_depth, generate_depth_visualization
            
            depth_data, stats, transform, crs = calculate_quarry_depth("cropped.tif")
            
            # Save depth visualization
            viz_path = "static/Figure/depth_analysis.png"
            generate_depth_visualization(depth_data, viz_path)
            
            return jsonify({
                "status": "success",
                "depth_stats": stats,
                "visualization": viz_path
            })
            
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    
    @advanced_bp.route("/api/calculate_volume", methods=["POST"])
    def calculate_volume():
        """Calculate excavation volume"""
        try:
            from volume_calculator import calculate_excavation_volume
            
            volume_data = calculate_excavation_volume("cropped.tif")
            
            return jsonify({
                "status": "success", 
                "volume_data": volume_data
            })
            
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    
    @advanced_bp.route("/api/analyze_slope", methods=["POST"])
    def analyze_slope():
        """Analyze slope and generate contours"""
        try:
            from slope_analysis import analyze_slope_contours
            
            slope_data = analyze_slope_contours("cropped.tif")
            
            return jsonify({
                "status": "success",
                "slope_data": slope_data
            })
            
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    @advanced_bp.route("/api/get_3d_data")
    def get_3d_data():
        """Provide latest 3D terrain data for visualization"""
        try:
            from three_visualization import get_latest_3d_data
            terrain_file = get_latest_3d_data()
            
            with open(terrain_file, 'r') as f:
                terrain_data = json.load(f)
            
            return jsonify(terrain_data)
            
        except Exception as e:
            return jsonify({
                "status": "error", 
                "message": f"3D data error: {str(e)}",
                "width": 50,
                "height": 50,
                "elevation": [[0]*50]*50,
                "minElevation": 0,
                "maxElevation": 100
            })

    return advanced_bp
    @advanced_bp.route("/3d_viewer")
    def three_d_viewer():
        """Serve 3D visualization page"""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>3D Quarry Visualization</title>
            <style>
                body { 
                    margin: 0; 
                    overflow: hidden; 
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                #container { 
                    position: relative; 
                    width: 100vw; 
                    height: 100vh; 
                }
                #infoPanel {
                    position: absolute;
                    top: 10px;
                    left: 10px;
                    background: rgba(0,0,0,0.8);
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    z-index: 100;
                    max-width: 300px;
                    backdrop-filter: blur(10px);
                }
                #controls {
                    position: absolute;
                    bottom: 20px;
                    left: 20px;
                    background: rgba(0,0,0,0.8);
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    z-index: 100;
                    backdrop-filter: blur(10px);
                }
                button {
                    background: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    margin: 5px;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: all 0.3s;
                }
                button:hover {
                    background: #45a049;
                    transform: scale(1.05);
                }
                .slider-container {
                    margin: 10px 0;
                }
                .slider-container label {
                    display: block;
                    margin-bottom: 5px;
                    font-size: 14px;
                }
                .loading {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    color: white;
                    font-size: 18px;
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <div id="container">
                <div class="loading" id="loading">
                    <div style="font-size: 24px; margin-bottom: 10px;">🔄</div>
                    Loading 3D Terrain Data...
                </div>
                
                <div id="infoPanel">
                    <h3 style="margin: 0 0 10px 0;">🏔️ 3D Quarry Visualization</h3>
                    <div id="stats">
                        <p>Loading terrain data...</p>
                    </div>
                </div>
                
                <div id="controls">
                    <button onclick="toggleView()">🔄 Toggle View</button>
                    <button onclick="resetCamera()">🎯 Reset Camera</button>
                    <button onclick="toggleRotation()" id="rotationBtn">⏹️ Stop Rotation</button>
                    
                    <div class="slider-container">
                        <label>📏 Vertical Scale: <span id="scaleValue">3</span>x</label>
                        <input type="range" id="verticalScale" min="1" max="10" value="3" step="0.5" onchange="updateScale(this.value)">
                    </div>
                    <div class="slider-container">
                        <label>⚡ Rotation Speed: <span id="rotationValue">0.2</span></label>
                        <input type="range" id="rotationSpeed" min="0" max="1" step="0.1" value="0.2" onchange="updateRotation(this.value)">
                    </div>
                </div>
            </div>

            <!-- Three.js Library -->
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
            
            <script>
                let scene, camera, renderer, controls, terrain;
                let isDepthView = false;
                let currentScale = 3;
                let rotationSpeed = 0.2;
                let isRotating = true;

                init();

                function init() {
                    // Create scene
                    scene = new THREE.Scene();
                    scene.background = new THREE.Color(0x87CEEB);
                    
                    // Create camera
                    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
                    camera.position.set(0, 50, 50);
                    
                    // Create renderer
                    renderer = new THREE.WebGLRenderer({ antialias: true });
                    renderer.setSize(window.innerWidth, window.innerHeight);
                    document.getElementById('container').appendChild(renderer.domElement);
                    
                    // Add controls
                    controls = new THREE.OrbitControls(camera, renderer.domElement);
                    controls.enableDamping = true;
                    controls.dampingFactor = 0.05;
                    
                    // Add lighting
                    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
                    scene.add(ambientLight);
                    
                    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                    directionalLight.position.set(50, 50, 50);
                    scene.add(directionalLight);
                    
                    // Load terrain data
                    loadTerrainData();
                    
                    // Handle window resize
                    window.addEventListener('resize', onWindowResize);
                    
                    // Start animation loop
                    animate();
                }

                function loadTerrainData() {
                    fetch('/api/get_3d_data')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('loading').style.display = 'none';
                            createTerrain(data);
                            updateStats(data);
                        })
                        .catch(error => {
                            console.error('Error loading terrain data:', error);
                            document.getElementById('stats').innerHTML = '<p style="color: red;">Error loading terrain data</p>';
                            document.getElementById('loading').innerHTML = '❌ Failed to load terrain data';
                        });
                }

                function createTerrain(terrainData) {
                    // Remove existing terrain
                    if (terrain) {
                        scene.remove(terrain);
                    }
                    
                    const width = terrainData.width || 50;
                    const height = terrainData.height || 50;
                    const elevation = terrainData.elevation || Array(height).fill().map(() => Array(width).fill(0));
                    const scale = terrainData.scale || currentScale;
                    
                    console.log('Creating terrain:', { width, height, scale });
                    
                    // Create geometry
                    const geometry = new THREE.PlaneGeometry(width, height, width - 1, height - 1);
                    
                    // Set vertex positions based on elevation
                    const positions = geometry.attributes.position.array;
                    for (let i = 0; i < positions.length; i += 3) {
                        const x = Math.floor((i / 3) % width);
                        const y = Math.floor((i / 3) / width);
                        
                        if (x < width && y < height) {
                            const elev = elevation[y] ? (elevation[y][x] || 0) : 0;
                            positions[i + 2] = elev * scale;
                        }
                    }
                    
                    geometry.computeVertexNormals();
                    
                    // Create material with colors based on elevation
                    const material = new THREE.MeshLambertMaterial({ 
                        color: 0x3a7ca5,
                        wireframe: false,
                        flatShading: false
                    });
                    
                    terrain = new THREE.Mesh(geometry, material);
                    terrain.rotation.x = -Math.PI / 2;
                    scene.add(terrain);
                    
                    // Add grid helper
                    const gridHelper = new THREE.GridHelper(Math.max(width, height), 10);
                    scene.add(gridHelper);
                }

                function toggleView() {
                    isDepthView = !isDepthView;
                    // Switch between elevation and depth view
                    loadTerrainData();
                }

                function toggleRotation() {
                    isRotating = !isRotating;
                    document.getElementById('rotationBtn').textContent = isRotating ? '⏹️ Stop Rotation' : '▶️ Start Rotation';
                }

                function resetCamera() {
                    controls.reset();
                    camera.position.set(0, 50, 50);
                    controls.update();
                }

                function updateScale(value) {
                    currentScale = parseFloat(value);
                    document.getElementById('scaleValue').textContent = value;
                    loadTerrainData();
                }

                function updateRotation(value) {
                    rotationSpeed = parseFloat(value);
                    document.getElementById('rotationValue').textContent = value;
                }

                function updateStats(data) {
                    const stats = document.getElementById('stats');
                    stats.innerHTML = `
                        <p><strong>Terrain Size:</strong> ${data.width || 'N/A'} × ${data.height || 'N/A'}</p>
                        <p><strong>Elevation Range:</strong> ${(data.minElevation || 0).toFixed(1)}m - ${(data.maxElevation || 0).toFixed(1)}m</p>
                        <p><strong>Mean Elevation:</strong> ${(data.meanElevation || 0).toFixed(1)}m</p>
                        <p><strong>View:</strong> ${isDepthView ? 'Depth Analysis' : 'Elevation'}</p>
                        <p><strong>Data Source:</strong> ${data.dataSource || 'Current Quarry'}</p>
                    `;
                }

                function onWindowResize() {
                    camera.aspect = window.innerWidth / window.innerHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(window.innerWidth, window.innerHeight);
                }

                function animate() {
                    requestAnimationFrame(animate);
                    
                    // Auto-rotate if enabled
                    if (isRotating && rotationSpeed > 0) {
                        terrain.rotation.y += rotationSpeed * 0.01;
                    }
                    
                    controls.update();
                    renderer.render(scene, camera);
                }
            </script>
        </body>
        </html>
        """
# [file content end]