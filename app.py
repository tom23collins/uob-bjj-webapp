from flask import Flask, redirect, render_template, url_for, request, abort
import flask
import flask_login
from db import db_query, db_update, db_query_values
import config
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config.from_object(config)
app.secret_key = app.config.get('SECRET_KEY')

users = db_query(app, 'SELECT * FROM user_table')
users = email_dict = {item[0]: {'password': item[1], 
                                'first_name': item[2], 
                                'last_name': item[3],
                                'medical_info': item[4],
                                'user_role': item[5]
                                } for item in users}
user = ''

if os.getenv('FLASK_ENV') == 'development':
    app.config['DEBUG'] = True

class User(flask_login.UserMixin):
    pass

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not flask_login.current_user.is_authenticated:
                flash("You need to be logged in to access this page.")
                return redirect(url_for('login'))
            if flask_login.current_user.user_role != role:
                flash("You don't have the required role to access this page.")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return None

    user = User()
    user.id = email
    user.first_name = users[email]['first_name']
    user.last_name = users[email]['last_name']
    user.medical_info = users[email]['medical_info']
    user.user_role = users[email]['user_role']
    return user

@app.route('/')
def index():
    sessions = db_query(app, 'SELECT * FROM event_table')
    
    if flask_login.current_user.is_authenticated:
        registrations = db_query_values(app, 'SELECT * FROM sign_up_log WHERE email = %s;', (flask_login.current_user.id,))

        updated_sessions = []

        for session in sessions:
            registered = any(str(session[0]) == registration[2] for registration in registrations)
            updated_sessions.append(session + (registered,))

        sessions = updated_sessions
    else:
        sessions = [row + (False,) for row in sessions]

    return render_template('index.html', 
                           event_data=sessions,
                           user=flask_login.current_user
                           )

@app.route('/committee-dashboard')
@role_required('committee')
def committee_dashboard():
    sessions = db_query(app, 'SELECT * FROM event_table')
    today = datetime.today().date()
    default_event = min(sessions, key=lambda event: (event[2] - today).days if (event[2] - today).days >= 0 else float('inf'))
    registrations = db_query_values(app, 'SELECT * FROM sign_up_log WHERE event_id = %s;', (default_event[0],))

    return render_template('/committee/dashboard.html', 
                           sign_ups=registrations,
                           user=flask_login.current_user
                           )

@app.route('/new-event', methods=['GET', 'POST'])
@role_required('committee')
def create_new_event():
    if flask.request.method == 'GET':
        return render_template('/committee/create_new_event.html',
                                user=flask_login.current_user)
    sql = """
    INSERT INTO event_table (`event_name`, `date`, `start_time`, `end_time`, `category`, `capacity`, `location`) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (flask.request.form['event_name'],
              flask.request.form['date'],
              flask.request.form.get('start_time'),
              flask.request.form.get('end_time'),
              flask.request.form.get('category'),
              flask.request.form.get('capacity'),
              flask.request.form.get('location'))
    db_update(app, sql, values)

    return render_template('/committee/create_new_event.html',
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
    if flask.request.method == 'GET':
        return render_template('user_register.html')
    sql = """
    INSERT INTO user_table (`email`, `password`, `first_name`, `last_name`, `medical_info`) 
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (flask.request.form['email'],
              generate_password_hash(flask.request.form['password']),
              flask.request.form['first_name'],
              flask.request.form['last_name'],
              flask.request.form['medical_info'])
    db_update(app, sql, values)

    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template('user_login.html')

    email = flask.request.form['email']
    password = flask.request.form['password']

    if email in users and check_password_hash(users[email]['password'], password):
        user = User()
        user.id = email
        flask_login.login_user(user)
        return redirect(url_for('index'))

    error = "Invalid email or password"
    return render_template('user_login.html', error=error)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('index'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run()
