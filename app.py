import functools
from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, g
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# --- App and Database Configuration ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://reyhane:password123@localhost/location_app_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'a_very_secret_key_that_is_hard_to_guess'
db = SQLAlchemy(app)


# --- Database Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    places = db.relationship('SavedPlace', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class SavedPlace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place_name = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<SavedPlace {self.place_name}>'

# --- Functions to manage user login state ---

@app.before_request
def load_logged_in_user():
    """If a user id is in the session, load the user object from the database."""
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        # Get the user data from the database
        g.user = User.query.get(user_id)

def login_required(view):
    """
    A decorator to protect views. Redirects to login page if user is not logged in.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view


# --- Web Page Routes ---

@app.route('/')
def hello():
    # Now the homepage just renders the layout
    return render_template('layout.html')

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        
        user = User.query.filter_by(username=username).first()

        if user is None or not check_password_hash(user.password_hash, password):
            error = 'Incorrect username or password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('dashboard')) # Redirect to the new dashboard
        
        flash(error)
    return render_template('login.html')

# --- NEW: Logout and Dashboard Routes ---

@app.route('/logout')
def logout():
    """Clear the current session, including the user_id."""
    session.clear()
    return redirect(url_for('hello'))

@app.route('/dashboard')
@login_required  # This protects the page
def dashboard():
    """Show the user's personal dashboard."""
    return render_template('dashboard.html')


# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True, port=8000)

