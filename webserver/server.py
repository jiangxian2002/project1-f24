#!/usr/bin/env python3

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, jsonify, session, url_for
from database import runq, engine
from flask_session import Session
from flask_bcrypt import Bcrypt
from helpers import apology, login_required
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
def index():
    # Fetch all columns for each musical
    cursor = g.conn.execute(text("""
        SELECT * 
        FROM musicals
    """)).mappings()
    
    # Organize data as a list of dictionaries for easy access in the template
    musicals = [
        {
            'musical_id': row['musical_id'],
            'title': row['title'],
            'description': row['description'],
            'opening_date': row['opening_date'],
            'closing_date': row['closing_date'],
            'official_website': row['official_website'],
            'city': row['city']
        }
        for row in cursor
    ]
    
    cursor.close()
    return render_template("home.html", musicals=musicals)

@app.route('/search', methods=['GET', 'POST'])
def search():
    search_entry_ori = request.args.get('search-entry', '')
    search_entry = search_entry_ori.lower()
    print("getting a search entry")
    print(search_entry)

    musicals = []
    if search_entry:
        cursor = g.conn.execute(text("""
            SELECT * 
            FROM musicals
            WHERE LOWER(title) LIKE :search_entry
        """), {'search_entry': f"%{search_entry}%"}).mappings()
        
        musicals = [
            {
                'musical_id': row['musical_id'],
                'title': row['title'],
                'description': row['description'],
                'opening_date': row['opening_date'],
                'closing_date': row['closing_date'],
                'official_website': row['official_website'],
                'city': row['city']
            }
            for row in cursor
        ]
        cursor.close()
    return render_template('home.html', musicals=musicals, search_entry=search_entry_ori)


@app.route('/broadway_show', methods=['GET', 'POST'])
def view_broadway_show():
    musical_id = request.args.get("id")
    user_id = session.get('user_id')

    if not musical_id:
        return apology("Musical ID is required", 400)

    # Retrieve the musical data
    musical = g.conn.execute(text("""
        SELECT * FROM musicals WHERE musical_id = :musical_id
    """), {'musical_id': musical_id}).mappings().fetchone()

    if not musical:
        return apology("Musical not found", 404)
    
    # Check if the user added this musical to the wishlist
    in_wishlist = False
    if user_id:
        wishlist_entry = g.conn.execute(text("""
            SELECT 1 FROM wishlist WHERE musical_id = :musical_id AND user_id = :user_id
        """), {'musical_id': musical_id, 'user_id': user_id}).fetchone()
        in_wishlist = wishlist_entry is not None

    # Retrieve showtimes, cast, comments, and theatres
    showtimes = g.conn.execute(text("SELECT * FROM showtimes WHERE musical_id = :musical_id"),
                               {'musical_id': musical_id}).mappings().fetchall()
    
    cast_members = g.conn.execute(text("""
        SELECT * FROM cast_members cm JOIN participated p ON cm.actor_id = p.actor_id
        WHERE p.musical_id = :musical_id
    """), {'musical_id': musical_id}).mappings().fetchall()
    
    comments = g.conn.execute(text("""
        SELECT * FROM comments c JOIN users u ON c.user_id = u.user_id
        WHERE c.musical_id = :musical_id ORDER BY c.date_time DESC
    """), {'musical_id': musical_id}).mappings().fetchall()
    
    theatres = g.conn.execute(text("""
        SELECT * FROM theatres t JOIN showing_at sa ON t.theatre_id = sa.theatre_id
        WHERE sa.musical_id = :musical_id
    """), {'musical_id': musical_id}).mappings().fetchall()

    # Check watched showtimes for the user
    watched_showtimes = set()
    if user_id:
        watched_showtimes = g.conn.execute(text("""
            SELECT showtime_id FROM watched WHERE user_id = :user_id AND musical_id = :musical_id
        """), {'user_id': user_id, 'musical_id': musical_id}).mappings().fetchall()
        watched_showtimes = {row['showtime_id'] for row in watched_showtimes}

    # Render template with all data
    return render_template('broadway_show.html', musical=musical, showtimes=showtimes,
                           cast_members=cast_members, comments=comments, theatres=theatres,
                           in_wishlist=in_wishlist, watched_showtimes=watched_showtimes)

