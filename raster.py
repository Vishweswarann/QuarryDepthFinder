import matplotlib.pyplot as plt
import rasterio
from rasterio.plot import show

img = rasterio.open("./dem_tile.tif")
show(img)


print(img.meta)
