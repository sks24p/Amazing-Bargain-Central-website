from flask import Blueprint, abort, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required, login_user, logout_user, LoginManager
from models import db, Users
from flask_bcrypt import Bcrypt

# Creating blueprint
auth_bp = Blueprint('auth', __name__)

# Initialise Bcrypt
bcrypt = Bcrypt()

# Routes

# Login page
@auth_bp.route("/login", methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')
        # Check if user exists - filter by email
        user = Users.query.filter_by(email = email).first()
        # Validate data
        if not user:
            flash("User doesn't exist. Please navigate to the Register page and create an account.", category = 'error')
        else:
            # Check passwords
            stored_password = user.password_hash
            if bcrypt.check_password_hash(stored_password, password):
                flash('Login successful!', category = 'success')
                login_user(user, remember = False)
                return redirect(url_for('home'))
            else:
                flash('Password is incorrect. Please try again.', category = 'error')
    return render_template("auth/login.html")     

# Logout page
@auth_bp.route("/logout", methods = ['GET'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out!", category = 'info')
    return redirect(url_for('auth.login'))

# Register page
@auth_bp.route("/register", methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        address = request.form.get('address')

        # Validate data
        if not all([email, password, name, address]):
            flash("All fields are required.", category = "error")
        else:
            # Check if email exists
            email_exists = Users.query.filter_by(email = email).first()
            # Validate data
            if email_exists:
                flash("Email is already in use.", category = "error")
            elif len(email) > 120:
                flash("Email is too long (max 120 characters)", category = "error")
            elif len(name) > 100:
                flash("Name is too long (max 100 characters)", category = "error")
            elif len(password) < 8:
                flash("Password must be at least 8 characters", category = "error")
            elif not any(c.isupper() for c in password):
                flash("Password must contain at least one uppercase letter", category = "error")
            elif not any(c.isdigit() for c in password):
                flash("Password must contain at least one number", category = "error")
            elif '@' not in email:
                flash("Invalid email format", category = "error")
            elif '@' in name:
                flash("'@' not allowed in name", category = "error")
            elif len(address) > 200:
                flash("Address is too long (max 200 characters)", category="error") 
            elif any(character in email for character in ['<', '>', '"', "'"]):
                flash("Email contains invalid characters", category = "error")
            else:
                # All validation passed - so create user
                new_user = Users(
                    email = email,
                    password_hash = bcrypt.generate_password_hash(password).decode('utf-8'),
                    name = name,
                    address = address)  
                db.session.add(new_user)
                db.session.commit()

                # Check if the admin is logged in when creating an account
                if current_user.is_authenticated and current_user.role == "admin":
                    flash("User created!", category = "success")
                    return redirect(url_for('admin.users'))

                # Else, log the user in immediately
                login_user(new_user, remember = False)
                flash("User created!", category = "success")
                return redirect(url_for('home'))
    return render_template("auth/register.html")              

# Account page
@auth_bp.route("/account", methods = ["GET"])
@login_required
def account():
    """User account page - requires login """
    return render_template("auth/account.html")

# Upgrade to seller page
@auth_bp.route("/upgrade_to_seller", methods = ['POST'])
@login_required
def upgrade_to_seller():
    if current_user.role == "customer":
        # Update role to seller
        current_user.role = "seller"
        db.session.commit()
        # redirect user to account page
        flash("You are now a seller!", category='success')
        return redirect(url_for('auth.account'))
        # Dashboard page is unlocked for user and you can view it at the nav bar
    elif current_user.role in ['seller', 'admin']:
        flash(f"You are a {current_user.role}", category='info')
        return redirect(url_for('auth.account'))
    else:
        abort(403)