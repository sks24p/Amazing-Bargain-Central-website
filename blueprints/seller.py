from typing import Type
from flask_login import current_user, login_required
from flask import abort, Blueprint, request, flash, render_template, url_for, redirect
from models import Products, Users, db

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
def dashboard():
    """Seller dashboard - manage products """
    return render_template("seller/dashboard.html")

@seller_bp.route("/add_product", methods = ['POST', 'GET'])
def add_product():
    if request.method == "POST":
        # Get form data
        name = request.form.get('name')
        description = request.form.get("description")
        price_str = request.form.get("price")
        image_url = request.form.get("image_url")

        # Validate data
        if not all([name, description, price_str, image_url]):
            # If any field is left empty, return true
            flash("All fields are required.", category = "error")
        else:
            try:
                price = float(price_str)
            except (ValueError, TypeError):
                flash("Invalid price value.", category = "error")
                return render_template("seller/add_product.html")

            # Check if product exists
            product_exists = Products.query.filter_by(name = name).first()
            if product_exists:
                flash("This product already exists.", category = "error")
            elif price <= 0.00:
                flash("Price can't be negative. Please input a positive value.", category = "error")
            elif any(character in image_url for character in ['<', '>', '"', "'"]):
                flash("Image URL contains invalid characters", category = "error")
            else:
                # Create Products object
                new_product = Products(
                    name = name,
                    description = description,
                    price = price,
                    seller_id = current_user.id,
                    image_url = image_url,
                )
                db.session.add(new_product)
                db.session.commit()
                flash("You have successfully created a product!", category = "success")
                return redirect(url_for("seller.dashboard"))
    return render_template("seller/add_product.html")