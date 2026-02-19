from flask import Blueprint, abort, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required, login_user, logout_user, LoginManager
from models import db, Users
from flask_bcrypt import Bcrypt
from logger import log_event

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
            # Log login failure
            log_event('login_failure', f'User {email} not found', severity = 'warning')
            flash("User doesn't exist. Please navigate to the Register page and create an account.", category = 'error')
        else:
            # Check passwords
            stored_password = user.password_hash
            if bcrypt.check_password_hash(stored_password, password):
                login_user(user, remember = False)
                flash('Login successful!', category = 'success')
                # Log login success
                log_event('login_success', f'User {email} logged in')
                return redirect(url_for('home'))
            else:
                # Log login failure
                log_event('login_failure', f'Wrong password for {email}', severity = 'warning')
                flash('Password is incorrect. Please try again.', category = 'error')
    return render_template("auth/login.html")     

# Logout page
@auth_bp.route("/logout", methods = ['GET'])
@login_required
def logout():
    logout_user()
    # Log logout
    log_event('logout', f'User {current_user.email} has logged out')
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
            # Log registration failure
            log_event('registration_failed', 
                      f"User left at least one input field empty before registration submission", 
                      severity = "warning")
        else:
            # Check if email exists
            email_exists = Users.query.filter_by(email = email).first()
            # Validate data
            if email_exists:
                flash("Email is already in use.", category = "error")
                # Log registration failure
                log_event('registration_failed', 
                        f"User already has an account", 
                        severity = "warning")
            elif len(email) > 120:
                flash("Email is too long (max 120 characters)", category = "error")
                # Log registration failure
                log_event('registration_failed', 
                        f"User's email input exceeded 120 characters during registration submission", 
                        severity = "warning")
            elif len(name) > 100:
                flash("Name is too long (max 100 characters)", category = "error")
                # Log registration failure
                log_event('registration_failed', 
                        f"User's name input exceeded 100 characters during registration submission", 
                        severity = "warning")
            elif len(password) < 8:
                flash("Password must be at least 8 characters", category = "error")
                # Log registration failure
                log_event('registration_failed', 
                        f"User's password input was less than 8 characters during registration submission", 
                        severity = "warning")
            elif not any(c.isupper() for c in password):
                flash("Password must contain at least one uppercase letter", category = "error")
            elif not any(c.isdigit() for c in password):
                flash("Password must contain at least one number", category = "error")
            elif '@' not in email:
                flash("Invalid email format", category = "error")
                # Log registration failure
                log_event('registration_failed', 
                        f"User's email input didn't contain '@' during registration submission", 
                        severity = "warning")
            elif '@' in name:
                flash("'@' not allowed in name", category = "error")
                # Log registration failure
                log_event('registration_failed', 
                        f"User's name input contained '@' during registration submission", 
                        severity = "warning")
            elif len(address) > 200:
                flash("Address is too long (max 200 characters)", category="error") 
                # Log registration failure
                log_event('registration_failed', 
                        f"User's address input exceeded 200 characters during registration submission", 
                        severity = "warning")
            elif any(character in email for character in ['<', '>', '"', "'"]):
                flash("Email contains invalid characters", category = "error")
                # Log registration failure
                log_event('registration_failed', 
                        f"User's email input contained invalid characters during registration submission", 
                        severity = "warning")
            else:
                # All validation passed - so create user
                new_user = Users(
                    email = email,
                    password_hash = bcrypt.generate_password_hash(password).decode('utf-8'),
                    name = name,
                    address = address)  
                db.session.add(new_user)
                db.session.commit()
                # Log registration success
                log_event('register_user', f'User {email} has been created')

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
        # Log upgrade to seller
        log_event('seller_upgrade', f'User {current_user.email} has upgraded to a seller')
        return redirect(url_for('auth.account'))
        # Dashboard page is unlocked for user and you can view it at the nav bar
    elif current_user.role in ['seller', 'admin']:
        flash(f"You are a {current_user.role}", category='info')
        # Log review submission failure
        log_event('seller_upgrade_failed', 
                    f"User {current_user.email}, despite being a {current_user.role}, tried to upgrade to seller but failed", 
                    severity = "error")
        return redirect(url_for('auth.account'))
    else:
        abort(403)