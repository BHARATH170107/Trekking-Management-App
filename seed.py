"""
Run this ONCE to create the pre-existing Admin account
(the project spec says admin must pre-exist -- no admin registration route).

    python seed.py

Default login after seeding:
    email:    admin@trek.com
    password: admin123
"""
from app import app
from extensions import db
from models import User

with app.app_context():
    db.create_all()

    existing_admin = User.query.filter_by(role="admin").first()
    if existing_admin:
        print("Admin already exists:", existing_admin.email)
    else:
        admin = User(
            name="Admin",
            email="admin@trek.com",
            contact="0000000000",
            role="admin",
            status="active",
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Admin created -> email: admin@trek.com | password: admin123")
