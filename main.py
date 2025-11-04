# [file name]: main.py
# [file content begin]
from flask import Flask
from flask_pymongo import PyMongo

def createApp():
    app = Flask(__name__)
    app.config["MONGO_URI"] = "mongodb://localhost:27017/QuarryDepthFinder"
    mongo = PyMongo(app)
    app.secret_key = "vanakam"

    # ✅ FIX: Import and register routes properly (no circular imports)
    try:
        from routes import callRoutes
        routes_bp = callRoutes(app, mongo)
        if routes_bp:
            app.register_blueprint(routes_bp)
            print("✅ Main routes enabled!")
        else:
            print("❌ Main routes failed to initialize")
    except Exception as e:
        print(f"❌ Main routes error: {e}")
    
    # ✅ FIX: Register advanced routes
    try:
        from advanced_routes import create_advanced_routes
        advanced_bp = create_advanced_routes(app, mongo)
        if advanced_bp:
            app.register_blueprint(advanced_bp)
            print("✅ Advanced features enabled!")
        else:
            print("❌ Advanced routes failed to initialize")
    except Exception as e:
        print(f"❌ Advanced routes error: {e}")
        
    # ✅ FIX: Register test routes  
    try:
        from test_depth import create_test_routes
        test_bp = create_test_routes(app)
        if test_bp:
            app.register_blueprint(test_bp)
            print("✅ Test routes enabled!")
        else:
            print("❌ Test routes failed to initialize")
    except Exception as e:
        print(f"❌ Test routes error: {e}")

    return app
# [file content end]