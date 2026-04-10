from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import qrcode

app = Flask(__name__)
app.secret_key = "secret123"

# DATABASE
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= MODELS =================

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
    food = db.Column(db.String(10))
    rating = db.Column(db.Float)
    available = db.Column(db.String(10), default="Yes")


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    room_id = db.Column(db.Integer)
    people = db.Column(db.Integer)
    check_in = db.Column(db.String(50))
    check_out = db.Column(db.String(50))
    total_price = db.Column(db.Float)


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer)
    amount = db.Column(db.Float)
    status = db.Column(db.String(20))


# CREATE DB
with app.app_context():
    db.create_all()

# ================= ROUTES =================

@app.route('/')
def index():
    query = request.args.get('search')

    if query:
        rooms = Room.query.filter(
            (Room.type.contains(query)) |
            (Room.name.contains(query))
        ).all()
    else:
        rooms = Room.query.all()

    return render_template('index.html', rooms=rooms, search=query)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            password=request.form['password']
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')


# 🔐 LOGIN (ADMIN + USER)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # ADMIN LOGIN
        if username == "admin" and password == "admin123":
            session['admin'] = True
            return redirect('/admin')

        # USER LOGIN
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            return redirect('/')
        else:
            return "Invalid credentials"

    return render_template('login.html')


# 🔓 LOGOUT (FIXED)
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# 🔐 ADMIN PANEL (SECURED)
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/login')

    rooms = Room.query.all()
    bookings = Booking.query.all()

    total_rooms = Room.query.count()
    total_bookings = Booking.query.count()
    total_revenue = sum([b.total_price for b in bookings])

    return render_template(
        'admin.html',
        rooms=rooms,
        bookings=bookings,
        total_rooms=total_rooms,
        total_bookings=total_bookings,
        total_revenue=total_revenue
    )


# ➕ ADD ROOM
@app.route('/add_room_admin', methods=['POST'])
def add_room_admin():
    if not session.get('admin'):
        return redirect('/login')

    room = Room(
        name=request.form['name'],
        type=request.form['type'],
        price=request.form['price'],
        image=request.form['image'],
        description=request.form['description'],
        food=request.form.get('food', 'No'),
        rating=4.0,
        available="Yes"
    )

    db.session.add(room)
    db.session.commit()

    return redirect('/admin')


# ❌ DELETE ROOM
@app.route('/delete_room/<int:id>')
def delete_room(id):
    if not session.get('admin'):
        return redirect('/login')

    room = Room.query.get(id)

    if room:
        db.session.delete(room)
        db.session.commit()

    return redirect('/admin')

@app.route('/cancel_booking/<int:id>')
def cancel_booking(id):
    if not session.get('admin'):
        return redirect('/login')

    booking = Booking.query.get(id)

    if booking:
        room = Room.query.get(booking.room_id)

        # make room available again
        if room:
            room.available = "Yes"

        db.session.delete(booking)
        db.session.commit()

    return redirect('/admin')

@app.route('/edit_room/<int:id>', methods=['GET', 'POST'])
def edit_room(id):
    if not session.get('admin'):
        return redirect('/login')

    room = Room.query.get(id)

    if request.method == 'POST':
        room.name = request.form['name']
        room.type = request.form['type']
        room.price = request.form['price']
        room.image = request.form['image']
        room.description = request.form['description']
        room.food = request.form['food']
        room.available = request.form['available']

        db.session.commit()
        return redirect('/admin')

    return render_template('edit_room.html', room=room)

@app.route('/room/<int:room_id>')
def room_details(room_id):
    room = Room.query.get(room_id)
    return render_template('room_details.html', room=room)


@app.route('/book/<int:room_id>', methods=['GET', 'POST'])
def book_room(room_id):
    if 'user_id' not in session:
        return redirect('/login')

    room = Room.query.get(room_id)

    if not room:
        return "Room not found"

    if request.method == 'POST':
        try:
            people = int(request.form.get('people'))
            check_in_str = request.form.get('check_in')
            check_out_str = request.form.get('check_out')

            if not check_in_str or not check_out_str:
                return "Please select dates"

            check_in = datetime.strptime(check_in_str, "%Y-%m-%d")
            check_out = datetime.strptime(check_out_str, "%Y-%m-%d")

            days = (check_out - check_in).days
            if days <= 0:
                return "Invalid date selection"

            total = days * room.price

            booking = Booking(
                user_id=session['user_id'],
                room_id=room.id,
                people=people,
                check_in=check_in_str,
                check_out=check_out_str,
                total_price=total
            )

            db.session.add(booking)
            db.session.commit()

            room.available = "No"
            db.session.commit()

            return redirect(f'/payment/{booking.id}')

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template('booking.html', room=room)


@app.route('/payment/<int:booking_id>', methods=['GET', 'POST'])
def payment(booking_id):
    booking = Booking.query.get(booking_id)

    if not booking:
        return "Booking not found"

    upi_data = f"upi://pay?pa=test@upi&pn=HotelBooking&am={booking.total_price}&cu=INR"
    qr = qrcode.make(upi_data)

    qr_path = f"static/images/qr_{booking.id}.png"
    qr.save(qr_path)

    if request.method == 'POST':
        method = request.form.get('method')

        payment = Payment(
            booking_id=booking.id,
            amount=booking.total_price,
            status=f"Paid via {method}"
        )

        db.session.add(payment)
        db.session.commit()

        return redirect('/my_bookings')

    return render_template('payment.html', booking=booking, qr_image=qr_path)


@app.route('/my_bookings')
def my_bookings():
    if 'user_id' not in session:
        return redirect('/login')

    bookings = Booking.query.filter_by(user_id=session['user_id']).all()
    return render_template('my_bookings.html', bookings=bookings)


@app.route('/add_sample_rooms')
def add_sample_rooms():
    if Room.query.count() > 0:
        return "Rooms already added!"

    room_types = ["Standard", "Deluxe", "Suite", "Premium"]

    for i in range(1, 21):
        room = Room(
            name=f"Room {i}",
            type=room_types[i % 4],
            price=2000 + i * 150,
            image=f"room{i}.jpg",
            description="Luxury room with AC, WiFi",
            food="Yes" if i % 2 == 0 else "No",
            rating=3.5 + (i % 2),
            available="Yes"
        )
        db.session.add(room)

    db.session.commit()
    return "Rooms Added Successfully!"


# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)