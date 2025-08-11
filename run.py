from main import createApp
from main import returnDb


app = createApp()

if __name__ == "__main__":

    with app.app_context():
        app.run(debug=True)
