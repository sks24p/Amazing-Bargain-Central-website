from flask_login import current_user, login_required
from flask import abort, Blueprint, flash, render_template, request, url_for, redirect
from models import Products

# Creating Blueprint
product_bp = Blueprint('products', __name__)


# Routes
@product_bp.route("/product/<int:product_id>")
def product_detail(product_id):
    """Gather a particular product with associated reviews to pass into the product details page"""
    product = Products.query.get_or_404(product_id)
    # Will include reviews here later once functionality created
    return render_template("products/detail.html", product = product)

@product_bp.route("/search", methods = ['GET'])
def search():
    """Display results when searching for a product"""
    search_query = request.args.get("query", "")
    if search_query:
        products = Products.query.filter(
            Products.name.ilike(f"%{search_query}%")
        ).all()
    else:
        products = list()
    return render_template('products/search.html', products = products, query = search_query)