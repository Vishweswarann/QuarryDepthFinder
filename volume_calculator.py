# [file name]: volume_calculator.py
# [file content begin]
import numpy as np
import rasterio
from scipy import integrate

def calculate_excavation_volume(dem_file, reference_elevation=None):
    """
    Calculate excavation volume using multiple methods
    """
    with rasterio.open(dem_file) as src:
        dem_data = src.read(1)
        transform = src.transform
        
    dem_data = dem_data.astype(np.float64)
    dem_data[dem_data == src.nodata] = np.nan
    
    if reference_elevation is None:
        reference_elevation = estimate_reference_elevation(dem_data)
    
    # Calculate depth map
    depth_map = reference_elevation - dem_data
    depth_map[depth_map < 0] = 0
    
    # Only consider areas with significant depth (> 1m)
    quarry_mask = depth_map > 1.0
    quarry_depths = depth_map[quarry_mask]
    
    if len(quarry_depths) == 0:
        return {
            'volume_pixel_method_m3': 0,
            'volume_integral_method_m3': 0,
            'average_depth_m': 0,
            'max_excavation_depth_m': 0,
            'excavation_area_m2': 0,
            'material_categories': {},
            'reference_elevation': reference_elevation,
            'quarry_pixels': 0
        }
    
    # Method 1: Pixel-based volume calculation
    pixel_area = abs(transform[0] * transform[4])
    volume_pixel = np.nansum(quarry_depths) * pixel_area
    
    # Method 2: Integration-based
    volume_integral = calculate_integral_volume(depth_map, transform)
    
    # Calculate material categories based on depth
    material_categories = categorize_excavation_material(depth_map, transform)
    
    return {
        'volume_pixel_method_m3': float(volume_pixel),
        'volume_integral_method_m3': float(volume_integral),
        'average_depth_m': float(np.nanmean(quarry_depths)),
        'max_excavation_depth_m': float(np.nanmax(quarry_depths)),
        'excavation_area_m2': float(np.sum(quarry_mask) * pixel_area),
        'material_categories': material_categories,
        'reference_elevation': float(reference_elevation),
        'quarry_pixels': int(np.sum(quarry_mask))
    }

def estimate_reference_elevation(dem_data):
    """
    Estimate original ground elevation using terrain analysis
    """
    # Use 85th percentile as reference (high points around quarry)
    flat_dem = dem_data[~np.isnan(dem_data)].flatten()
    
    if len(flat_dem) > 0:
        reference = np.percentile(flat_dem, 85)
    else:
        reference = 100  # Default fallback
    
    return reference

def calculate_integral_volume(depth_map, transform):
    """
    Calculate volume using numerical integration
    """
    # Only integrate over quarry areas
    quarry_mask = depth_map > 1.0
    if not np.any(quarry_mask):
        return 0
    
    # Create grid for integration
    x_res = abs(transform[0])
    y_res = abs(transform[4])
    
    x = np.arange(depth_map.shape[1]) * x_res
    y = np.arange(depth_map.shape[0]) * y_res
    
    # Integrate only quarry areas
    quarry_depths = np.where(quarry_mask, depth_map, 0)
    
    try:
        volume = integrate.simps(integrate.simps(quarry_depths, x), y)
        return float(abs(volume))
    except:
        return 0

def categorize_excavation_material(depth_map, transform):
    """
    Categorize excavation into material types based on depth ranges
    """
    pixel_area = abs(transform[0] * transform[4])
    
    categories = {
        'shallow_0_5m': {'depth_range': (1, 5), 'volume_m3': 0, 'area_m2': 0},
        'medium_5_15m': {'depth_range': (5, 15), 'volume_m3': 0, 'area_m2': 0},
        'deep_15_30m': {'depth_range': (15, 30), 'volume_m3': 0, 'area_m2': 0},
        'very_deep_30m_plus': {'depth_range': (30, np.inf), 'volume_m3': 0, 'area_m2': 0}
    }
    
    for category, info in categories.items():
        min_depth, max_depth = info['depth_range']
        mask = (depth_map >= min_depth) & (depth_map < max_depth) & (~np.isnan(depth_map))
        
        category_volume = np.sum(depth_map[mask]) * pixel_area
        category_area = np.sum(mask) * pixel_area
        
        categories[category]['volume_m3'] = float(category_volume)
        categories[category]['area_m2'] = float(category_area)
    
    return categories
# [file content end]