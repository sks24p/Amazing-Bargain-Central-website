from sqlalchemy import func
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy database instance
db = SQLAlchemy()

class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    # Columns
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), unique = True, nullable = False)
    name = db.Column(db.String(100), nullable = False)
    password_hash = db.Column(db.String(128), nullable = False)
    role = db.Column(db.String(20), default = "customer") 
    address = db.Column(db.String(200), nullable = False)
    created_at = db.Column(db.DateTime, default = func.now())
    # Constraints
    __table_args__ = (
        db.CheckConstraint("role IN ('customer', 'seller', 'admin')", name = 'check_role'),
    )
    # Relationships
    products = db.relationship('Products', back_populates='seller', lazy = True)
    orders = db.relationship('Orders', back_populates='user', lazy = True)
    reviews = db.relationship('Reviews', back_populates='user', lazy = True)

class Products(db.Model):
    __tablename__ = 'products'
    # Columns
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), unique = True, nullable = False)
    description = db.Column(db.Text, nullable = False)
    price = db.Column(db.Float, nullable = False)
    image_url = db.Column(db.String(150), nullable = False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    created_at = db.Column(db.DateTime, default = func.now())
    updated_at = db.Column(db.DateTime, default = func.now(), onupdate = func.now())
    # Constraints
    __table_args__ = (
        db.CheckConstraint('price > 0.00', name='price_zero'),
    )
    # Relationships
    seller = db.relationship('Users', back_populates='products', lazy = True)
    order_items = db.relationship('Order_Items', back_populates='product', lazy = True)
    reviews = db.relationship('Reviews', back_populates='product', lazy = True)

class Orders(db.Model):
    __tablename__ = 'orders'
    # Columns
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    total_price = db.Column(db.Float, nullable = False)
    status = db.Column(db.String(20), default = "Processing")
    created_at = db.Column(db.DateTime, default = func.now())
    # Constraints
    __table_args__ = (
        db.CheckConstraint('total_price >= 0.00', name='check_total_price'),
    )
    # Relationships
    user = db.relationship('Users', back_populates='orders', lazy = True)
    order_items = db.relationship('Order_Items', back_populates='order', lazy = True)

class Order_Items(db.Model):
    __tablename__ = 'order_items'
    # Columns
    id = db.Column(db.Integer, primary_key = True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable = False)
    quantity = db.Column(db.Integer, nullable = False, default = 1)
    price_at_purchase = db.Column(db.Float, nullable = False)
    # Constraints
    __table_args__ = (
        db.CheckConstraint('quantity > 0', name='check_quantity'),
    )
    # Relationships
    order = db.relationship('Orders', back_populates = 'order_items', lazy = True)
    product = db.relationship('Products', back_populates = 'order_items', lazy = True)

class Reviews(db.Model):
    __tablename__ = 'reviews'
    # Columns
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable = False)
    rating = db.Column(db.Integer, nullable = False)
    comment = db.Column(db.Text, nullable = False)
    created_at = db.Column(db.DateTime, default = func.now())
    # Constraints
    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating'),
    )
    # Relationships
    user = db.relationship('Users', back_populates = 'reviews', lazy = True)
    product = db.relationship('Products', back_populates = 'reviews', lazy = True)     


