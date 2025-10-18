from flask import Flask
from routes import callRoutes




def createApp():

    app = Flask(__name__)


    app.secret_key = 'vanakam'



    routes = callRoutes(app)
    app.register_blueprint(routes)
    

    return app

