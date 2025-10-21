from main import createApp


app = createApp()

if __name__ == "__main__":

    with app.app_context():
        app.run(debug=True)
