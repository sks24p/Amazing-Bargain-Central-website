from app import app, db
from models import Users

with app.app_context():
    email = input("\nEnter email of user to make admin: ")

    user = Users.query.filter_by(email = email).first()
    if user:
        user.role = "admin"
        print(f"\nUser {user.name} ({user.email} is now an admin!)")
        db.session.commit()
    else:
        print("\nUser not found.")