import requests


def download_dem(south, west, north, east, output_file='dem.tif'):

    # Define bounding box and parameters
    # south, north = 20, 21
    # west, east = 78, 79
    dem_type = "SRTMGL1"
    output_format = "GTiff"
    output_file = "dem_tile.tif"
    dem_key = "f6e4359261eadf297651af4329f48c18"

    # Construct the API URL

    url = (
            f"https://portal.opentopography.org/API/globaldem?"
    f"demtype={dem_type}&south={south}&north={north}&west={west}&east={east}"
    f"&outputFormat={output_format}&API_Key={dem_key}"
    )
    # NOTE: api key for opentopography f6e4359261eadf297651af4329f48c18
    print(f"Requesting DEM data from: {url}")

    # Send GET request
    response = requests.get(url)


    # Check if request was successful
    if response.status_code == 200:
        # Write content to file
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"DEM saved successfully to {output_file}")
    else:
        print(f"Failed to download DEM. Status code: {response.status_code}")
        print("Response message:", response.text)

