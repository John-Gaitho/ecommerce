from app import create_app
app = create_app()

@app.route("/")
def home():
    return "Welcome to Branded in Grace API!"

if __name__ == "__main__":
    app.run()