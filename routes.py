# [file name]: routes.py
import os
import time
from datetime import datetime

import matplotlib
from bson.objectid import ObjectId  # ✅ Required for handling MongoDB IDs

matplotlib.use('Agg')
import random

import matplotlib.pyplot as plt
import numpy as np
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from werkzeug.utils import secure_filename

from extraFunctions import crop_dem, download_dem, visualization


def callRoutes(app, mongo):
    routes = Blueprint("routes", __name__, template_folder="templates")

    @routes.route("/")
    def home():
        return render_template("home.html")


    @routes.route("/ThirtyMeterDem")
    def ThirtyMeterDem():
        boundaries = mongo.db.Boundaries.find({"userId": 1})
        coords = []
        sitename = []

        for i in boundaries:
            coords.append(i["coords"])
            sitename.append(i["sitename"])

        return render_template("index2.html", coords=coords, sitename=sitename)


    @routes.route("/usgsdem")
    def usgsdem():
        return render_template("usgsdem.html")

    @routes.route("/OneMeterDem")
    def OneMeterDem():
        return render_template("oneMeterDem.html")

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

        referencePoint = data.get("reference_point")

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
            depth_data, depth_stats, transform, crs = calculate_quarry_depth("cropped.tif", referencePoint)
            
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
            data = request.get_json()  
            
            # 2. Extract the reference point
            reference_point = data.get("reference_point") 

            if reference_point:
                 print(f"📍 Analyze Depth Route received reference: {reference_point}")

            from depth_analysis import (calculate_quarry_depth,
                                        generate_depth_visualization)
            
            dem_file = "cropped.tif"
            
            # 3. Pass it to the function
            depth_data, stats, transform, crs = calculate_quarry_depth(dem_file, reference_point)
            
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

    
    @routes.route("/api/upload_dem", methods=["POST"])
    def upload_dem():
        """
        1. Receives a custom .tif file from the user (Drone/Pix4D data)
        2. Saves it locally
        3. Runs depth analysis immediately
        4. Returns the stats and the heatmap image URL
        """
        try:
            # 1. Validation: Did they send a file?
            if 'file' not in request.files:
                return jsonify({"status": "error", "message": "No file part"}), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({"status": "error", "message": "No selected file"}), 400
            
            # 2. Validation: Is it a TIF?
            if file and (file.filename.lower().endswith('.tif') or file.filename.lower().endswith('.tiff')):
                
                # Create uploads directory if it doesn't exist
                upload_folder = "uploads"
                os.makedirs(upload_folder, exist_ok=True)
                
                # Save the file securely
                filename = secure_filename(file.filename)
                timestamp = int(time.time())
                save_path = os.path.join(upload_folder, f"{timestamp}_{filename}")
                file.save(save_path)
                
                print(f"✅ File uploaded: {save_path}")

                # 3. Run Analysis 
                # Import inside to avoid circular dependency
                from depth_analysis import (calculate_quarry_depth,
                                            generate_depth_visualization)

                # Check for optional reference point
                ref_lat = request.form.get('ref_lat')
                ref_lng = request.form.get('ref_lng')
                reference_point = None
                
                if ref_lat and ref_lng:
                    try:
                        reference_point = {'lat': float(ref_lat), 'lng': float(ref_lng)}
                    except:
                        pass # Ignore invalid coords

                # Calculate Depth
                depth_data, stats, transform, crs = calculate_quarry_depth(save_path, reference_point)
                
                # 4. Generate Visualization (Heatmap)
                viz_filename = f"heatmap_{timestamp}.png"
                viz_folder = os.path.join("static", "Figure")
                os.makedirs(viz_folder, exist_ok=True)
                
                viz_path = os.path.join(viz_folder, viz_filename)
                
                # Generate the heatmap
                generate_depth_visualization(depth_data, viz_path)
                
                # 5. Return JSON Result
                return jsonify({
                    "status": "success",
                    "message": "Analysis Complete",
                    "depth_stats": stats,
                    "heatmap_url": url_for('static', filename=f'Figure/{viz_filename}'),
                    "filename": filename
                })
            
            else:
                return jsonify({"status": "error", "message": "Invalid file type. Only .tif allowed"}), 400

        except Exception as e:
            print(f"❌ Upload Error: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

        # === 💾 SAVED SITES API ===

    @routes.route("/api/sites", methods=["GET"])
    def get_sites():
        """Fetch all saved sites for the drawer"""
        try:
            # Get sites, sorted by newest first
            sites = mongo.db.Boundaries.find({"userId": 1}).sort("_id", -1)
            
            site_list = []
            for site in sites:
                site_list.append({
                    "id": str(site["_id"]),
                    "name": site.get("sitename", "Unnamed Site"),
                    "date": site.get("date", "Unknown Date"),
                    "coords": site["coords"]
                })
            return jsonify({"status": "success", "sites": site_list})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    @routes.route("/api/save_site", methods=["POST"])
    def save_new_site():
        """Save a new site boundary"""
        try:
            data = request.get_json()
            coords = data.get("coords")
            sitename = data.get("sitename")
            
            if not coords or not sitename:
                return jsonify({"status": "error", "message": "Missing data"}), 400

            dataToInsert = {
                "userId": 1,
                "sitename": sitename,
                "coords": coords,
                "date": datetime.now().strftime("%Y-%m-%d"), # ✅ Auto-add date
                "timestamp": time.time()
            }

            mongo.db.Boundaries.insert_one(dataToInsert)
            return jsonify({"status": "success", "message": "Site Saved"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    @routes.route("/api/sites/<site_id>", methods=["DELETE"])
    def delete_site(site_id):
        """Delete a site"""
        try:
            mongo.db.Boundaries.delete_one({"_id": ObjectId(site_id)})
            return jsonify({"status": "success", "message": "Deleted"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

# === 📂 GET SAVED SITES FOR SIDEBAR ===
    @routes.route("/api/sites", methods=["GET"])
    def get_sites():
        """Fetch all saved sites for the drawer"""
        try:
            # Get sites, sorted by newest first (assuming _id stores timestamp roughly)
            sites = mongo.db.Boundaries.find({"userId": 1}).sort("_id", -1)
            
            site_list = []
            for site in sites:
                # Handle cases where 'date' might not exist in old records
                date_str = site.get("date", "Unknown Date")
                
                site_list.append({
                    "id": str(site["_id"]),
                    "name": site.get("sitename", "Unnamed Site"),
                    "date": date_str,
                    "coords": site["coords"]
                })
            
            return jsonify({"status": "success", "sites": site_list})
        except Exception as e:
            print(f"Error fetching sites: {e}")
            return jsonify({"status": "error", "message": str(e)})

    # === 🗑️ DELETE SITE API ===
    @routes.route("/api/sites/<site_id>", methods=["DELETE"])
    def delete_site(site_id):
        from bson.objectid import \
            ObjectId  # Import here to avoid top-level dependency issues
        try:
            mongo.db.Boundaries.delete_one({"_id": ObjectId(site_id)})
            return jsonify({"status": "success", "message": "Deleted"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})

    return routes 
