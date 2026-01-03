from flask_login import current_user, login_required
from flask import abort, Blueprint, flash, render_template, url_for, redirect


# Creating Blueprint
admin_bp = Blueprint('admin', __name__)

# Check if user's role is a seller or admin
@admin_bp.before_request
@login_required
def require_admin():
    """Only Admins can access admin routes"""
    if current_user.role != 'admin':
        flash("You need to be an admin to access this page.", category = 'error')
        abort(403)

# Routes

# Dashboard page
@admin_bp.route("/dashboard", methods = ["GET"])
@login_required
def dashboard():
    """Admin dashboard - manage users and site """
    return render_template("admin/dashboard.html")

