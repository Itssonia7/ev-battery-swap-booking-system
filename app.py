from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, Booking

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('User already exists. Please login.', 'error')
            return redirect(url_for('login'))
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful. Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    return render_template('login.html')

# Logout route (handles unauthenticated access gracefully)
@app.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Admin login route
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == "admin@evswap.com" and password == "admin123":
            users = User.query.all()
            bookings = Booking.query.all()
            return render_template('admin_dashboard.html', users=users, bookings=bookings)
        else:
            flash('Invalid admin credentials.', 'error')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

# Book appointment route
@app.route('/book', methods=['POST'])
@login_required
def book():
    station = request.form['station']
    date = request.form['date']
    time = request.form['time']
    new_booking = Booking(user_id=current_user.id, station=station, date=date, time=time)
    db.session.add(new_booking)
    db.session.commit()
    flash('Appointment booked successfully!', 'success')
    return redirect(url_for('home'))

# Main entry
if __name__ == '__main__':
    app.run(debug=True)