@app.route('/add_comment', methods=['POST'])
@login_required
def add_comment():
    user_id = session["user_id"]
    musical_id = request.form.get("musical_id")
    comment_text = request.form.get("comment")
    try:
        g.conn.execute(text("""
            INSERT INTO comments (user_id, musical_id, comment, date_time)
            VALUES (:user_id, :musical_id, :comment, NOW())
        """), {
            'user_id': user_id,
            'musical_id': musical_id,
            'comment': comment_text
        })
        g.conn.commit()
    except Exception as e:
        print(e)
        return apology("Failed to add comment", 500)

    # Redirect back to the musical page
    return redirect('/broadway_show?id=' + musical_id)

@app.route('/add_to_watched', methods=['POST'])
@login_required
def add_to_watched():
    user_id = session["user_id"]
    musical_id = request.form.get("musical_id")
    showtime_id = request.form.get("showtime_id")
    notes = request.form.get("notes")  # Optional notes

    # Insert into the watched table
    try:
        g.conn.execute(text("""
            INSERT INTO watched (user_id, musical_id, showtime_id, notes)
            VALUES (:user_id, :musical_id, :showtime_id, :notes)
        """), {
            'user_id': user_id,
            'musical_id': musical_id,
            'showtime_id': showtime_id,
            'notes': notes
        })
        g.conn.commit()
    except Exception as e:
        print(e)
        return apology("Failed to add to watched list", 500)

    # Redirect back to the musical page after adding
    return redirect(url_for('view_broadway_show', id=musical_id))

@app.route('/remove_from_watched', methods=['POST'])
@login_required
def remove_from_watched():
    user_id = session["user_id"]
    musical_id = request.form.get("musical_id")
    showtime_id = request.form.get("showtime_id")

    try:
        g.conn.execute(text("""
            DELETE FROM watched
            WHERE user_id = :user_id AND musical_id = :musical_id AND showtime_id = :showtime_id
        """), {
            'user_id': user_id,
            'musical_id': musical_id,
            'showtime_id': showtime_id
        })
        g.conn.commit()
    except Exception as e:
        print(e)
        return apology("Failed to remove from watched list", 500)

    return redirect(url_for('view_broadway_show', id=musical_id))

@app.route('/theatre', methods=['GET'])
def view_theatre():
    # Get the theatre_id from the query string (URL parameter)
    theatre_id = request.args.get("theatre_id")

    if not theatre_id:
        return apology("Theatre ID is required", 400)

    # Retrieve theatre details
    theatre = g.conn.execute(text("""
        SELECT *
        FROM theatres
        WHERE theatre_id = :theatre_id
    """), {'theatre_id': theatre_id}).mappings().fetchone()

    if not theatre:
        return apology("Theatre not found", 404)

    # Retrieve musicals shown at the theatre with their respective dates
    musicals = g.conn.execute(text("""
        SELECT m.musical_id, m.title, sa.start_date, sa.end_date
        FROM musicals m
        JOIN showing_at sa ON m.musical_id = sa.musical_id
        WHERE sa.theatre_id = :theatre_id
        ORDER BY sa.start_date DESC
    """), {'theatre_id': theatre_id}).mappings().fetchall()

    # Render the template and pass the theatre and musicals data
    return render_template('theatre.html', theatre=theatre, musicals=musicals)

@app.route('/cast_member', methods=['GET'])
def view_cast_member():
    # Get the actor_id from the query string (URL parameter)
    actor_id = request.args.get("actor_id")

    if not actor_id:
        return apology("Actor ID is required", 400)

    # Retrieve cast member details
    cast_member = g.conn.execute(text("""
        SELECT *
        FROM cast_members
        WHERE actor_id = :actor_id
    """), {'actor_id': actor_id}).mappings().fetchone()

    if not cast_member:
        return apology("Cast member not found", 404)

    # Retrieve musicals in which the cast member has participated with their respective dates
    musicals = g.conn.execute(text("""
        SELECT *
        FROM musicals m
        JOIN participated p ON m.musical_id = p.musical_id
        WHERE p.actor_id = :actor_id
        ORDER BY p.start_date DESC
    """), {'actor_id': actor_id}).mappings().fetchall()

    # Render the template and pass the cast member and musicals data
    return render_template('cast_member.html', cast_member=cast_member, musicals=musicals)


