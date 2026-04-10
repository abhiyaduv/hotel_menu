from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# USER TABLE (LOGIN SYSTEM)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))




class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(50))
    price = db.Column(db.Float)
    image = db.Column(db.String(200))
    description = db.Column(db.String(300))
    food = db.Column(db.String(10))   # Yes/No
    rating = db.Column(db.Float)      # 1 to 5
    available = db.Column(db.String(10), default="Yes")
# BOOKING TABLE
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    room_id = db.Column(db.Integer)
    people = db.Column(db.Integer)
    check_in = db.Column(db.String(50))
    check_out = db.Column(db.String(50))

    total_price = db.Column(db.Float)


# PAYMENT TABLE
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer)
    amount = db.Column(db.Float)
    status = db.Column(db.String(50))