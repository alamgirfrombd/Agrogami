from flask import Flask, session
from app.routes.auth_routes import auth_bp

app = Flask(__name__)
app.secret_key = "your_very_secret_key"  # change this to env var in production

app.register_blueprint(auth_bp)

@app.route('/')
def index():
    return "Welcome! Go to /login to access the system."

if __name__ == "__main__":
    app.run(debug=True)