@app.route('/user/<int:user_id>')
@login_required
def view_user(user_id):
    # Query user details based on user_id
    user_query = text("""
        SELECT username, email, bio, city 
        FROM users 
        WHERE user_id = :user_id
    """)
    user = g.conn.execute(user_query, {'user_id': user_id}).fetchone()

    if not user:
        return apology("User not found", 404)

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

    return render_template('view_user.html', user=user, 
                           followers_count=followers_count, followed_count=followed_count)


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

@app.route('/manage_social', methods=['GET'])
@login_required
def manage_social():
    user_id = session['user_id']

    # Query to retrieve users whom the current user is not following
    users_to_follow = g.conn.execute(text("""
        SELECT u.user_id, u.username, u.bio
        FROM users u
        WHERE u.user_id != :user_id
        AND u.user_id NOT IN (
            SELECT followed_id
            FROM follows
            WHERE follower_id = :user_id
        )
    """), {'user_id': user_id}).mappings().fetchall()
    
    # Query to retrieve users whom the current user is following
    users_followed = g.conn.execute(text("""
        SELECT u.user_id, u.username, u.bio
        FROM users u
        JOIN follows f ON u.user_id = f.followed_id
        WHERE f.follower_id = :user_id
    """), {'user_id': user_id}).mappings().fetchall()

    # Query to retrieve users following the current user
    users_followers = g.conn.execute(text("""
        SELECT u.user_id, u.username, u.bio
        FROM users u
        JOIN follows f ON u.user_id = f.follower_id
        WHERE f.followed_id = :user_id
    """), {'user_id': user_id}).mappings().fetchall()

    return render_template('manage_social.html', users_followed=users_followed, users_to_follow=users_to_follow, users_followers=users_followers)

@app.route('/follow', methods=['POST'])
@login_required
def follow():
    user_id = session['user_id']
    followed_id = request.form.get("followed_id")

    if not followed_id:
        return apology("User to follow not specified", 400)

    # Insert a new follow relationship into the follows table
    try:
        g.conn.execute(text("""
            INSERT INTO follows (follower_id, followed_id)
            VALUES (:follower_id, :followed_id)
        """), {'follower_id': user_id, 'followed_id': followed_id})
        g.conn.commit()
    except Exception as e:
        print(e)
        return apology("Failed to add follow", 500)

    return redirect('/manage_social')

@app.route('/unfollow', methods=['POST'])
@login_required
def unfollow():
    user_id = session['user_id']
    unfollowed_id = request.form.get("unfollowed_id")

    if not unfollowed_id:
        return apology("User to unfollow not specified", 400)

    # Remove the follow relationship from the follows table
    try:
        g.conn.execute(text("""
            DELETE FROM follows
            WHERE follower_id = :follower_id AND followed_id = :unfollowed_id
        """), {'follower_id': user_id, 'unfollowed_id': unfollowed_id})
        g.conn.commit()
    except Exception as e:
        print(e)
        return apology("Failed to remove follow", 500)

    return redirect('/manage_social')

@app.route('/remove_follow', methods=['POST'])
@login_required
def remove_follow():
    user_id = session['user_id']
    follower_id = request.form.get("follower_id")

    if not follower_id:
        return apology("Follower not specified", 400)

    # Remove the follow relationship where the specified user follows the current user
    try:
        g.conn.execute(text("""
            DELETE FROM follows
            WHERE follower_id = :follower_id AND followed_id = :user_id
        """), {'follower_id': follower_id, 'user_id': user_id})
        g.conn.commit()
    except Exception as e:
        print(e)
        return apology("Failed to remove follower", 500)

    return redirect('/manage_social')


@app.route('/manage_showtimes', methods=['GET'])
@login_required
def manage_showtimes():
    user_id = session['user_id']

    # Query to retrieve all musicals the user has watched
    watched_musicals = g.conn.execute(text("""
        SELECT DISTINCT m.musical_id, m.title
        FROM watched w
        JOIN musicals m ON w.musical_id = m.musical_id
        WHERE w.user_id = :user_id
        ORDER BY m.title
    """), {'user_id': user_id}).mappings().fetchall()

    # Dictionary to store showtimes grouped by musical_id
    watched_musicals_showtimes = {}
    for musical in watched_musicals:
        musical_id = musical["musical_id"]
        showtimes = g.conn.execute(text("""
            SELECT s.date, s.start_time, w.notes, w.showtime_id, m.title
            FROM watched w
            JOIN showtimes s ON w.showtime_id = s.showtime_id AND w.musical_id = s.musical_id
            JOIN musicals m ON w.musical_id = m.musical_id
            WHERE w.user_id = :user_id AND w.musical_id = :musical_id
            ORDER BY s.date ASC, s.start_time ASC
        """), {'user_id': user_id, 'musical_id': musical_id}).mappings().fetchall()
        
        # Store the showtimes for each musical
        watched_musicals_showtimes[musical_id] = showtimes
        
    return render_template('manage_showtimes.html', watched_musicals=watched_musicals, watched_musicals_showtimes=watched_musicals_showtimes)

