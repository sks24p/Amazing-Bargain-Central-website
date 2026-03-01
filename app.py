from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
from config import Config
from models import db, Users, Products
from flask_login import LoginManager, current_user
from logger import log_event
from flask_talisman import Talisman
from dotenv import load_dotenv
import os

# Create app instance
app = Flask(__name__)
app.config.from_object(Config)

# Remove server header
@app.after_request
def security_headers(response):
    response.headers.pop('Server', None)

csp = {
    'default-src': "'self'",
    'script-src': "'self'",
    'style-src': "'self'",
    'img-src': "'self' data:",
    'font-src': "'self'",
    'connect-src': "'self'",
    'frame-ancestors': "'none'"

}

# Secure HTTP to HTTPS
Talisman(app,
    force_https=True,
    content_security_policy=csp,
    strict_transport_security=True,
)

# Import blueprints
from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.seller import seller_bp
from blueprints.products import product_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix = "/admin")
app.register_blueprint(seller_bp, url_prefix = "/seller")
app.register_blueprint(product_bp, url_prefix = "/products")


# Initialise extensions
db.init_app(app)
csrf = CSRFProtect(app)
 
# Flask-login configuration 
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = " Please log in to access this page."
login_manager.login_message_category = "info"

# Create all tables
with app.app_context():
    db.create_all()
    print("Database tables have been created!")

# Load up a user for a query
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Error validation for CSRF tokens
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('auth/csrf_error.html', reason = e.description), 400

# Error handling

@app.errorhandler(403)
def forbidden(error):
    # Log 403 error from user
    log_event('403_application_error', f"User {current_user.email} encountered a 403 error", severity = "error")
    return render_template("errors/403.html"), 403

@app.errorhandler(404)
def page_not_found(error):

    # Don't log or respond to browser automatic requests
    ignore_paths = ['/favicon.ico', '/.well-known/appspecific/com.chrome.devtools.json']
    
    if request.path in ignore_paths:
        return '', 204  # Just return nothing - no log created!

    # Log 404 error from user
    log_event('404_application_error', 
              f"Path: {request.path}, User: {current_user.email if current_user.is_authenticated else 'Anonymous'}", 
              severity = "warning")
    return render_template("errors/404.html"), 404

# Routes
@app.route("/home")
@app.route("/")
def home():
    # Query products to display at home page
    products = Products.query.order_by(Products.created_at.desc()).limit(20).all()
    return render_template("index.html", products = products)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          


if __name__ == '__main__':
    # Debug mode controlled by environment variable
    # Never set debug=True in production
    # Defaults to False for security
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug = debug_mode)