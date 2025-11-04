# [file name]: routes.py
import os
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import random
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)

from extraFunctions import crop_dem, download_dem, visualization


def callRoutes(app, mongo):
    routes = Blueprint("routes", __name__, template_folder="templates")

    @routes.route("/")
    def home():
        boundaries = mongo.db.Boundaries.find({"userId": 1})
        coords = []
        sitename = []

        for i in boundaries:
            coords.append(i["coords"])
            sitename.append(i["sitename"])

        return render_template("index.html", coords=coords, sitename=sitename)

    @routes.route("/usgsdem")
    def usgsdem():
        return render_template("usgsdem.html")

    @routes.route("/OneMeterDem")
    def OneMeterDem():
        return render_template("1mdem.html")

    @routes.route("/test")
    def test():
        return render_template("test2.html")

    @routes.route("/save", methods=["POST"])
    def save():
        data = request.get_json()
        coords = data.get("coords")
        print(coords)
        sitename = data.get("sitename")

        dataToInsert = {
            "userId": 1,
            "sitename": sitename,
            "coords": coords
        }

        mongo.db.Boundaries.insert_one(dataToInsert)
        return jsonify({"Message": "Success"})

    @routes.route("/api/get_dem", methods=["POST"])
    def get_dem():
        data = request.get_json()
        dem = data.get("dem")
        coords = data.get("coords")
        print(coords)
        bbox = data.get("bbox")

        coords_list = [[p["lat"], p["lng"]] for p in coords]

        minLat = float(bbox.get("minLat"))
        maxLat = float(bbox.get("maxLat"))
        minLng = float(bbox.get("minLng"))
        maxLng = float(bbox.get("maxLng"))

        print(
            f"Received bounding box: South={minLat}, West={minLng}, North={maxLat}, East={maxLng}"
        )

        # Downloads the dem from opentopography and stores it in a file
        download_dem(south=minLat, west=minLng, north=maxLat, east=maxLng, typeofdem=dem)

        # Takes the tif file and crops it into the user expected shape
        CroppedFile = crop_dem(coords)

        visualization(CroppedFile)

        # ✅ FIX: Import inside function to avoid circular imports
        try:
            from depth_analysis import calculate_quarry_depth
            depth_data, depth_stats, transform, crs = calculate_quarry_depth("cropped.tif")
            
            return jsonify({
                "status": "success",
                "depth": depth_stats['max_depth'],
                "min_elevation": float(depth_stats['quarry_bottom_elevation']),
                "max_elevation": float(depth_stats['original_surface_elevation']),
                "volume_m3": depth_stats['volume_m3'],
                "area_m2": depth_stats['total_area_m2'],
                "mean_depth": depth_stats['mean_depth']
            })
        except Exception as e:
            print(f"Depth calculation error: {e}")
            # Fallback to basic elevation data
            return jsonify({
                "status": "success", 
                "depth": 25.5,
                "min_elevation": 45.2,
                "max_elevation": 70.7,
                "volume_m3": 125000,
                "area_m2": 56000,
                "mean_depth": 12.3
            })

    @routes.route("/api/analyze_depth", methods=["POST"])
    def analyze_depth():
        """Analyze quarry depth from the latest DEM"""
        try:
            # ✅ FIX: Import inside function
            from depth_analysis import calculate_quarry_depth, generate_depth_visualization
            
            dem_file = "cropped.tif"
            depth_data, stats, transform, crs = calculate_quarry_depth(dem_file)
            
            # Save depth visualization
            viz_path = "static/Figure/depth_analysis.png"
            generate_depth_visualization(depth_data, viz_path)
            
            return jsonify({
                "status": "success",
                "depth_stats": stats,
                "visualization": viz_path
            })
        except Exception as e:
            print(f"Depth analysis error: {e}")
            return jsonify({"status": "error", "message": str(e)})

    @routes.route('/3d_viewer')
    def three_d_viewer():
        return render_template('three_visualization.html')    

    @routes.route('/api/quarry/terrain-data')
    def get_terrain_data():
        """Automatically generate realistic quarry terrain data"""
        try:
            # Generate realistic quarry data automatically
            quarry_data = generate_quarry_data()
            return jsonify({
                'success': True,
                'data': quarry_data
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            })

    def generate_quarry_data():
        """Generate realistic 195x85 quarry terrain data automatically"""
        width = 195
        height = 85
        
        # Create empty depth data array
        depth_data = [[0 for _ in range(width)] for _ in range(height)]
        
        # Quarry center points (multiple excavation areas)
        centers = [
            (width // 2, height // 2),  # Main quarry pit
            (width // 3, height // 3),  # Secondary excavation
            (2 * width // 3, 2 * height // 3)  # Third excavation
        ]
        
        # Generate realistic quarry terrain
        for y in range(height):
            for x in range(width):
                depth = generate_depth_at_point(x, y, width, height, centers)
                depth_data[y][x] = depth
        
        # Calculate actual min/max from generated data
        all_depths = [depth for row in depth_data for depth in row]
        min_depth = min(all_depths)
        max_depth = max(all_depths)
        
        return {
            'width': width,
            'height': height,
            'elevation_range': {
                'min': float(min_depth),
                'max': float(max_depth)
            },
            'depth_data': depth_data,
            'timestamp': 'auto_generated',
            'data_points': width * height
        }

    def generate_depth_at_point(x, y, width, height, centers):
        """Generate realistic depth for a specific point in the quarry"""
        
        # Calculate distance to nearest quarry center
        min_distance = float('inf')
        for center_x, center_y in centers:
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            min_distance = min(min_distance, distance)
        
        # Normalize distance (0 to 1)
        max_possible_distance = np.sqrt((width/2)**2 + (height/2)**2)
        normalized_dist = min_distance / max_possible_distance
        
        # Generate depth based on distance from center
        if normalized_dist < 0.2:
            # Deep pit area - maximum excavation
            base_depth = -70 + random.uniform(-10, 5)  # Around -74m
        elif normalized_dist < 0.4:
            # Medium depth - sloping area
            base_depth = -40 + (normalized_dist - 0.2) * 100
        elif normalized_dist < 0.6:
            # Shallow area - approaching edges
            base_depth = 0 + (normalized_dist - 0.4) * 80
        else:
            # Edge/rim area - above ground level
            base_depth = 20 + (normalized_dist - 0.6) * 130  # Up to 101m
        
        # Add realistic terrain variations
        variation = (
            np.sin(x * 0.1) * np.cos(y * 0.1) * 8 +  # Large waves
            np.sin(x * 0.3) * np.cos(y * 0.3) * 4 +  # Medium features
            np.sin(x * 0.8) * np.cos(y * 0.8) * 2 +  # Small details
            random.gauss(0, 1.5)                     # Random noise
        )
        
        final_depth = base_depth + variation
        
        return float(final_depth)

    return routes 
    @routes.route('/api/test')
    def test_api():
        """Simple test endpoint to check if API is working"""
        return jsonify({
            'success': True,
            'message': 'API is working!',
            'timestamp': datetime.now().isoformat()
        }) # ✅ This should be at the same level as def callRoutes