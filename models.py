from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class User(UserMixin, db.Model):
    """
    Single table for all three roles (admin / staff / trekker).
    Using one table with a `role` column is simpler than three separate
    tables and is enough to satisfy the requirements -- keep it simple
    so you can explain every column in the viva.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    contact = db.Column(db.String(50))
    role = db.Column(db.String(20), nullable=False)  # 'admin' | 'staff' | 'trekker'

    # Trekkers are 'active' immediately. Staff start as 'pending' until
    # the admin approves them. Anyone can be set to 'blacklisted'.
    status = db.Column(db.String(20), default="active")

    # Treks this user manages (only meaningful when role == 'staff')
    treks_assigned = db.relationship("Trek", backref="staff", lazy=True)

    # Bookings this user has made (only meaningful when role == 'trekker')
    bookings = db.relationship("Booking", backref="trekker", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Trek(db.Model):
    __tablename__ = "treks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # Easy / Moderate / Hard
    duration = db.Column(db.Integer, nullable=False)  # in days
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)

    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Pending -> Approved -> Open -> Closed/Completed
    status = db.Column(db.String(20), default="Pending")

    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    bookings = db.relationship("Booking", backref="trek", lazy=True)

    def __repr__(self):
        return f"<Trek {self.name} ({self.status})>"


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Booked")  # Booked / Cancelled / Completed

    def __repr__(self):
        return f"<Booking user={self.user_id} trek={self.trek_id} ({self.status})>"
