from multiprocessing import Value
from flask_login import current_user, login_required
from flask import abort, Blueprint, request, flash, render_template, url_for, redirect, current_app
from models import Products, db, Orders, Order_Items
from security import File_Security as FS, Data_Security as DS
from datetime import datetime, timedelta

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

# Helper functions

def check_product_ownership(product_id):
    """Check if current user owns product or is admin"""
    product = Products.query.get_or_404(product_id)
    if product.seller_id == current_user.id or current_user.role == 'admin':
        pass
    else:
        abort(403)
    return product  # Return product so route can use it

def check_order_access(order_id):
    """Check if current seller has items in order or is admin"""
    order = Orders.query.get_or_404(order_id)
    
    if current_user.role == 'admin':
        return order, order.order_items  # Admins see everything, so return all order items alongside order
    
    # Get seller's items in order
    seller_items = [
        item for item in order.order_items
        if item.product.seller_id == current_user.id
    ]
    
    if not seller_items:
        abort(403)
    
    return order, seller_items

def validating_add_product(name, description, price):
    if not all([name, description, price]):
        # If any field is left empty, return true
        raise ValueError("All fields are required.")
    if price <= 0:
        raise ValueError("Price must be a positive value.")
    # Check if a product with the inputted name exists
    exists = Products.query.filter_by(name = name).first()
    if exists:
        raise ValueError("This product already exists. Try a different name.")
    
    cleaned_description = DS.sanitise_text_to_markdown(description)
    return cleaned_description

def validating_edit_product(product, name, description, price):
    if not all([name, description, price]):
        # If any field is left empty, return true
        raise ValueError("All fields are required.")
    if price <= 0:
        raise ValueError("Price must be a positive value.")
    # Check if a product with the inputted name exists that's not the current product
    existing_product = Products.query.filter(Products.name == name, Products.id != product.id).first()
    if existing_product:
        raise ValueError("This product already exists. Try a different name.")
    cleaned_description = DS.sanitise_text_to_markdown(description)
    return cleaned_description

def process_thumbnail(thumbnail):
    """Save product image. Returns file path or raises error"""
    if not thumbnail or not thumbnail.filename:
        raise ValueError("Product thumbnail is required.")
    
    # Check if the file extension is valid
    FS.check_image_extension(thumbnail.filename)
    # Read file content (needed to check size and magic bytes)
    file_content = thumbnail.read()
    # Check if the file size exceeds the limit (5 MB in this case)
    file_size = len(file_content)
    FS.check_image_size(file_size)
    # Validate using magic bytes
    FS.check_image_type(file_content)
    # Sanitise and generate new secure file name
    secure_filename = FS.generate_secure_image_name(thumbnail.filename)
    # Save path
    saved_path = current_app.config["UPLOAD_FOLDER_PRODUCTS"] / secure_filename
    saved_path.parent.mkdir(parents = True, exist_ok = True)
    # Reset file pointer, after examining size and magic bytes, and save to disc
    thumbnail.seek(0)
    thumbnail.save(saved_path)
    # Store relative path for database
    image_path = f"uploads/products/{secure_filename}"   
    return image_path



# Routes

# Dashboard page
@seller_bp.route("/dashboard")
def dashboard():
    """Seller dashboard - manage products """
    return render_template("seller/dashboard.html")

# Product detail page for seller 
@seller_bp.route("/products")
def products():
    """Show all products belonging to seller """
    products = Products.query.filter_by(seller_id = current_user.id).all()
    return render_template("seller/products.html", products = products)

# Product detail for a particular product for seller 
@seller_bp.route("/products/<int:product_id>")
def product_detail(product_id):
    """ Show product's detail for a particular product for seller  """
    product = check_product_ownership(product_id)
    return render_template("seller/product_detail.html", product = product)


@seller_bp.route("/add_product", methods = ['POST', 'GET'])
def add_product():
    if request.method == "POST":
        # Get form data
        name = request.form.get('name')
        description = request.form.get("description")
        price_str = request.form.get("price")
        thumbnail = request.files.get("product_thumbnail")
        try:
            price = float(price_str)
        except (ValueError, TypeError):
            flash("Invalid price value.", category = "error")
            return redirect(url_for("seller.dashboard"))

        # Validate product fields and sanitise description
        try:
            cleaned_description = validating_add_product(name, description, price)
        except ValueError as e:
            flash(str(e), category="error")
            return redirect(url_for("seller.dashboard"))
        
        # Validate thumbnail, sanitise file name and return file path
        try:
            image_path = process_thumbnail(thumbnail)
        except ValueError as e:
            flash(str(e), category="error")
            return redirect(url_for("seller.dashboard"))
        except Exception as e:
            print(f"Error saving file: {e}")
            flash("Error uploading image. Please try again.", category = "error")
            return redirect(url_for("seller.dashboard"))

        # Create Products object (indented within if block as all images must have thumbnails)
        new_product = Products(
            name = name,
            description = cleaned_description,
            price = price,
            seller_id = current_user.id,
            image_path = image_path
        )
        db.session.add(new_product)
        db.session.commit()
        flash("You have successfully created a product!", category = "success")
        return redirect(url_for("seller.dashboard"))
    return render_template("seller/add_product.html")