@app.route('/update_notes', methods=['POST'])
@login_required
def update_notes():
    user_id = session["user_id"]
    musical_id = request.form.get("musical_id")
    showtime_id = request.form.get("showtime_id")
    notes = request.form.get("notes")
    try:
        g.conn.execute(text("""
            UPDATE watched
            SET notes = :notes
            WHERE user_id = :user_id AND musical_id = :musical_id AND showtime_id = :showtime_id
        """), {
            'notes': notes,
            'user_id': user_id,
            'musical_id': musical_id,
            'showtime_id': showtime_id
        })
        g.conn.commit()
    except Exception as e:
        print(e)
        return apology("Failed to update notes", 500)

    return redirect(url_for('manage_showtimes'))

@app.route('/manage_wishlist', methods=['GET'])
@login_required
def manage_wishlist():
    user_id = session['user_id']

    # Query to retrieve shows in the user's wishlist
    wishlist_shows = g.conn.execute(text("""
        SELECT m.musical_id, m.title, m.description, m.opening_date, m.closing_date
        FROM musicals m
        JOIN wishlist w ON m.musical_id = w.musical_id
        WHERE w.user_id = :user_id
    """), {'user_id': user_id}).mappings().fetchall()

        # Query to retrieve friends with common wishlisted musicals and watch status
    common_wishlist_query = text("""
        WITH bidirectional_friends AS (
            SELECT f1.follower_id AS user_id, f1.followed_id AS friend_id
            FROM follows f1
            JOIN follows f2
              ON f1.follower_id = f2.followed_id
              AND f1.followed_id = f2.follower_id
        ),
        wishlisted_musicals AS (
            SELECT DISTINCT user_id, musical_id
            FROM wishlist
        ),
        watched_musicals AS (
            SELECT DISTINCT user_id, musical_id
            FROM watched
        )
        SELECT wm1.musical_id, u2.username AS friend, 
               CASE WHEN wm2_watched.musical_id IS NOT NULL THEN 'Watched' ELSE 'Not Watched' END AS watched_status
        FROM bidirectional_friends bf
        JOIN wishlisted_musicals wm1
          ON bf.user_id = wm1.user_id
        JOIN wishlisted_musicals wm2
          ON bf.friend_id = wm2.user_id AND wm1.musical_id = wm2.musical_id
        LEFT JOIN watched_musicals wm2_watched
          ON wm2.user_id = wm2_watched.user_id AND wm2.musical_id = wm2_watched.musical_id
        JOIN users u2 ON bf.friend_id = u2.user_id
        WHERE bf.user_id = :user_id
        ORDER BY wm1.musical_id, u2.username;
    """)

    common_wishlist = g.conn.execute(common_wishlist_query, {'user_id': user_id}).mappings().fetchall()

    # Group the common wishlist by musical_id
    from collections import defaultdict
    common_wishlist_by_musical = defaultdict(list)
    for entry in common_wishlist:
        common_wishlist_by_musical[entry['musical_id']].append({
            'friend': entry['friend'],
            'watched_status': entry['watched_status']
        })

    recommendation_query = text("""
        WITH bidirectional_friends AS (
            SELECT DISTINCT f1.follower_id AS user_id, f1.followed_id AS friend_id
            FROM follows f1
            JOIN follows f2
              ON f1.follower_id = f2.followed_id
              AND f1.followed_id = f2.follower_id
        ),
        friends_watched_multiple AS (
            SELECT wm.user_id AS friend_id, wm.musical_id, COUNT(*) AS watch_count
            FROM watched wm
            JOIN bidirectional_friends bf ON wm.user_id = bf.friend_id
            GROUP BY wm.user_id, wm.musical_id
            HAVING COUNT(*) > 1
        ),
        recommended_musicals AS (
            SELECT DISTINCT bf.user_id, fwm.friend_id, fwm.musical_id, m.title AS musical_title, m.city, m.opening_date, m.closing_date, m.description
            FROM friends_watched_multiple fwm
            JOIN bidirectional_friends bf ON fwm.friend_id = bf.friend_id
            JOIN musicals m ON fwm.musical_id = m.musical_id
            WHERE NOT EXISTS (
              SELECT 1
              FROM wishlist w
              WHERE w.user_id = bf.user_id
                AND w.musical_id = fwm.musical_id
              UNION
              SELECT 1
              FROM watched ww
              WHERE ww.user_id = bf.user_id
                AND ww.musical_id = fwm.musical_id
            )
        )
        SELECT DISTINCT rm.musical_title, rm.musical_id, rm.city, rm.opening_date, rm.closing_date, rm.description
        FROM recommended_musicals rm
        WHERE rm.user_id = :user_id
        ORDER BY rm.musical_title;
    """)

    recommendations = g.conn.execute(recommendation_query, {'user_id': user_id}).mappings().fetchall()

    return render_template(
        'manage_wishlist.html',
        wishlist_shows=wishlist_shows,
        common_wishlist_by_musical=common_wishlist_by_musical,
        recommendations=recommendations
    )

