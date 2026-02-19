# [file name]: three_visualization.py
# [file content begin]
import json
import os
from datetime import datetime

import numpy as np
import rasterio


def generate_3d_terrain_data(dem_file="cropped.tif"):
    """
    Generate fresh 3D terrain data for Three.js visualization
    """
    try:
        # Always use the latest cropped file
        if not os.path.exists(dem_file):
            print(f"DEM file not found: {dem_file}")
            return generate_sample_3d_data()
        
        with rasterio.open(dem_file) as src:
            dem_data = src.read(1)
            transform = src.transform
            bounds = src.bounds
            
        print(f"🔄 Generating 3D data from: {dem_file}")
        print(f"📊 DEM shape: {dem_data.shape}")
        
        # Process DEM data
        dem_data = dem_data.astype(np.float64)
        dem_data[dem_data == src.nodata] = np.nan
        
        # Fill NaN values
        dem_data = fill_nan_values(dem_data)
        
        # Downsample if too large for better performance
        if dem_data.shape[0] > 150 or dem_data.shape[1] > 150:
            dem_data = dem_data[::2, ::2]
            print(f"📏 Downsampled to: {dem_data.shape}")
        
        # Calculate statistics
        min_elev = float(np.nanmin(dem_data))
        max_elev = float(np.nanmax(dem_data))
        mean_elev = float(np.nanmean(dem_data))
        
        print(f"📈 Elevation range: {min_elev:.1f}m to {max_elev:.1f}m")
        print(f"📊 Mean elevation: {mean_elev:.1f}m")
        
        # Convert to list for JSON
        elevation_list = dem_data.tolist()
        
        # Create terrain data
        terrain_data = {
            "elevation": elevation_list,
            "minElevation": min_elev,
            "maxElevation": max_elev,
            "meanElevation": mean_elev,
            "width": int(dem_data.shape[1]),
            "height": int(dem_data.shape[0]),
            "bounds": {
                "left": float(bounds.left),
                "right": float(bounds.right),
                "bottom": float(bounds.bottom),
                "top": float(bounds.top)
            },
            "scale": 3,
            "timestamp": datetime.now().isoformat(),
            "dataSource": dem_file
        }
        
        # Save with unique filename
        output_dir = "static/3d"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_json = os.path.join(output_dir, f"terrain_{timestamp}.json")
        
        os.makedirs(output_dir, exist_ok=True)
        with open(output_json, 'w') as f:
            json.dump(terrain_data, f, indent=2)
        
        print(f"✅ 3D terrain data saved: {output_json}")
        print(f"📐 Terrain size: {terrain_data['width']} x {terrain_data['height']}")
        
        return output_json
        
    except Exception as e:
        print(f"❌ Error generating 3D data: {e}")
        return generate_sample_3d_data()

def get_latest_3d_data():
    """Get the most recent 3D terrain data file"""
    output_dir = "static/3d"
    if not os.path.exists(output_dir):
        return generate_3d_terrain_data()
    
    # Find all terrain JSON files
    terrain_files = [f for f in os.listdir(output_dir) if f.startswith('terrain_') and f.endswith('.json')]
    
    if not terrain_files:
        return generate_3d_terrain_data()
    
    # Get the most recent file
    latest_file = max(terrain_files)
    return os.path.join(output_dir, latest_file)

def fill_nan_values(data):
    """Fill NaN values using interpolation"""
    mask = np.isnan(data)
    if not np.any(mask):
        return data
    
    try:
        from scipy import ndimage
        indices = ndimage.distance_transform_edt(mask, return_distances=False, return_indices=True)
        data[mask] = data[tuple(indices[:, mask])]
    except:
        # Simple fill with mean
        data[mask] = np.nanmean(data)
    
    return data

def generate_sample_3d_data():
    """Generate realistic sample quarry terrain"""
    print("🔄 Generating sample quarry terrain...")
    
    # Create a more realistic quarry shape
    x = np.linspace(-3, 3, 100)
    y = np.linspace(-3, 3, 100)
    X, Y = np.meshgrid(x, y)
    
    # Create quarry-like depression
    R = np.sqrt(X**2 + Y**2)
    quarry_depth = np.exp(-R**2) * 50
    terrain_variation = np.sin(X*2) * np.cos(Y*2) * 10
    
    Z = 100 - quarry_depth + terrain_variation
    
    terrain_data = {
        "elevation": Z.tolist(),
        "minElevation": float(np.min(Z)),
        "maxElevation": float(np.max(Z)),
        "meanElevation": float(np.mean(Z)),
        "width": 100,
        "height": 100,
        "bounds": {
            "left": -3,
            "right": 3,
            "bottom": -3,
            "top": 3
        },
        "scale": 3,
        "timestamp": datetime.now().isoformat(),
        "dataSource": "sample_quarry"
    }
    
    output_dir = "static/3d"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_json = os.path.join(output_dir, f"sample_terrain_{timestamp}.json")
    
    os.makedirs(output_dir, exist_ok=True)
    with open(output_json, 'w') as f:
        json.dump(terrain_data, f, indent=2)
    
    print(f"✅ Sample 3D data saved: {output_json}")
    return output_json
# [file content end]
