from flask_login import current_user, login_required
from flask import abort, Blueprint, flash, render_template, request, url_for, redirect
from models import Products, Cart_Items, db, Orders, Order_Items

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

@product_bp.route("/product/<int:product_id>/add-to-cart", methods = ['POST'])
@login_required
def add_to_cart(product_id):
    """Add product to the cart"""
    if request.method == 'POST':
        quantity_str = request.form.get('quantity')
        
        # Validate data
        if not quantity_str:
            flash("This field cannot be left empty.", category = "error")
            return redirect(url_for('products.product_detail', product_id = product_id))
        try:
            quantity = int(quantity_str)
        except (ValueError, TypeError):
            flash("Invalid input. Please try again.", category = "error")
            return redirect(url_for('products.product_detail', product_id = product_id))
        if quantity <= 0:
            flash("Quantity must be greater than 0.", category = "error")
            return redirect(url_for('products.product_detail', product_id = product_id))
        # Check if cart item exists
        cart_item_exists = Cart_Items.query.filter_by(user_id = current_user.id, product_id = product_id).first()
        if cart_item_exists:
            # Add on quantity
            cart_item_exists.quantity += quantity
        else:
            new_cart_item = Cart_Items(
                user_id = current_user.id,
                product_id = product_id,
                quantity = quantity
            )
            db.session.add(new_cart_item)
        db.session.commit()
        flash("Added to cart!", category = "success")
        return redirect(url_for('products.product_detail', product_id = product_id))
        
@product_bp.route("/cart")
@login_required
def view_cart():
    # Query all cart items for user
    cart_items = Cart_Items.query.filter_by(user_id = current_user.id).all()
    if not cart_items:
        flash("Cart is empty. Please add items to cart to checkout.", category = "info")
    # Calculate total for each cart_item (subtotal)
    cart_total = sum(item.quantity * item.product.price for item in cart_items)
    return render_template("products/cart.html", cart_total = cart_total, cart_items = cart_items)

@product_bp.route("/cart/<int:cart_item_id>/update", methods = ['POST'])
@login_required
def update_cart_item(cart_item_id):
    """Update the quantity of a product, within a cart item"""
    # Validate data
    if request.method == "POST":
        quantity_str = request.form.get("quantity")
        try:
            new_quantity = int(quantity_str)
        except (ValueError, TypeError):
            flash("Invalid input. Please try again.", category = "error")
            return redirect(url_for('products.view_cart'))
        if new_quantity <= 0:
            flash("Number must be greater than 0.", category = "error")
            return redirect(url_for('products.view_cart'))

        # Query cart item and validate that it matches user
        cart_item = Cart_Items.query.get_or_404(cart_item_id)
        if cart_item.user_id != current_user.id:
            abort(403)
        # Update quantity
        cart_item.quantity = new_quantity 
        db.session.commit()
        return redirect(url_for('products.view_cart'))

@product_bp.route("/cart/<int:cart_item_id>/remove", methods = ['POST'])
@login_required
def remove_from_cart(cart_item_id):
    """Remove a cart item"""
    if request.method == "POST":
        cart_item = Cart_Items.query.get_or_404(cart_item_id)
        if cart_item.user_id != current_user.id:
            abort(403)
        db.session.delete(cart_item)
        db.session.commit()
        flash("Item removed!", category = "info")
        return redirect(url_for("products.view_cart"))

@product_bp.route("/checkout", methods = ['GET', 'POST'])
@login_required
def checkout():
    # Query all cart items for user
    all_cart_items = Cart_Items.query.filter_by(user_id = current_user.id).all()
    if not all_cart_items:
        flash("Cart is empty. Please add items to cart to checkout.", category = "info")
        return redirect(url_for("home"))
    # Calculate total for each cart_item (subtotal)
    grand_total = sum(item.quantity * item.product.price for item in all_cart_items)
    return render_template("products/checkout.html", grand_total = grand_total, 
                           all_cart_items = all_cart_items)

@product_bp.route("/checkout/place-order", methods = ['POST'])
@login_required
def place_order():
    if request.method == "POST":
        # Get delivery address from form
        delivery_address = request.form.get("delivery_address")
        if not delivery_address:
            flash("Empty field. Please try again.", category = "error")
            return redirect(url_for("products.checkout"))
        # Get all cart items from user
        cart_items = Cart_Items.query.filter_by(user_id = current_user.id).all()
        if not cart_items:
            flash("Cart is empty.", category="error")
            return redirect(url_for('products.view_cart'))
        total_price = sum(item.quantity * item.product.price for item in cart_items)
        try:
            # Create Orders record
            new_order = Orders(
                user_id = current_user.id,
                total_price = total_price,
                delivery_address = delivery_address
            )
            db.session.add(new_order)
            # Send pending changes to the database to get ID of order for Order_items
            db.session.flush()
            # For each cart item, create Order_items record
            for item in cart_items:
                # Validation for if the quantity = 0 somehow for a cart item
                if item.quantity <= 0:
                    flash("One of your items has a quantity that isn't positive. Please fix this.", category = "error")
                    return redirect(url_for("products.view_cart"))
                # Query cart item and validate that it matches user
                if item.user_id != current_user.id:
                    abort(403)
                
                new_order_item = Order_Items(
                    order_id = new_order.id,
                    product_id = item.product.id,
                    quantity = item.quantity,
                    product_price_at_purchase = item.product.price
                )
                db.session.add(new_order_item)
                # After creating order item, delete cart item from cart
                db.session.delete(item)
            db.session.commit()
            return redirect(url_for('products.order_success', order_id = new_order.id))
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            flash("Something went wrong. Please try again.", category = "error")
            return redirect(url_for('products.checkout'))

@product_bp.route("/order/<int:order_id>/success")
@login_required
def order_success(order_id):
    # Query order
    order = Orders.query.get_or_404(order_id)
    # Verify order belongs to current user
    if order.user_id != current_user.id:
        abort(403)
    flash("Order placed successfully!", category = "success")
    return render_template("products/order_success.html", order = order)

@product_bp.route("/my-orders")
@login_required
def my_orders():
    # Query orders for current user
    my_orders = current_user.orders 
    #Orders.query.filter_by(user_id=current_user.id).order_by(Orders.created_at.desc()).all()
    return render_template("order/history.html", orders = my_orders)

@product_bp.route("/order/<int:order_id>")
@login_required
def order_detail(order_id):
    # Query order
    order = Orders.query.get_or_404(order_id)
    # Query all items that belong to order
    order_items = Order_Items.query.filter_by(order_id = order_id).all()
    if order.user_id != current_user.id:
        abort(403)
    return render_template('order/detail.html', order = order, order_items = order_items)
