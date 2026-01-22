from flask_login import current_user, login_required
from flask import abort, Blueprint, request, flash, render_template, url_for, redirect, current_app
from models import Products, Users, db
from security import File_Security as FS, Data_Security as DS
import markdown, bleach

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
        thumbnail = request.files.get("product_thumbnail")
        try:
            price = float(price_str)
        except (ValueError, TypeError):
            flash("Invalid price value.", category = "error")
            return redirect(url_for("seller.dashboard"))

        # Validate data
        if not all([name, description, price_str, thumbnail]):
            # If any field is left empty, return true
            flash("All fields are required.", category = "error")
            return redirect(url_for("seller.dashboard"))
        else:
            # Check if product exists
            product_exists = Products.query.filter_by(name = name).first()
            if product_exists:
                flash("This product already exists.", category = "error")
                return redirect(url_for("seller.dashboard"))
            # Check if price is not positive
            elif price <= 0.00:
                flash("Price can't be negative. Please input a positive value.", category = "error")
                return redirect(url_for("seller.dashboard"))
            else:
                # Sanitising description and converting it to markdown format
                cleaned_description = DS.sanitise_text_to_markdown(description)

                # Validating image file
                if thumbnail and thumbnail.filename:
                    try:
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