import os

import matplotlib.pyplot as plt
import pyproj
import rasterio
import requests
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds

# Set PROJ_LIB path
try:
    os.environ['PROJ_LIB'] = pyproj.datadir.get_data_dir()
except Exception:
    pass # Handle cases where pyproj might not be fully loaded

def download_dem(south, west, north, east, typeofdem="COP", output_file='dem_tile.tif'):
    """
    Downloads DEM data.
    Args:
        south (float): Min Latitude
        west (float): Min Longitude
        north (float): Max Latitude
        east (float): Max Longitude
        typeofdem (str): "COP", "SRTMGL1", "USGS", or "OneMeterDem"
        output_file (str): The filename to save the downloaded file to.
    """
    
    dem_key = "f6e4359261eadf297651af4329f48c18" # OpenTopography Key

    # ---------------------------------------------------------
    # CASE 1: USGS 1-Meter DEM (The National Map)
    # ---------------------------------------------------------
    if typeofdem == "OneMeterDem":
        url = "https://tnmaccess.nationalmap.gov/api/v1/products"
        
        # FIX 1: Correct BBox Order -> West, South, East, North
        # API expects: minX, minY, maxX, maxY
        params = {
            "datasets": "Digital Elevation Model (DEM) 1 meter",
            "bbox": f"{west},{south},{east},{north}", 
            "prodFormats": "GeoTIFF"
        }

        print(f"🔍 Searching USGS for 1m DEM with params: {params}")   
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            print(f"Found {data.get('total', 0)} products")

            if data.get('items'):
                # Download the first available product
                download_url = data['items'][0]['downloadURL']
                print(f"⬇️ Downloading 1m DEM from: {download_url}")
                
                file_response = requests.get(download_url, stream=True)
                
                # FIX 2: Save directly to 'output_file' (dem_tile.tif) so crop_dem finds it
                with open(output_file, 'wb') as f:
                    for chunk in file_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"✅ Downloaded 1m DEM to: {output_file}")
                return # STOP here! Do not run the code below.
            else:
                print("❌ No 1-meter DEM products found for this area.")
                # Fallback or exit? For now, we return to avoid overwriting with bad data.
                return 

        except Exception as e:
            print(f"❌ Error downloading OneMeterDem: {e}")
            return

    # ---------------------------------------------------------
    # CASE 2: USGS 10m (via OpenTopography)
    # ---------------------------------------------------------
    elif typeofdem == "USGS":
        url = (f"https://portal.opentopography.org/API/usgsdem?datasetName=USGS10m&south={south}&north={north}&west={west}&east={east}&outputFormat=GTiff&API_Key={dem_key}")

    # ---------------------------------------------------------
    # CASE 3: Global DEM (COP30 / SRTM)
    # ---------------------------------------------------------
    else:
        # Default to COP90 or SRTMGL1
        dem_type = "SRTMGL1" if typeofdem == "SRTMGL1" else "COP30"
        output_format = "GTiff"
        
        url = (
            f"https://portal.opentopography.org/API/globaldem?"
            f"demtype={dem_type}&south={south}&north={north}&west={west}&east={east}"
            f"&outputFormat={output_format}&API_Key={dem_key}"
        )
        
    print(f"Requesting DEM data from: {url}")

    # Send GET request for Cases 2 & 3
    response = requests.get(url, verify=True)

    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"✅ DEM saved successfully to {output_file}")
    else:
        print(f"❌ Failed to download DEM. Status code: {response.status_code}")
        print("Response message:", response.text)

def crop_dem(leaflet_polygon_coords):
    # ... (Keep your existing crop_dem code exactly as is) ...
    # Step 1: Extract all lats and lngs
    lats = [pt["lat"] for pt in leaflet_polygon_coords]
    lons = [pt["lng"] for pt in leaflet_polygon_coords]

    # Step 2: Create bbox in EPSG:4326
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)

    input_tif = "dem_tile.tif"
    output_tif = "cropped.tif"

    # Check if input file exists before trying to open
    if not os.path.exists(input_tif):
        print(f"❌ Error: {input_tif} was not created. Download failed.")
        return None

    try:
        with rasterio.open(input_tif) as src:
            # Step 3: Reproject bbox to raster CRS
            bbox_in_raster_crs = transform_bounds(
                'EPSG:4326',  # Leaflet's coords CRS
                src.crs,      # Raster's CRS
                min_lon, min_lat, max_lon, max_lat
            )

            # Step 4: Convert bbox to raster window
            window = from_bounds(*bbox_in_raster_crs, transform=src.transform)

            # Step 5: Read cropped data
            data = src.read(window=window)

            # Step 6: Update metadata
            out_meta = src.meta.copy()
            out_meta.update({
                "height": window.height,
                "width": window.width,
                "transform": src.window_transform(window)
            })

        # Step 7: Save cropped raster
        with rasterio.open(output_tif, "w", **out_meta) as dest:
            dest.write(data)

        print(f"Cropped raster saved: {output_tif}")
        return output_tif
        
    except Exception as e:
        print(f"❌ Error cropping DEM: {e}")
        return None

def visualization(filePath="cropped.tif"):
    if not filePath or not os.path.exists(filePath):
        print("❌ Visualization skipped: No cropped file found.")
        return

    # Open your cropped .tif file
    with rasterio.open(filePath) as src:
        data = src.read(1)  # read the first band

    # Plot with matplotlib
    plt.figure(figsize=(8, 6))
    plt.imshow(data, cmap="terrain")
    plt.colorbar(label="Elevation (m)")
    plt.title("Cropped DEM Elevation")
    plt.xlabel("Pixel X")
    plt.ylabel("Pixel Y")
    plt.savefig("static/Figure/myplot.png") # Ensure 'static' is lowercase to match folder structure typically
    plt.close() # Close plot to free memory
