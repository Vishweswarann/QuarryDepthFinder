import os

import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.warp import transform
from scipy import ndimage


# === IMPROVED GRADIENT DESCENT OPTIMIZATION ===
def gradient_descent_surface_optimization(dem_data, learning_rate=0.1, iterations=1000):
    """
    Use gradient descent to find optimal surface elevation that minimizes
    the error between estimated and actual terrain
    """
    try:
        # Get edge pixels for training data (wider edge for better sampling)
        edge_width = 10  # Increased from 5
        top_edge = dem_data[:edge_width, :]
        bottom_edge = dem_data[-edge_width:, :] 
        left_edge = dem_data[:, :edge_width]
        right_edge = dem_data[:, -edge_width:]
        
        edge_elevations = np.concatenate([
            top_edge.flatten(),
            bottom_edge.flatten(),
            left_edge.flatten(), 
            right_edge.flatten()
        ])
        
        # Remove NaN values and outliers
        edge_elevations = edge_elevations[~np.isnan(edge_elevations)]
        
        if len(edge_elevations) == 0:
            print("⚠️ No edge data, using fallback")
            return np.nanmax(dem_data)
        
        # Remove extreme outliers (beyond 3 standard deviations)
        mean_val = np.mean(edge_elevations)
        std_val = np.std(edge_elevations)
        filtered_elevations = edge_elevations[
            (edge_elevations > mean_val - 3*std_val) & 
            (edge_elevations < mean_val + 3*std_val)
        ]
        
        if len(filtered_elevations) == 0:
            filtered_elevations = edge_elevations  # Fallback to original
        
        print(f"📊 Edge data: {len(filtered_elevations)} points, range: {np.min(filtered_elevations):.1f}m to {np.max(filtered_elevations):.1f}m")
        
        # Better initial guess - 85th percentile (higher but realistic)
        surface_estimate = np.percentile(filtered_elevations, 85)
        
        print(f"🔍 Starting gradient descent from: {surface_estimate:.2f}m")
        
        # Gradient descent to minimize MSE with edge elevations
        for i in range(iterations):
            # Calculate gradient (derivative of MSE)
            error = surface_estimate - filtered_elevations
            gradient = 2 * np.mean(error)
            
            # Update surface estimate
            surface_estimate = surface_estimate - learning_rate * gradient
            
            # Early convergence check with tolerance
            if abs(gradient) < 0.0001:
                print(f"✅ Converged after {i} iterations")
                break
            
            # Print progress every 100 iterations
            if i % 100 == 0:
                print(f"   Iteration {i}: surface={surface_estimate:.2f}m, gradient={gradient:.6f}")
        
        print(f"🎯 Gradient Descent Surface: {surface_estimate:.2f}m (after {i+1} iterations)")
        return surface_estimate
        
    except Exception as e:
        print(f"❌ Gradient descent failed: {e}")
        import traceback
        traceback.print_exc()
        return np.nanpercentile(dem_data[~np.isnan(dem_data)], 85)  # Fallback



