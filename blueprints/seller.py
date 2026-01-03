from flask_login import current_user, login_required
from flask import abort, Blueprint, flash, render_template, url_for, redirect


# Creating Blueprint
seller_bp = Blueprint('seller', __name__)

# Check if user's role is a seller or admin
@seller_bp.before_request
@login_required
def require_seller():
    """Only sellers (and admins) can access seller routes"""
    if current_user.role not in ['seller','admin']:
        flash("You need to be a seller to access this page.", category = 'error')
        abort(403)

# Routes

# Dashboard page
@seller_bp.route("/dashboard", methods = ["GET"])
@login_required
def dashboard():
    """Seller dashboard - manage products """
    return render_template("seller/dashboard.html")
