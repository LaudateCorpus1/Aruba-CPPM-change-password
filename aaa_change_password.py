"""
Flask application to check the local user password and change it via API Calls
for Aruba Clearpass
Tim Cappalli's API script is used as a start point:
    https://github.com/aruba/clearpass-api-python-snippets
"""
# !/usr/bin/env python3
# Imports
# import sys
from datetime import datetime

# import urllib3
from flask import Flask, session, redirect, url_for, request, render_template

# Import class Сppm_Сonnect from file (classes.py)
from classes import Cppm_Connect
from common_functions import change_password
# Import universal functions from file (common_functions.py)
from common_functions import get_access_token
from common_functions import pg_sql

# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# main configuration parameters from files through class
cppm_connect_main = Cppm_Connect()

# Define status_code variable
cppm_connect_main.status_code = 0


def exp_days_f(cppm_class, current_user):
    """
    User's password expiration and check force change password function.
    1. Calculates days to expiry password for particular user
    2. Checks change password force checkbox.
        Returns:
            exp_days: Number of days until a password expired
            change_pwd_next_login: status for force change password checkbox (boolean)
    """
    now = datetime.now()
    # Get User ID, date of password changing and user attributes
    uid, pwd_dt, attr, change_pwd_next_login = pg_sql('user', cppm_class,
                                                      current_user)
    #    print (cppm_class.db_password, current_user)
    exp_days = int(cppm_connect_main.days_to_passw_exp) - (now - pwd_dt).days
    #    print(exp_days, change_pwd_next_login)
    return exp_days, change_pwd_next_login


app = Flask(__name__)
app.secret_key = 'b_5#y2L"F4Q8z\n\xec]/'  # Use function ?!


@app.route('/')
def index():
    """
    Start page function based on template (templates/index.html)
    Returns:
        Web start page
    """
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page function based on template (templates/login.html)
        Asks user to input username and password
        Checks entered credentials
        Returns:
            1. Login page
            2. Rebuild Login page in case of an issue or incorrect credentials
               with status message
            3. Redirect to logged in page (Function logged_in)
    """
    # Kill function's parameters
    #    global status_code уже нет
    cppm_connect_main.status_code = 0
    get_access_type = 'login'
    session['username'] = None
    session['password'] = None
    # Get username and password
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        # Access token function call for local user verification
        try:
            token_response, cppm_connect_main.status_code = get_access_token(
                cppm_connect_main, session['username'], session['password'],
                get_access_type)
            # kill request.method
        #            request.method = None
        #            print ('main login status_code' , status_code)
        # Check status for user verification
        except Exception as login_page_exception:
            print('Page Login Exception', login_page_exception)
            login_message = 'Something went wrong, please reenter your login and password'
            return render_template('login.html', login_message=login_message)

        if cppm_connect_main.status_code == 200:
            print('main login status_code-2', cppm_connect_main.status_code)
            # Delete password from memory
            session.pop('password', None)
            return redirect(url_for('logged_in'))
        # Rewrite /login page with password warning
        login_message = 'User or password are incorrect'
        return render_template('login.html', login_message=login_message)

    #   Start /login page
    login_message = 'Please enter your your username and password'
    return render_template('login.html', login_message=login_message,
                           title='Log in')


@app.route('/change_password_page', methods=['GET', 'POST'])
def change_password_page():
    """
    Change password page function page based on template
    Asks user to input new password
        Checks entered passwords
        Returns:
            1. Change password page
            2. Rebuilt change password page in the case of an issue
               or entered incorrect password's pair (shows why incorrect)
            3. Redirect to logged in page (Function logged_in)
    """
    if cppm_connect_main.status_code != 200:
        return redirect(url_for('login'))
    if session['username'] is not None:
        # Kill function's parameters
        session['patch_user_code'] = 0
        patch_user_status = None
        #        print (patch_user_code)
        session['new_password1'] = None
        session['new_password2'] = None
        # Get new password
        if request.method == 'POST':
            session['new_password1'] = request.form['new_password1']
            session['new_password2'] = request.form['new_password2']
            # Basic password verification
            if session['new_password1'] != session['new_password2']:
                cp_message = 'Passwords don\'t match'
                return render_template('change_password_page.html',
                                       cp_message=cp_message,
                                       title='Change Password',
                                       username=session['username'])
            try:
                patch_user_status, session[
                    'patch_user_code'] = change_password(cppm_connect_main,
                                                         session['username'],
                                                         session[
                                                             'new_password1'])
                # If change password is successful redirect to logged_in App
                if session['patch_user_code'] == 200:
                    return redirect(url_for('logged_in'))
                    # Else show "whats wrong" and try again
                #                    elif patch_user_code != 200:
                cp_message = str(patch_user_status)
                return render_template('change_password_page.html',
                                       cp_message=cp_message,
                                       title='Change Password',
                                       username=session['username'])
            except Exception as page_change_pwd_exception:
                print('Page CP Exception-2', page_change_pwd_exception)
                cp_message = 'Something went wrong, please reenter your new password'
                return render_template('change_password_page.html',
                                       cp_message=cp_message,
                                       title='Change Password',
                                       username=session['username'])
    # Start /change_password_page
    cp_message = 'Please enter your new password'
    return render_template('change_password_page.html', cp_message=cp_message,
                           title='Change Password',
                           username=session['username'])


@app.route('/logout')
def logout():
    """
    Logout page function
    Clears username information and redirects to start page
       Returns:
           Redirect to start page (Function index)
    """
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))


# Application for logged in page
@app.route('/logged_in')
def logged_in():
    """
    Logged_in page function based on template (templates/logged_in.html)
    Shows days to password expiration for particular user
     Returns:
         Redirect to change password page in case of Change password flag
         Logged_in page with password expiration message
    """
    exp_days, change_pwd_next_login = exp_days_f(cppm_connect_main,
                                                 session['username'])
    if change_pwd_next_login:
        return redirect(url_for('change_password_page'))
    if exp_days <= 0:
        exp_message = 'Your password is already expired according to internal policy'
    elif session.get('patch_user_code') == 200:
        exp_message = f'Password changed successfully. It expires in {exp_days} days'
        session.pop('patch_user_code', None)
    else:
        exp_message = f'Your password expires in {exp_days} days'
    return render_template('logged_in.html', username=session['username'],
                           status_code=cppm_connect_main.status_code,
                           title='Logged_in', exp_message=exp_message)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
