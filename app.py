from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Create application instance
app = Flask(__name__)
app.config.from_object(Config)

# Create the SQLAlchemy database instance
db = SQLAlchemy(app)
 
# Create all tables
with app.app_context():
    db.create_all()
    print("Database tables created!")

# Routes
@app.route("/")
def home():
    return "Home page"

if __name__ == '__main__':
    app.run(debug = True)