def calculate_quarry_depth(dem_file, reference_point=None):
    """
    Calculate quarry depth using an optional manual reference point.
    reference_point should be a dict: {'lat': 20.5, 'lng': 78.9}
    """
    try:
        print(f"🔍 Analyzing DEM file: {dem_file}")
        
        if not os.path.exists(dem_file):
            print(f"❌ DEM file not found: {dem_file}")
            return create_fallback_data()
        
        with rasterio.open(dem_file) as src:
            dem_data = src.read(1)
            transform_affine = src.transform
            crs = src.crs
            
            # Convert NoData values to NaN
            dem_data = dem_data.astype(float)
            dem_data[dem_data == src.nodata] = np.nan
            
            # --- 📍 NEW LOGIC: Manual Reference Point ---
            surface_elevation = None
            
            if reference_point:
                print(f"📍 User provided reference point: {reference_point}")
                try:
                    # 1. Convert Lat/Lon (EPSG:4326) to the DEM's Coordinate System
                    # Note: transform() takes lists of coordinates
                    xs, ys = transform('EPSG:4326', crs, [reference_point['lng']], [reference_point['lat']])
                    proj_x, proj_y = xs[0], ys[0]
                    
                    # 2. Find which pixel corresponds to that coordinate
                    row, col = src.index(proj_x, proj_y)
                    print(f"   Mapped to Pixel: Row {row}, Col {col}")
                    
                    # 3. Read the elevation at that pixel
                    # Check if the point is actually inside the cropped image
                    if 0 <= row < dem_data.shape[0] and 0 <= col < dem_data.shape[1]:
                        manual_elevation = dem_data[row, col]
                        
                        # Validate the value (not NaN)
                        if not np.isnan(manual_elevation):
                            surface_elevation = manual_elevation
                            print(f"✅ MANUAL REFERENCE SET: {surface_elevation} meters")
                        else:
                            print("⚠️ Selected point is NaN (No Data). Using auto-estimation.")
                    else:
                        print("⚠️ Reference point is OUTSIDE the cropped quarry area. Using auto-estimation.")
                        
                except Exception as e:
                    print(f"❌ Error processing reference point: {e}")
            
            # --- Fallback to Auto-Estimation if no valid manual point ---
            if surface_elevation is None:
                print("⚙️ Using automatic surface estimation...")
                surface_elevation = estimate_original_surface(dem_data)

            # --- STANDARD CALCULATION (Same as before) ---
            quarry_bottom = np.nanmin(dem_data)
            
            # Calculate depth map (Surface - Current)
            depth_map = surface_elevation - dem_data
            depth_map[depth_map < 0] = 0  # Ignore things higher than reference
            depth_map[np.isnan(dem_data)] = np.nan
            
            # Calculate Area & Volume
            pixel_width = abs(transform_affine[0])
            pixel_height = abs(transform_affine[4])
            pixel_area = pixel_width * pixel_height
            
            valid_depth_mask = (depth_map > 0) & (~np.isnan(depth_map))
            excavated_pixels = np.sum(valid_depth_mask)
            total_area_m2 = excavated_pixels * pixel_area
            volume_m3 = np.nansum(depth_map) * pixel_area
            
            # Statistics
            if excavated_pixels > 0:
                max_depth = np.nanmax(depth_map)
                mean_depth = np.nanmean(depth_map[valid_depth_mask])
                median_depth = np.nanmedian(depth_map[valid_depth_mask])
            else:
                max_depth = 0
                mean_depth = 0
                median_depth = 0
            
            stats = {
                'max_depth': float(max_depth) if not np.isnan(max_depth) else 0.0,
                'mean_depth': float(mean_depth) if not np.isnan(mean_depth) else 0.0,
                'median_depth': float(median_depth) if not np.isnan(median_depth) else 0.0,
                'quarry_bottom_elevation': float(quarry_bottom) if not np.isnan(quarry_bottom) else 0.0,
                'original_surface_elevation': float(surface_elevation) if not np.isnan(surface_elevation) else 0.0,
                'volume_m3': float(volume_m3) if not np.isnan(volume_m3) else 0.0,
                'total_area_m2': float(total_area_m2) if not np.isnan(total_area_m2) else 0.0,
                'excavated_pixels': int(excavated_pixels),
                'pixel_area_m2': float(pixel_area) if not np.isnan(pixel_area) else 0.0,
                'surface_original_method': float(estimate_original_surface(dem_data)), # For comparison
                'surface_gradient_descent': float(surface_elevation) # Using manual as the "optimized" value
            }
            
            return depth_map, stats, transform_affine, crs
            
    except Exception as e:
        print(f"❌ Error in calculate_quarry_depth: {e}")
        import traceback
        traceback.print_exc()
        return create_fallback_data()

def estimate_original_surface(dem_data):
    """
    Estimate original ground surface before excavation
    """
    try:
        # Method 1: Use the highest points around the edges as reference
        edge_width = 5  # pixels from edge
        
        # Get edge elevations
        top_edge = dem_data[:edge_width, :]
        bottom_edge = dem_data[-edge_width:, :]
        left_edge = dem_data[:, :edge_width]
        right_edge = dem_data[:, -edge_width:]
        
        edge_elevations = np.concatenate([
            top_edge.flatten(),
            bottom_edge.flatten(), 
            left_edge.flatten(),
            right_edge.flatten()
        ])
        
        # Remove NaN values
        edge_elevations = edge_elevations[~np.isnan(edge_elevations)]
        
        if len(edge_elevations) > 0:
            # Use 90th percentile of edge elevations as surface estimate
            surface = np.percentile(edge_elevations, 90)
        else:
            # Fallback: use max elevation in entire dataset
            surface = np.nanmax(dem_data)
        
        # Ensure we have a valid surface value
        if np.isnan(surface):
            surface = np.nanmax(dem_data)
            if np.isnan(surface):
                surface = 100.0  # Final fallback
        
        print(f"🏔️ Estimated original surface: {surface:.1f}m")
        return surface
        
    except Exception as e:
        print(f"❌ Error estimating surface: {e}")
        return 100.0  # Safe fallback


# In QuarryDepthFinder3/depth_analysis.py

