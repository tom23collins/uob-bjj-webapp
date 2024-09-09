from flask import Flask, redirect, render_template, url_for, request, flash
import flask_login
from db import db_query, db_update, db_query_values
import config
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from scripts import format_date
import requests

app = Flask(__name__)
app.config.from_object(config)
app.secret_key = app.config.get('SECRET_KEY')

if os.getenv('FLASK_ENV') == 'development':
    app.config['DEBUG'] = True

class User(flask_login.UserMixin):
    pass

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not flask_login.current_user.is_authenticated:
                flash("You need to be logged in to access this page.")
                return redirect(url_for('login'))
            
            # Bypass if user role is admin
            if flask_login.current_user.user_role == 'administrator':
                return f(*args, **kwargs)

            # Check if the user has the required role
            if flask_login.current_user.user_role != role:
                flash("You don't have the required role to access this page.")
                return redirect(url_for('index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


@login_manager.user_loader
def user_loader(email):
    user_data = db_query_values(app, 'SELECT * FROM user_table WHERE email = %s', (email,))
    if not user_data:
        return None

    user = User()
    user.id = user_data[0][0]
    user.password = user_data[0][1]
    user.first_name = user_data[0][2]
    user.last_name = user_data[0][3]
    user.medical_info = user_data[0][4]
    user.user_role = user_data[0][5]
    return user

@app.route('/')
def index():
    current_date = datetime.now().strftime('%Y-%m-%d')
    session_data = db_query_values(app, 'SELECT * FROM event_table WHERE date >= %s', (current_date,))
    updated_sessions = []
    registrations = []

    if flask_login.current_user.is_authenticated:
        registrations = db_query_values(app, 'SELECT * FROM sign_up_log WHERE email = %s;', (flask_login.current_user.id,))

    registration_event_ids = {int(registration[2]) for registration in registrations}

    for session in session_data:
        registration_count = db_query_values(app, 'SELECT COUNT(*) FROM sign_up_log WHERE event_id = %s', (session[0],))

        event = {
            'event_id': session[0],
            'event_name': session[1],
            'date': format_date(session[2]),
            'start_time': datetime.strptime(str(session[3]), "%H:%M:%S").strftime("%H:%M"),
            'end_time': datetime.strptime(str(session[4]), "%H:%M:%S").strftime("%H:%M"),
            'category': session[5],
            'capacity': session[6] - registration_count[0][0],
            'location': session[7],
            'location_link': session[8],
            'registered': int(session[0]) in registration_event_ids if flask_login.current_user.is_authenticated else False,
            'registration_count': registration_count
        }
        updated_sessions.append(event)

    return render_template('index.html', 
                           event_data=updated_sessions,
                           user=flask_login.current_user)

@app.route('/class-sign-up', methods=['GET'])
@flask_login.login_required
def class_sign_up():
    if request.method == 'GET':
        sql = """
        INSERT INTO sign_up_log (`email`, `event_id`, `timestamp`) 
        VALUES (%s, %s, %s)
        """
        values = (flask_login.current_user.id,
                  request.args.get('event_id'),
                  datetime.now())
        db_update(app, sql, values)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('user_register.html')

    # Prepare SQL query to insert new user
    sql = """
    INSERT INTO user_table (`email`, `password`, `first_name`, `last_name`, `medical_info`)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (
        request.form['email'],
        generate_password_hash(request.form['password']),
        request.form['first_name'],
        request.form['last_name'],
        request.form['medical_info']
    )

    # Execute the database update function
    db_update(app, sql, values)

    # Redirect to the login page after successful registration
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('user_login.html')

    # Extract email and password from the form submission
    email = request.form['email']
    password = request.form['password']

    # Load the user using the email
    user = user_loader(email)
    if user and check_password_hash(user.password, password):
        flask_login.login_user(user)
        return redirect(url_for('index'))

    # If login fails, return an error
    error = "Invalid email or password. Please contact a comittee member if you have forgotten your login."
    return render_template('user_login.html', error=error)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('index'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('register'))


# Committee views
@app.route('/sign-ups', methods=['GET'])
@role_required('committee')
@flask_login.login_required
def view_sign_ups():
    sign_up_data = []
    event_id = (request.args.get('event_id'),)
    sql = "SELECT * FROM sign_up_log WHERE event_id = %s"
    for sign_ups in db_query_values(app, sql, event_id):
        names = db_query_values(app, "SELECT first_name, last_name FROM user_table WHERE email = %s", (sign_ups[1],))
        sign_up = {
            'first_name': names[0][0],
            'last_name': names[0][1],  # Convert event_id to integer
            'time_stamp': sign_ups[3]
        }
        sign_up_data.append(sign_up)

    data = db_query_values(app, 'SELECT * FROM event_table WHERE event_id = %s', event_id)
    event = {
        'event_id': data[0][0],
        'event_name': data[0][1],
        'date': format_date(data[0][2]),
        'start_time': datetime.strptime(str(data[0][3]), "%H:%M:%S").strftime("%H:%M"),
        'end_time': datetime.strptime(str(data[0][4]), "%H:%M:%S").strftime("%H:%M"),
        'category': data[0][5],
        'capacity': data[0][6],
        'location': data[0][7]
    }
    
    return render_template('/committee/sign_ups.html',
                           user=flask_login.current_user,
                           event_data=event,
                           data=sign_up_data)


@app.route('/new-event', methods=['GET', 'POST'])
@role_required('committee')
def create_new_event():
    if request.method == 'GET':
        return render_template('/committee/create_new_event.html',
                               user=flask_login.current_user)
    
    sql = """
    INSERT INTO event_table (`event_name`, `date`, `start_time`, `end_time`, `category`, `capacity`, `location`, `location_link`)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        request.form['event_name'],
        request.form['date'],
        request.form.get('start_time'),
        request.form.get('end_time'),
        request.form.get('category'),
        request.form.get('capacity'),
        request.form.get('location'),
        request.form.get('location_link')
    )
    db_update(app, sql, values)

    return render_template('/committee/create_new_event.html',
                           user=flask_login.current_user)


@app.route('/edit-event', methods=['GET', 'POST'])
@role_required('committee')
@flask_login.login_required
def edit_event():
    if request.method == 'GET':
        event_id = (request.args.get('event_id'),)
        data = db_query_values(app, 'SELECT * FROM event_table WHERE event_id = %s', event_id)
        event = {
            'event_id': data[0][0],
            'event_name': data[0][1],
            'date': data[0][2].strftime("%Y-%m-%d"),
            'start_time': datetime.strptime(str(data[0][3]), "%H:%M:%S").strftime("%H:%M"),
            'end_time': datetime.strptime(str(data[0][4]), "%H:%M:%S").strftime("%H:%M"),
            'category': data[0][5],
            'capacity': data[0][6],
            'location': data[0][7],
            'location_link': data[0][8]
        }
        return render_template('/committee/edit_event.html', user=flask_login.current_user, data=event)
    
    if request.method == 'POST':
        # SQL Update Statement
        sql = """
        UPDATE event_table
        SET event_name = %s, date = %s, start_time = %s, end_time = %s,
            category = %s, capacity = %s, location = %s, location_link = %s
        WHERE event_id = %s
        """
        
        # Extract form data
        values = (
            request.form['event_name'],
            request.form['date'],
            request.form['start_time'],
            request.form['end_time'],
            request.form['category'],
            request.form['capacity'],
            request.form['location'],
            request.form['location_link'],
            request.form['event_id'],  # Ensure the event_id is passed for the WHERE clause
        )
        # Update the database
        db_update(app, sql, values)
        
        return redirect(url_for('index'))


@app.route('/members', methods=['GET'])
@role_required('committee')
@flask_login.login_required
def members():
    data = []
    for users in db_query(app, 'SELECT * FROM user_table'):
        user = {
            'email': users[0],
            'first_name': users[2],
            'last_name': users[3],
            'medical_info': users[4],
            'user_role': users[5]
        }
        data.append(user)
    return render_template('/committee/members.html',
                           user=flask_login.current_user,
                           data=data)

@app.route('/update-password', methods=['GET'])
@role_required('committee')
@flask_login.login_required
def update_password():
    if request.method == 'GET':
        # Prepare SQL query to update the password for an existing user
        sql = """
        UPDATE user_table
        SET `password` = %s
        WHERE `email` = %s
        """
        values = (
            generate_password_hash(request.args.get('password')),  # Hash the new password
            request.args.get('email'),  # Identify the user by email
        )

        # Execute the database update function
        db_update(app, sql, values)
    return redirect(url_for('members'))

@app.route('/update-role', methods=['GET'])
@role_required('committee')
@flask_login.login_required
def update_role():
    if request.method == 'GET':
        # Prepare SQL query to update the password for an existing user
        sql = """
        UPDATE user_table
        SET `user_role` = %s
        WHERE `email` = %s
        """
        values = (
            request.args.get('user_role'),
            request.args.get('email'),  # Identify the user by email
        )

        # Execute the database update function
        db_update(app, sql, values)
    return redirect(url_for('members'))


if __name__ == "__main__":
    app.run()