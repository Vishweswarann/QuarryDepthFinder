# [file name]: test_depth.py
# [file content begin]
from flask import Blueprint, jsonify, request
import numpy as np

def create_test_routes(app):
    test = Blueprint("test", __name__)
    
    @test.route("/test_depth")
    def test_depth():
        """Simple test page for depth calculation"""
        return """
        <html>
        <head>
            <title>Test Depth Calculation</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                button { padding: 15px 30px; font-size: 16px; margin: 10px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }
                .result { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 10px; }
                .stats { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; }
                pre { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 5px; overflow-x: auto; }
            </style>
        </head>
        <body>
            <h1>🧪 Test Quarry Depth Calculation</h1>
            <p>This tool analyzes your quarry DEM data and calculates depth, volume, and other metrics.</p>
            
            <button onclick="calculateDepth()">🔍 Calculate Depth</button>
            <button onclick="generateProfile()">📈 Generate Profile</button>
            
            <div id="results" class="result">
                <p>Click buttons above to analyze your quarry...</p>
            </div>
            
            <script>
            async function calculateDepth() {
                showLoading("Calculating depth...");
                
                const response = await fetch('/api/analyze_depth', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({dem_file: 'cropped.tif'})
                });
                const data = await response.json();
                
                let html = '<h3>📊 Depth Analysis Results:</h3>';
                if (data.status === 'success') {
                    html += '<div class="stats">';
                    html += '<h4>Key Metrics:</h4>';
                    html += '<ul>';
                    html += '<li><strong>Max Depth:</strong> ' + data.depth_stats.max_depth.toFixed(1) + ' meters</li>';
                    html += '<li><strong>Average Depth:</strong> ' + data.depth_stats.mean_depth.toFixed(1) + ' meters</li>';
                    html += '<li><strong>Excavation Volume:</strong> ' + data.depth_stats.volume_m3.toLocaleString() + ' m³</li>';
                    html += '<li><strong>Quarry Area:</strong> ' + data.depth_stats.total_area_m2.toLocaleString() + ' m²</li>';
                    html += '</ul>';
                    html += '</div>';
                    
                    html += '<h4>Depth Visualization:</h4>';
                    html += '<img src="' + data.visualization + '" style="max-width: 100%; border: 1px solid #ccc;">';
                } else {
                    html += '<p style="color: red;">❌ Error: ' + data.message + '</p>';
                }
                
                document.getElementById('results').innerHTML = html;
            }
            
            async function generateProfile() {
                showLoading("Generating profile...");
                
                const response = await fetch('/api/generate_profile', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({dem_file: 'cropped.tif'})
                });
                const data = await response.json();
                
                let html = '<h3>📈 Depth Profile:</h3>';
                if (data.status === 'success') {
                    html += '<img src="' + data.profile_image + '" style="max-width: 100%; border: 1px solid #ccc;">';
                } else {
                    html += '<p style="color: red;">❌ Error: ' + data.message + '</p>';
                }
                
                document.getElementById('results').innerHTML = html;
            }
            
            function showLoading(message) {
                document.getElementById('results').innerHTML = '<p>⏳ ' + message + '</p>';
            }
            </script>
        </body>
        </html>
        """
    
    @test.route("/api/generate_profile", methods=["POST"])
    def generate_profile():
        """Generate depth profile cross-section"""
        try:
            # Import here to avoid circular imports
            from depth_analysis import generate_depth_profile
            profile_path = generate_depth_profile("cropped.tif")
            return jsonify({
                "status": "success",
                "profile_image": profile_path
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    return test
# [file content end]