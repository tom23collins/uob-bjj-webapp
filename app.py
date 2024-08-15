from flask import Flask, redirect, render_template, url_for, request
import flask
import flask_login
from db import db_query, db_update
import config
import os
from datetime import datetime

# Backend to do:
# Hash passwords
# Check if user is signed up for event (user feedback)
# Create new events
# Dashboard for users with commitee role

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

@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    user.first_name = users[email]['first_name']
    user.last_name = users[email]['last_name']
    user.medical_info = users[email]['medical_info']
    user.user_role = users[email]['user_role']
    return user

@app.route('/')
def index():
    return render_template('index.html', 
                           event_data=db_query(app, 'SELECT * FROM event_table'),
                           is_authenticated=flask_login.current_user.is_authenticated,
                           user=flask_login.current_user
                           )

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
        return '''
               <form action='register' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='text' name='first_name' id='first_name' placeholder='first name'/>
                <input type='text' name='last_name' id='last_name' placeholder='last name'/>
                <input type='text' name='medical_info' id='medical_info' placeholder='medical info'/>
                <input type='submit' name='submit'/>
               </form>
               '''
    sql = """
    INSERT INTO user_table (`email`, `password`, `first_name`, `last_name`, `medical_info`) 
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (flask.request.form['email'],
              flask.request.form['password'],
              flask.request.form['first_name'],
              flask.request.form['last_name'],
              flask.request.form['medical_info'])
    db_update(app, sql, values)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit'/>
               </form>
               '''

    email = flask.request.form['email']
    if email in users and flask.request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        return redirect(url_for('index'))

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for('index'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run()