@app.route('/add_to_wishlist', methods=['POST'])
@login_required
def add_to_wishlist():
    user_id = session['user_id']
    musical_id = request.form.get("musical_id")

    if not musical_id:
        return apology("Show ID is required", 400)

    try:
        g.conn.execute(text("""
            INSERT INTO wishlist (user_id, musical_id)
            VALUES (:user_id, :musical_id)
        """), {'user_id': user_id, 'musical_id': musical_id})
        g.conn.commit()
    except Exception as e:
        print(e)
        return apology("Failed to add to wishlist", 500)

    return redirect('/manage_wishlist')

@app.route('/remove_from_wishlist', methods=['POST'])
@login_required
def remove_from_wishlist():
    user_id = session['user_id']
    musical_id = request.form.get("musical_id")

    if not musical_id:
        return apology("Show ID is required", 400)

    try:
        g.conn.execute(text("""
            DELETE FROM wishlist
            WHERE user_id = :user_id AND musical_id = :musical_id
        """), {'user_id': user_id, 'musical_id': musical_id})
        g.conn.commit()
    except Exception as e:
        print(e)
        return apology("Failed to remove from wishlist", 500)

    return redirect('/manage_wishlist')


@app.route('/update_bio', methods=['POST'])
@login_required
def update_bio():
    user_id = session['user_id']
    new_bio = request.form.get('bio')

    print("new value is")

    if new_bio is None:
        return apology("No bio provided", 400)

    # Update the bio in the database
    update_bio_query = text("""
        UPDATE users 
        SET bio = :new_bio 
        WHERE user_id = :user_id
    """)
    g.conn.execute(update_bio_query, {'new_bio': new_bio, 'user_id': user_id})
    g.conn.commit()

    return redirect("/account")

@app.route('/update_city', methods=['POST'])
@login_required
def update_city():
    user_id = session['user_id']
    new_city = request.form.get('city')

    if new_city is None:
        return apology("No city provided", 400)

    # Update the bio in the database
    update_city_query = text("""
        UPDATE users 
        SET city = :new_city
        WHERE user_id = :user_id
    """)
    g.conn.execute(update_city_query, {'new_city': new_city, 'user_id': user_id})
    g.conn.commit()

    return redirect("/account")


@app.route('/user/followers')
@login_required
def view_followers():
    user_id = session['user_id']
    # Query to fetch followers of the given user
    query = text("""
        SELECT u.user_id, u.username, u.bio, u.city
        FROM follows f
        JOIN users u ON f.follower_id = u.user_id
        WHERE f.followed_id = :user_id
    """)
    followers = g.conn.execute(query, {'user_id': user_id}).fetchall()

    # Render the followers page with the followers list
    return render_template('followers.html', followers=followers)

@app.route('/user/following')
@login_required
def view_following():
    user_id = session['user_id']
    # Query to fetch users that the given user is following
    query = text("""
        SELECT u.user_id, u.username, u.bio, u.city
        FROM follows f
        JOIN users u ON f.followed_id = u.user_id
        WHERE f.follower_id = :user_id
    """)
    following = g.conn.execute(query, {'user_id': user_id}).fetchall()

    # Render the following page with the following list
    return render_template('following.html', following=following)


### Login and Register routes
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
