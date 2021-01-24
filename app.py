from flask import Flask, redirect, render_template, request, session, url_for, flash
from flask_session import Session
import sqlite3
from functools import wraps
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import *

app = Flask(__name__)


def login_required(f):
    """Used to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookes)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def homepage():
    """Show the description of our web application"""
    return render_template("homepage.html")


@app.route("/register_as_employer", methods=["GET", "POST"])
def register_as_employer():
    """Show the register page for employers"""

    # Submit via POST
    if request.method == "POST":

        # Ensure every information was submitted.
        if not request.form.get("first_name") and not request.form.get("last_name"):
            return render_template("error.html", error="Please enter your name.", code=400)

        elif not request.form.get("company"):
            return render_template("error.html", error="Please enter your company.", code=400)

        # Find a way to validate email TODO
        elif not request.form.get("email"):
            return render_template("error.html", error="Please enter your email.", code=400)

        elif not request.form.get("password"):
            return render_template("error.html", error="Please enter your password.", code=400)

        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("error.html", error="Passwords do not match.", code=400)
        
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        company = request.form.get("company")
        user_type = "employer"
        email = request.form.get("email")
        hash = generate_password_hash(request.form.get("password"))

        try:
            with sqlite3.connect("employment.db") as conn:
                cursor = conn.cursor()
                new_user_id = cursor.execute("INSERT INTO users (first_name, last_name, email, hash, user_type, company) VALUES (?, ?, ?, ?, ?, ?)", (first_name, last_name, email, hash, user_type, company))
        except sqlite3.IntegrityError:
            return render_template("error.html", error="Account already exists.", code=400)

        cursor.execute("SELECT user_id FROM users WHERE email=?", (email,))
        session["user_id"] = cursor.fetchone()
        session["user_type"] = user_type

        return redirect(url_for("portal"))

    else:
        return render_template("employer_register.html")


@app.route("/register_as_employee", methods=["GET", "POST"])
def register_as_employee():
    """Show the register page for potential employees"""

    # Submit via POST
    if request.method == "POST":

        # Ensure every information was submitted.
        if not request.form.get("first_name") and not request.form.get("last_name"):
            return render_template("error.html", error="Please enter your name.", code=400)

        # Find a way to validate email TODO
        elif not request.form.get("email"):
            return render_template("error.html", error="Please enter your email.", code=400)

        elif not request.form.get("password"):
            return render_template("error.html", error="Please enter your password.", code=400)

        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("error.html", error="Passwords do not match.", code=400)
        
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        user_type = "employee"
        email = request.form.get("email")
        hash = generate_password_hash(request.form.get("password"))

        try:
            with sqlite3.connect("employment.db") as conn:
                cursor = conn.cursor()
                new_user_id = cursor.execute("INSERT INTO users (first_name, last_name, email, hash, user_type) VALUES (?, ?, ?, ?, ?)", (first_name, last_name, email, hash, user_type))
        except sqlite3.IntegrityError:
            return render_template("error.html", error="Account already exists.", code=400)

        with sqlite3.connect("employment.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE email=?", email)
            session["user_id"] = cursor.fetchone()
            session["user_type"] = user_type
        
        return redirect(url_for("portal"))

    else:
        return render_template("employee_register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Shows the login page"""
    
    session.clear()

    if request.method == "POST":
        if not request.form.get("email"):
            return render_template("error.html", error="Please enter your email.", code=400)
        
        elif not request.form.get("password"):
            return render_template("error.html", error="Please enter your password.", code=400)

        # Query database for email
        with sqlite3.connect("employment.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email=?", request.form.get("email"))
            rows = cursor.fetchall()

        # Ensure username exist and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("error.html", error="Invalid username and/or password.", code=400)

        # Remember which user is logged in
        session["user_id"] = rows[0]["user_id"]
        session["user_type"] = rows[0]["user_type"]

        # Redirect the user to the portal
        return redirect(url_for(portal))
        
    else:
        return render_template("login.html")
    

@app.route("/portal")
@login_required
def portal():
    """Shows the portal for users"""

    # Checks which user_type the user is
    if session["user_type"] == "employer":
        
        # Get all potential employees list
        with sqlite3.connect("employment.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_type=employee")
            potential_employees_list = cursor.fetchall()
        
        # Get all postings created by the user
        with sqlite3.connect("employment.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM postings WHERE user_id=?", session["user_id"])
            user_postings = cursor.fetchall()

        # Filter distance to get matches
        matches = {}
        for posting in user_postings:
            possible_matches = filter_distance(posting[2], potential_employees_list, distance=posting[3])
            matches[posting] = possible_matches

        return render_template("employer_portal.html", matches=matches)

    else:
        return render_template("employee_portal.html")


@app.route("/add_postings", methods=["GET", "POST"])
@login_required
def add_postings():
    """Shows a form for adding new employer postings"""

    if request.method == "POST":
        if not request.form.get("job_name"):
            return render_template("error.html", error="Please enter a job name.", code=400)

        elif not request.form.get("location"):
            return render_template("error.html", error="Please enter a location.", code=400)

        elif not request.form.get("max_distance"):
            return render_template("error.html", error="Please enter a max distance.", code=400)

        elif not request.form.get("skills"):
            return render_template("error.html", error="Please enter the skills you are looking for.", code=400)

        elif not request.form.get("job_description"):
            return render_template("error.html", error="Please enter the job description.", code=400)

        job_name = request.form.get("job_name")
        location = request.form.get("location")
        max_distance = request.form.get("max_distance")
        skills = request.form.get("skills")
        job_description = request.form.get("job_description")

        cursor.execute("INSERT INTO postings (job_name, location, max_distance, skill, user_id, job_description) VALUES (?, ?, ?, ?, ?, ?)", (job_name, location, max_distance, skill, user_id, job_description))

    else:
        return render_template("add_postings.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for("index"))

