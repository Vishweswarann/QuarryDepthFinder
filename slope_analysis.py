import numpy as np
import rasterio
import matplotlib.pyplot as plt

def calculate_slope_simple(dem_file):
    """
    Simplified slope calculation for route integration
    """
    try:
        with rasterio.open(dem_file) as src:
            dem_data = src.read(1)
            transform = src.transform
            
        dem_data = dem_data.astype(np.float32)
        dem_data[dem_data == src.nodata] = np.nan
        
        # Calculate slope
        x_resolution = transform[0]
        y_resolution = abs(transform[4])
        
        grad_x, grad_y = np.gradient(dem_data, x_resolution, y_resolution)
        slope_radians = np.arctan(np.sqrt(grad_x**2 + grad_y**2))
        slope_degrees = np.degrees(slope_radians)
        
        # Basic statistics
        slope_stats = {
            'average': float(np.nanmean(slope_degrees)),
            'max': float(np.nanmax(slope_degrees)),
            'min': float(np.nanmin(slope_degrees)),
            'std': float(np.nanstd(slope_degrees))
        }
        
        return slope_degrees, slope_stats
        
    except Exception as e:
        print(f"Error in calculate_slope_simple: {e}")
        raise e

def generate_slope_map(slope_data, output_path):
    """
    Generate slope visualization map
    """
    plt.figure(figsize=(10, 8))
    
    # Plot slope map
    im = plt.imshow(slope_data, cmap='YlOrRd')
    plt.colorbar(im, label='Slope (degrees)')
    plt.title('Slope Analysis Map')
    
    # Save the figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path

def get_slope_profile(slope_data, start_point, end_point):
    """
    Extract slope profile along a line (simplified)
    """
    height, width = slope_data.shape
    
    # Convert normalized points to array indices
    x1, y1 = int(start_point[0] * width), int(start_point[1] * height)
    x2, y2 = int(end_point[0] * width), int(end_point[1] * height)
    
    # Extract profile line
    num_points = 100
    x_values = np.linspace(x1, x2, num_points).astype(int)
    y_values = np.linspace(y1, y2, num_points).astype(int)
    
    # Ensure indices are within bounds
    x_values = np.clip(x_values, 0, width-1)
    y_values = np.clip(y_values, 0, height-1)
    
    # Extract slope values
    profile_slopes = slope_data[y_values, x_values]
    distances = np.linspace(0, 1, num_points)
    
    return {
        'distance': distances.tolist(),
        'slope': profile_slopes.tolist(),
        'start_point': start_point,
        'end_point': end_point
    }