import re, os, binascii, md5
from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import MySQLConnector
NAME_REGEX = re.compile(r"^[-a-zA-Z']+$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$")
app = Flask(__name__)
mysql = MySQLConnector(app, 'walldb')
app.secret_key = "This1sMykeyth3r34r3manylik31t7432557"

@app.route("/")
def index():
	if "id" in session:
		return redirect("/wall")
	else:
		return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
	valid = True
	if not EMAIL_REGEX.match(request.form["email"]):
		flash("Must enter a valid email address.", "login")
		valid = False
	if len(request.form["password"]) < 8:
		flash("Must enter a valid password.", "login")
		valid = False
	if valid:
		query = "SELECT id, password, salt FROM users WHERE email = :email"
		data = {
			"email": request.form["email"]
		}
		login_info = mysql.query_db(query,data)
		if login_info == []:
			flash("Invalid email or password.", "login")
			return redirect("/")
		elif md5.new(request.form["password"]+login_info[0]["salt"]).hexdigest() == login_info[0]["password"]:
			session["id"] = login_info[0]["id"]
			return redirect("/wall")
	else:
		return redirect("/")

@app.route("/register", methods=["POST"])
def register():
	valid = True
	if len(request.form["first_name"]) < 2:
		flash("First name cannot be fewer than 2 characters.", "register")
		valid = False
	elif not NAME_REGEX.match(request.form["first_name"]):
		flash("First name cannot contain numbers.", "register")
		valid = False
	if len(request.form["last_name"]) < 2:
		flash("Last name cannot be fewer than 2 characters.", "register")
		valid = False
	elif not NAME_REGEX.match(request.form["last_name"]):
		flash("Last name cannot contain numbers.", "register")
		valid = False
	if not EMAIL_REGEX.match(request.form["email"]):
		flash("Must enter a valid email address.", "register")
		valid = False
	else:
		query = "SELECT email FROM users WHERE email = :email"
		data = {"email":request.form["email"]}
		if mysql.query_db(query, data) != []:
			flash("An account with that email address already exists.", "register")
			valid = False
	if len(request.form["password"]) < 8:
		flash("Password must be at least 8 characters.", "register")
		valid = False
	if not request.form["password"] == request.form["password_confirm"]:
		flash("Password and confirmation do not match.", "register")
		valid = False
	if valid:
		salt = binascii.b2a_hex(os.urandom(15))
		hashed_pw = md5.new(request.form["password"] + salt).hexdigest()

		query = "INSERT INTO users (first_name, last_name, email, password, salt, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, :salt, NOW(), NOW())"
		data = {
			"first_name": request.form["first_name"],
			"last_name": request.form["last_name"],
			"email": request.form["email"],
			"password": hashed_pw,
			"salt": salt
		}
		session["id"] = mysql.query_db(query, data)
		return redirect("/wall")
	else:
		return redirect("/")

@app.route("/wall")
def wall():
	query = "SELECT first_name FROM users WHERE id = :id"
	data = {
		"id": session["id"]
	}
	logged_user = mysql.query_db(query,data)
	first_name = logged_user[0]["first_name"]

	query = "SELECT users.id, CONCAT_WS(' ', users.first_name, users.last_name) AS author, messages.id, messages.message, DATE_FORMAT(messages.created_at, '%M %D, %Y %l:%i %p') AS post_time FROM users JOIN messages ON users.id = messages.user_id ORDER BY messages.created_at DESC"
	all_messages = mysql.query_db(query)

	return render_template("wall.html", first_name=first_name, all_messages=all_messages)

@app.route("/post_message", methods=["POST"])
def post_message():
	query = "INSERT INTO messages (user_id, message, created_at, updated_at) VALUES (:user_id, :message, NOW(), NOW())"
	data = {
		"user_id": session["id"],
		"message": request.form["message"]
	}
	mysql.query_db(query, data)
	return redirect("/wall")

@app.route("/logout", methods=["POST"])
def logout():
	session.pop("id")
	return redirect("/")

app.run(debug=True)