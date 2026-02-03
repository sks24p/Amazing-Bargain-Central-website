from flask_login import current_user, login_required
from flask import abort, Blueprint, flash, render_template, url_for, redirect, request
from models import Users, db, Products, Orders, Order_Items
from datetime import datetime, timedelta


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

# Helper functions


# Routes

# Dashboard page
@admin_bp.route("/dashboard", methods = ["GET"])
def dashboard():
    """Admin dashboard - manage users and site """
    return render_template("admin/dashboard.html")

@admin_bp.route("/users")
def users():
    """View all users"""
    page = request.args.get('page', 1, type = int)
    search_filter = request.args.get("search", "")
    query = Users.query

    if search_filter != "all":
        # Search for email
        if "@" in search_filter:
            query = query.filter(Users.email.ilike(f"%{search_filter}%"))
        else:
            query = query.filter(Users.name.ilike(f"%{search_filter}%"))

    users = query.order_by(Users.created_at.desc()).paginate(page = page, per_page = 20)
    return render_template("admin/users.html", users = users)

@admin_bp.route("/users/<int:user_id>")
def user_detail(user_id):
    """View a user's details """
    user = Users.query.get_or_404(user_id)
    return render_template("admin/user_detail.html", user = user)

@admin_bp.route("/users/<int:user_id>/update-role", methods = ['POST'])
def user_role(user_id):
    """Change a user's role """
    if request.method == "POST":
        user_role = request.form.get("user_role")
        # Preventing user from manipulating permissions
        if user_role not in ["customer", "seller"]:
            abort(403)
        user = Users.query.get_or_404(user_id)
        user.role = user_role
        db.session.commit()
        flash(f"User role change successfully to {user_role}.", category = "success")
        return redirect(url_for('admin.user_detail', user_id = user_id))

@admin_bp.route("/users/<int:user_id>/delete", methods = ['POST'])
def delete_user(user_id):
    user = Users.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted.", category = "success")
    return redirect(url_for('admin.users'))

@admin_bp.route("/products")
def products():
    """ View all products on ABC """
    page = request.args.get('page', 1, type = int)
    product_name = request.args.get('product_name', "")
    seller_name = request.args.get('seller_name', "")
    # Join Products and Users tables to look at rows in both tables
    query = db.session.query(Products).join(Users, Products.seller_id == Users.id)

    # Filtering products by product name
    if product_name != "":
        query = query.filter(Products.name.ilike(f"%{product_name}%"))

    # Filtering users by seller name
    if seller_name != "":
        query = query.filter(Users.name.ilike(f"%{seller_name}%"))

    products = query.order_by(Products.created_at.desc()).paginate(page = page, per_page = 20)
    return render_template("admin/products.html", products = products)

@admin_bp.route("/orders")
def orders():
    """View all orders on ABC (not a specific seller's ones)"""
    page = request.args.get('page', 1, type = int)
    query = Orders.query

    # Status filter
    status_filter = request.args.get('status', 'all')
    if status_filter != "all":
        query = query.filter(Orders.status == status_filter)

    # Date filter
    date_filter = request.args.get('date', 'all')
    match (date_filter):
        case 'today':
            today_start = datetime.now().replace(hour = 0, minute = 0, second = 0)
            query = query.filter(Orders.created_at >= today_start)
        case 'yesterday':
            yesterday = datetime.now() - timedelta(days = 1)
            yesterday_start = yesterday.replace(hour = 0, minute = 0, second = 0)
            today_start = datetime.now().replace(hour = 0, minute = 0, second = 0)
            query = query.filter(Orders.created_at >= yesterday_start, Orders.created_at < today_start)
        case 'week':
            week_ago = datetime.now() - timedelta(days = 7)
            query = query.filter(Orders.created_at >= week_ago)
        case 'month':
            month_ago = datetime.now() - timedelta(days = 30)
            query = query.filter(Orders.created_at >= month_ago)
        case 'year':
            year_ago = datetime.now() - timedelta(days = 365)
            query = query.filter(Orders.created_at >= year_ago)
    
    orders = query.distinct().order_by(Orders.created_at.desc()).paginate(page = page, per_page = 20)
    return render_template('admin/orders.html',
                           orders = orders,
                           current_status = status_filter,
                           current_date = date_filter)

@admin_bp.route("/manage-orders/<int:order_id>/change-status", methods = ['POST'])
def change_order_status(order_id):
    """Change the status of an order (Admins only allowed)"""
    order = Orders.query.get_or_404(order_id)
    order_status = request.form.get("order_status")

    # Prevent admin from tampering with order status outside of these accepted values
    if order_status not in ["processing", "fulfilled", "denied"]:
        abort(401)
    order.status = order_status
    db.session.commit()
    flash("Order status has successfully been updated!", category = "success")
    return redirect(url_for('seller.order_detail', order_id = order_id))