@seller_bp.route("/manage-products/<int:product_id>/edit", methods = ["POST", "GET"])
def edit_product(product_id):
    # Query particular product
    product = check_product_ownership(product_id)

    if request.method == "POST":
        # Get form data
        name = request.form.get('name')
        description = request.form.get("description")
        price_str = request.form.get("price")
        thumbnail = request.files.get("product_thumbnail")
        try:
            price = float(price_str)
        except (ValueError, TypeError):
            flash("Invalid price value.", category = "error")
            return redirect(url_for("seller.dashboard"))
        
        # Validate product fields and sanitise description
        try:
            cleaned_description = validating_edit_product(product, name, description, price)
        except ValueError as e:
            flash(str(e), category="error")
            return redirect(url_for("seller.dashboard"))

        # Validate thumbnail, sanitise file name and return file path
        try:
            if thumbnail and thumbnail.filename:
               image_path = process_thumbnail(thumbnail)
               product.image_path = image_path
        except ValueError as e:
            flash(str(e), category="error")
            return redirect(url_for("seller.dashboard"))
        except Exception as e:
            print(f"Error saving file: {e}")
            flash("Error uploading image. Please try again.", category = "error")
            return redirect(url_for("seller.dashboard"))

        # Update product fields
        product.name = name
        product.description = cleaned_description
        product.price = price
        db.session.commit()
        
        flash("Product updated successfully!", category = "success")
        return redirect(url_for("seller.dashboard"))
    return render_template("seller/edit_product.html", product = product)


@seller_bp.route("/manage-products/<int:product_id>/remove", methods = ["POST"])
def remove_product(product_id):
    """Delete product"""
    if request.method == "POST":
        product = check_product_ownership(product_id)

        db.session.delete(product)
        db.session.commit()
        flash("Product deleted", category = "info")
        return redirect(url_for("seller.dashboard"))
    
@seller_bp.route("/manage-orders")
def orders():
    # Query seller's orders (s_o_query for short)
    s_o_query = db.session.query(Orders).join(
        Order_Items, Orders.id == Order_Items.order_id
    ).join(
        Products, Order_Items.product_id == Products.id
    ).filter(
        Products.seller_id == current_user.id
    )

    # Status filter
    status_filter = request.args.get('status', 'all')
    if status_filter != "all":
        s_o_query = s_o_query.filter(Orders.status == status_filter)

    # Date filter
    date_filter = request.args.get('date', 'all')

    match (date_filter):
        case 'today':
            today_start = datetime.now().replace(hour = 0, minute = 0, second = 0)
            s_o_query = s_o_query.filter(Orders.created_at >= today_start)
        case 'yesterday':
            yesterday = datetime.now() - timedelta(days = 1)
            yesterday_start = yesterday.replace(hour = 0, minute = 0, second = 0)
            today_start = datetime.now().replace(hour = 0, minute = 0, second = 0)
            s_o_query = s_o_query.filter(Orders.created_at >= yesterday_start, Orders.created_at < today_start)
        case 'week':
            week_ago = datetime.now() - timedelta(days = 7)
            s_o_query = s_o_query.filter(Orders.created_at >= week_ago)
        case 'month':
            month_ago = datetime.now() - timedelta(days = 30)
            s_o_query = s_o_query.filter(Orders.created_at >= month_ago)
        case 'year':
            year_ago = datetime.now() - timedelta(days = 365)
            s_o_query = s_o_query.filter(Orders.created_at >= year_ago)
    
    # Limit filter
    limit_filter = request.args.get('limit', 20, type = int)
    
    orders = s_o_query.distinct().order_by(Orders.created_at.desc()).limit(limit_filter).all()
    return render_template('seller/orders.html',
                           orders = orders,
                           current_status = status_filter,
                           current_date = date_filter,
                           current_limit = limit_filter)

@seller_bp.route("/manage-orders/<int:order_id>")
def order_detail(order_id):
    order, seller_items = check_order_access(order_id)
    total = sum(item.quantity * item.product_price_at_purchase for item in seller_items)

    return render_template("seller/order_detail.html", order = order, seller_items = seller_items, total = total)

@seller_bp.route("/manage-orders/<int:order_id>/<int:order_item_id>")
def order_item_detail(order_id, order_item_id):
    order_item = Order_Items.query.get_or_404(order_item_id)

    if order_item.product.seller_id == current_user.id or current_user.role == 'admin':
        pass
    else:
        abort(403)

    return render_template("seller/order_item_detail.html", order_item = order_item)
