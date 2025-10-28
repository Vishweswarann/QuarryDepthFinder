import os
import sys

import certifi
import matplotlib.pyplot as plt
import rasterio
import requests
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds

# Force SSL certificate path
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['CURL_CA_BUNDLE'] = certifi.where()

os.environ['PROJ_LIB'] = r'C:\Users\vishw\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\site-packages\rasterio\proj_data'


def download_dem(south, west, north, east,typeofdem="COP", output_file='dem.tif'):

    # Define bounding box and parameters
    # south, north = 20, 21
    # west, east = 78, 79
    dem_type = "SRTMGL1"
    output_format = "GTiff"
    output_file = "dem_tile.tif"
    dem_key = "f6e4359261eadf297651af4329f48c18"

    # Construct the API URL
    url = ""

    if typeofdem == "USGS":
        url = (f"https://portal.opentopography.org/API/usgsdem?datasetName=USGS10m&south={south}&north={north}&west={west}&east={east}&outputFormat=GTiff&API_Key={dem_key}")

    elif typeofdem == "OneMeterDem":
        
        # Define API endpoint and parameters
        url = "https://tnmaccess.nationalmap.gov/api/v1/products"
        params = {
            "datasets": "Digital Elevation Model (DEM) 1 meter",
            "bbox": f"{west}, {south}, {east}, {north}",  # Example: Colorado area
            "prodFormats": "GeoTIFF"
        }

        # Make API request
        response = requests.get(url, params=params)
        data = response.json()


        # Print number of results
        print(f"Found {data['total']} products")

        # Download the first GeoTIFF file
        if data['items']:
            download_url = data['items'][0]['downloadURL']
            filename = "dem_tile.tif"

            print(f"Downloading {filename}...")
            file_response = requests.get(download_url, stream=True)
            file_size = int(file_response.headers.get('Content-Length', 0))
            chunk_size = 8192
            downloaded = 0

            with open(filename, 'wb') as f:
                for chunk in file_response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        done = int(50 * downloaded / file_size) if file_size else 0
                        sys.stdout.write(f"\r[{'#' * done}{'.' * (50 - done)}] {downloaded/(1024 * 1024):.2f}/{file_size/(1024 * 1024):.2f} MB")
                        sys.stdout.flush()
            print("\nDownload complete!")

            print(f"Downloaded: {filename}")

        return


    else:
        url = (
                f"https://portal.opentopography.org/API/globaldem?"
        f"demtype={dem_type}&south={south}&north={north}&west={west}&east={east}"
        f"&outputFormat={output_format}&API_Key={dem_key}"
        )
        
    # NOTE: api key for opentopography f6e4359261eadf297651af4329f48c18
    print(f"Requesting DEM data from: {url}")

    # Send GET request
    response = requests.get(url, verify=True)


    # Check if request was successful
    if response.status_code == 200:
        # Write content to file
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"DEM saved successfully to {output_file}")
    else:
        print(f"Failed to download DEM. Status code: {response.status_code}")
        print("Response message:", response.text)



def crop_dem(leaflet_polygon_coords):
    # Example: coords from Leaflet polygon (EPSG:4326)
    # This is what you'd get from L.polygon(...).getLatLngs()[0]

    # Step 1: Extract all lats and lngs
    lats = [pt["lat"] for pt in leaflet_polygon_coords]
    lons = [pt["lng"] for pt in leaflet_polygon_coords]

    # Step 2: Create bbox in EPSG:4326
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)

    input_tif = "dem_tile.tif"
    output_tif = "cropped.tif"

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



def visualization(filePath = "cropped.tif"):

    min_elevation = 0
    max_elevation = 0
    depth = 0
    # Open your cropped .tif file
    with rasterio.open("cropped.tif") as src:
        data = src.read(1, masked=True)  # read the first band
        profile = src.profile
        min_elevation = data.min()
        max_elevation = data.max()
        depth = max_elevation - min_elevation
        

    # Plot with matplotlib
    plt.figure(figsize=(8, 6))
    plt.imshow(data, cmap="terrain")  # 'terrain' colormap for elevation
    plt.colorbar(label="Elevation (m)")  # colorbar shows depth/elevation
    plt.title("Cropped DEM Elevation")
    plt.xlabel("Pixel X")
    plt.ylabel("Pixel Y")
    plt.savefig("Static/Figure/myplot.png")
    # plt.show()
    

    return float(min_elevation), float(max_elevation), float(depth)

    
