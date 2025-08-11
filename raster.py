import rasterio
import matplotlib.pyplot as plt

# Open a raster file
with rasterio.open('dem_tile.tif') as src:
    print(src.profile)  # metadata info
    dem_array = src.read(1)  # read first band as numpy array
    print(dem_array.shape)   # shape of raster (rows, cols)


    # plt.imshow(dem_array, cmap='terrain')
    # plt.colorbar(label='Elevation (m)')
    # plt.title('DEM Raster')
    # plt.show()
