from flask import Flask
from flask_pymongo import PyMongo

from routes import callRoutes


def createApp():

    app = Flask(__name__)

    app.config["MONGO_URI"] = "mongodb://localhost:27017/QuarryDepthFinder"

    mongo = PyMongo(app)

    app.secret_key = "vanakam"

    routes = callRoutes(app, mongo)
    app.register_blueprint(routes)

    return app
