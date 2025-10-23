import os
from datetime import datetime

import matplotlib.pyplot as plt
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)

from extraFunctions import crop_dem, download_dem, visualization


def callRoutes(app, mongo):

    routes = Blueprint("routes", __name__, template_folder="templates")

    @routes.route("/")
    def home():
        boundaries = mongo.db.Boundaries.find({"userId" : 1})
        coords = []
        sitename = []

        for i in boundaries:
            coords.append(i["coords"])
            sitename.append(i["sitename"])

        return render_template("index.html", coords = coords, sitename = sitename)

    @routes.route("/usgsdem")
    def usgsdem():
        return render_template("usgsdem.html")

    @routes.route("/OneMeterDem")
    def OneMeterDem():
        return render_template("1mdem.html")

    @routes.route("/test")
    def test():
        return render_template("test2.html")

    @routes.route("/save", methods=["POST"])
    def save():

        data = request.get_json()

        coords = data.get("coords")
        print(coords)
        sitename = data.get("sitename")

        dataToInsert = {"userId" : 1,
                        "sitename" : sitename,
                        "coords" : coords}

        mongo.db.Boundaries.insert_one(dataToInsert)

        return jsonify({"Message": "Success"})

    @routes.route("/api/get_dem", methods=["POST"])
    def get_dem():
        data = request.get_json()

        dem = data.get("dem")
        coords = data.get("coords")
        print(coords)
        bbox = data.get("bbox")

        coords_list = [[p["lat"], p["lng"]] for p in coords]

        minLat = float(bbox.get("minLat"))
        maxLat = float(bbox.get("maxLat"))
        minLng = float(bbox.get("minLng"))
        maxLng = float(bbox.get("maxLng"))

        print(
            f"Received bounding box: South={minLat}, West={
              minLng}, North={maxLat}, East={maxLng}"
        )

        # TODO: Use bounding box to call DEM API and process DEM

        # Downloads the dem from opentopography and stores it in a fiile
        download_dem(south=minLat, west=minLng, north=maxLat, east=maxLng, typeofdem=dem)

        # Takes the tif file and crops it into the user expected shape
        # mask_raster_with_leaflet("dem_tile.tif", coords_list, "masked.tif", show_plot=True)

        CroppedFile = crop_dem(coords)

        visualization(CroppedFile)

        # Dummy response
        return jsonify({"depth": 42.0, "min_elevation": 100, "max_elevation": 142})

    return routes
