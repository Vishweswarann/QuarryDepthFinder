from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import os
import matplotlib.pyplot as plt
from extraFunctions import download_dem, crop_dem, visualization


def callRoutes(app):

    routes = Blueprint("routes", __name__, template_folder="templates")

    @routes.route('/')
    def home():
        return render_template("index.html")

    @routes.route('/usgsdem')
    def usgsdem():
        return render_template("usgsdem.html")


    @routes.route('/test')
    def test():
        return render_template("test2.html")

    @routes.route('/api/get_dem', methods=['POST'])
    def get_dem():
        data = request.get_json()

        coords = data.get("coords")
        bbox = data.get("bbox")

        coords_list = [[p["lat"], p["lng"]] for p in coords]

        minLat = float(bbox.get('minLat'))
        maxLat = float(bbox.get('maxLat'))
        minLng = float(bbox.get('minLng'))
        maxLng = float(bbox.get('maxLng'))

        print(f"Received bounding box: South={minLat}, West={
              minLng}, North={maxLat}, East={maxLng}")

        # TODO: Use bounding box to call DEM API and process DEM

        # Downloads the dem from opentopography and stores it in a fiile
        download_dem(south=minLat, west=minLng, north=maxLat, east=maxLng)

        # Takes the tif file and crops it into the user expected shape
        # mask_raster_with_leaflet("dem_tile.tif", coords_list, "masked.tif", show_plot=True)

        CroppedFile = crop_dem(coords)


        visualization(CroppedFile)


        # Dummy response
        return jsonify({
            "depth": 42.0,
            "min_elevation": 100,
            "max_elevation": 142
        })


    @routes.route('/api/get_usgsdem', methods=['POST'])
    def get_usgsdem():
        data = request.get_json()

        coords = data.get("coords")
        bbox = data.get("bbox")

        coords_list = [[p["lat"], p["lng"]] for p in coords]

        minLat = float(bbox.get('minLat'))
        maxLat = float(bbox.get('maxLat'))
        minLng = float(bbox.get('minLng'))
        maxLng = float(bbox.get('maxLng'))

        print(f"Received bounding box: South={minLat}, West={
              minLng}, North={maxLat}, East={maxLng}")

        # TODO: Use bounding box to call DEM API and process DEM

        # Downloads the dem from opentopography and stores it in a fiile
        download_dem(south=minLat, west=minLng, north=maxLat, east=maxLng, typeofdem="USGS")

        # Takes the tif file and crops it into the user expected shape
        # mask_raster_with_leaflet("dem_tile.tif", coords_list, "masked.tif", show_plot=True)

        CroppedFile = crop_dem(coords)


        visualization(CroppedFile)


        # Dummy response
        return jsonify({
            "depth": 42.0,
            "min_elevation": 100,
            "max_elevation": 142
        })

    return routes