def generate_depth_visualization(depth_data, output_path):
    """
    Generate a professional-grade visualization with DISCRETE colors and LABELS.
    """
    try:
        # Increase figure size for better resolution
        fig = plt.figure(figsize=(16, 10))
        
        # --- PLOT 1: The Main Depth Map (Top Left) ---
        ax1 = plt.subplot(2, 2, 1)
        
        # Mask out zero values (unexcavated ground)
        depth_display = depth_data.copy()
        depth_display[depth_data <= 0] = np.nan
        
        # 1. Define Discrete Levels (The "Steps")
        max_depth = np.nanmax(depth_data)
        if np.isnan(max_depth) or max_depth == 0:
            max_depth = 10 # Fallback
            
        # Create ~15 distinct levels (e.g., 0, 5, 10, 15...)
        num_levels = 15
        levels = np.linspace(0, max_depth, num_levels + 1)
        
        # 2. Create a Discrete Colormap (No more smooth blending)
        # 'Spectral_r' is good, but we discretize it into N chunks
        cmap = plt.get_cmap('Spectral_r', num_levels)
        norm = matplotlib.colors.BoundaryNorm(levels, ncolors=cmap.N, clip=True)
        
        # 3. Plot with 'norm' to enforce discrete colors
        img1 = ax1.imshow(depth_display, cmap=cmap, norm=norm, aspect='equal')
        
        # 4. Add Contour Lines AND Labels (The Numbers)
        if max_depth > 0:
            # Draw black lines at the boundaries
            contours = ax1.contour(depth_display, levels=levels, colors='black', linewidths=0.5, alpha=0.6)
            # Add NUMBERS to the lines!
            ax1.clabel(contours, inline=True, fontsize=8, fmt='%1.0fm', colors='black')
            
        # Add colorbar with ticks at every level
        cbar = plt.colorbar(img1, ax=ax1, label='Depth (m)', ticks=levels, format='%.0fm')
        cbar.ax.tick_params(labelsize=8)
        
        ax1.set_title(f'Discrete Depth Map (Max: {max_depth:.1f}m)', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Distance (pixels)')
        ax1.set_ylabel('Distance (pixels)')
        
        # --- PLOT 2: Raw Elevation Data (Top Right) ---
        ax2 = plt.subplot(2, 2, 2)
        
        # Hillshade for 3D context
        ls = matplotlib.colors.LightSource(azdeg=315, altdeg=45)
        dem_safe = depth_data.copy()
        dem_safe[np.isnan(dem_safe)] = 0
        rgb = ls.shade(dem_safe, cmap=plt.cm.terrain, vert_exag=0.1, blend_mode='soft')
        
        ax2.imshow(rgb, aspect='equal')
        ax2.set_title('3D Terrain Context', fontsize=12)
        ax2.axis('off')
        
        # --- PLOT 3: Depth Histogram (Bottom Left) ---
        ax3 = plt.subplot(2, 2, 3)
        depths = depth_data[(depth_data > 0) & (~np.isnan(depth_data))]
        if len(depths) > 0:
            # Match histogram colors to the map
            n, bins, patches = ax3.hist(depths, bins=levels, edgecolor='black', alpha=0.8)
            # Color the bars to match the depth map
            for i, patch in enumerate(patches):
                # Map the bin center to our colormap
                color_val = (bins[i] + bins[i+1])/2
                patch.set_facecolor(cmap(norm(color_val)))
                
            ax3.set_xlabel('Depth Range (m)')
            ax3.set_ylabel('Pixel Count')
            ax3.set_title('Depth Frequency Distribution')
        else:
            ax3.text(0.5, 0.5, 'No Excavation Detected', ha='center', va='center')

        # --- PLOT 4: Stats Summary (Bottom Right) ---
        ax4 = plt.subplot(2, 2, 4)
        ax4.axis('off')
        
        valid_pixels = np.sum(~np.isnan(depth_data))
        excavated_pixels = np.sum((depth_data > 0) & (~np.isnan(depth_data)))
        
        summary_text = (
            f"QUARRY ANALYSIS REPORT\n"
            f"----------------------\n"
            f"Max Depth: {max_depth:.2f} m\n"
            f"Avg Depth: {np.nanmean(depths):.2f} m\n"
            f"\n"
            f"Total Area: {valid_pixels} px\n"
            f"Excavated:  {excavated_pixels} px\n"
            f"\n"
            f"Visualization Type:\n"
            f"Discrete Steps ({num_levels} levels)\n"
        )
        ax4.text(0.1, 0.5, summary_text, fontsize=12, family='monospace', va='center')

        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"📊 Visualization saved: {output_path}")
        
    except Exception as e:
        print(f"❌ Error generating visualization: {e}")
        import traceback
        traceback.print_exc()
