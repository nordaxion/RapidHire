from flask import Flask, redirect, render_template, request, session, url_for, flash
from flask_session import Session
import sqlite3
from functools import wraps
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

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

db = sqlite3.connect('employment.db')
cursor = db.cursor()

@app.route("/")
def homepage():
    """Show the description of our web application"""

    # TODO
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
            with cursor:
                new_user_id = cursor.execute("INSERT INTO users (first_name, last_name, email, hash, user_type, company) VALUES (?, ?, ?, ?, ?, ?)", first_name, last_name, email, hash, user_type, company)
        except sqlite3.IntegrityError:
            return render_template("error.html", error="Account already exists.", code=400)

        cursor.execute("SELECT user_id FROM users WHERE email=?", email)
        session["user_id"] = cursor.fetchone()
        session["user_type"] = user_type

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
            with cursor:
                new_user_id = cursor.execute("INSERT INTO users (first_name, last_name, email, hash, user_type) VALUES (?, ?, ?, ?, ?)", first_name, last_name, email, hash, user_type)
        except sqlite3.IntegrityError:
            return render_template("error.html", error="Account already exists.", code=400)

        cursor.execute("SELECT user_id FROM users WHERE email=?", email)
        session["user_id"] = cursor.fetchone()
        session["user_type"] = user_type

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
def portal():
    """Shows the portal for employers"""

    #TODO
    return render_template("employer_portal.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for("index"))


