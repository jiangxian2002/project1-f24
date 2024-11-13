#!/usr/bin/env python3

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, jsonify, session
from database import runq, engine
from flask_session import Session
from flask_bcrypt import Bcrypt
from helpers import apology, login_required
from werkzeug.utils import secure_filename
import uuid as uuid

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
bcrypt = Bcrypt(app)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
@login_required
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)

  cursor = g.conn.execute(text("SELECT title FROM musicals"))
  names = [row[0] for row in cursor] 
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("home.html", **context)

@app.route('/account')
@login_required
def account():
    user_id = session['user_id']

    # Query user details
    user_query = text("""
        SELECT username, email, bio, city 
        FROM users 
        WHERE user_id = :user_id
    """)
    user = g.conn.execute(user_query, {'user_id': user_id}).fetchone()

    if not user:
        return apology("User not found")

    # Query follower count
    followers_count_query = text("""
        SELECT COUNT(*) 
        FROM follows 
        WHERE followed_id = :user_id
    """)
    followers_count = g.conn.execute(followers_count_query, {'user_id': user_id}).scalar()

    # Query followed count
    followed_count_query = text("""
        SELECT COUNT(*) 
        FROM follows 
        WHERE follower_id = :user_id
    """)
    followed_count = g.conn.execute(followed_count_query, {'user_id': user_id}).scalar()

    # Render the account page with the retrieved data
    return render_template('account.html', user=user, 
                           followers_count=followers_count, followed_count=followed_count)

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name')
    print(name)
    if name:
        cmd = 'INSERT INTO test(name) VALUES (:name)'
        g.conn.execute(text(cmd), {'name': name})
        g.conn.commit()
    return redirect('/')


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email:
            return apology("Missing email", 404)
        if not password:
            return apology("Missing password", 404)
        
        user = g.conn.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email}).mappings().fetchone()
        if not user:
            return apology("No such user", 404)
        
        if not bcrypt.check_password_hash(user['passwordhash'], password):
            return apology("Wrong password", 404)

        # Log the user in
        session['user_id'] = user['user_id']
        return redirect("/")

    else: 
        return render_template('login.html')
    
@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("Missing username", 404)
        if not email:
            return apology("Missing email", 404)
        if not password:
            return apology("Missing password", 404)
        if not confirmation:
            return apology("Missing password confirmation", 404)
        if password != confirmation:
            return apology("Passwords do not match", 404)

        user_check = g.conn.execute(text("SELECT * FROM users WHERE username = :username"), 
                                    {"username": username}).fetchone()
        if user_check:
            return apology("Username taken. Please choose something else.", 404)
            
        user_check = g.conn.execute(text("SELECT * FROM users WHERE email = :email"), 
                                    {"email": email}).fetchone()
        if user_check:
            return apology("Account already created with email. Please log in.", 404)
        
        # Hash the password and insert the new user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        g.conn.execute(text("""
            INSERT INTO users (username, email, passwordhash)
            VALUES (:username, :email, :passwordhash)
        """), {"username": username, "email": email, "passwordhash": hashed_password})
        g.conn.commit()
        return redirect("/")
    else: 
        return render_template('register.html')

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
