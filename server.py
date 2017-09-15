import re, os, binascii, md5
from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import MySQLConnector
LETTER_REGEX = re.compile(r"^[a-zA-Z]+$")
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$")
app = Flask(__name__)
mysql = MySQLConnector(app, 'walldb')
app.secret_key = "This1sMykeyth3r34r3manylik31t7432557"

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
	pass

@app.route("/register", methods=["POST"])
def register():
	valid = True
	if len(request.form["first_name"]) < 3:
		flash("First name cannot be fewer than 2 characters.")
		valid = False
	elif not LETTER_REGEX.match(request.form["first_name"]):
		flash("First name cannot contain numbers.")
		valid = False
	if len(request.form["last_name"]) < 3:
		flash("Last name cannot be fewer than 2 characters.")
		valid = False
	elif not LETTER_REGEX.match(request.form["last_name"]):
		flash("Last name cannot contain numbers.")
		valid = False
	if not EMAIL_REGEX.match(request.form["email"]):
		flash("Must enter a valid email address.")
		valid = False
	if len(request.form["password"]) < 8:
		flash("Password must be at least 8 characters.")
		valid = False
	if not request.form["password"] == request.form["password_confirm"]:
		flash("Password and confirmation do not match.")
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
		mysql.query_db(query, data)
		return redirect("/")
	else:
		return redirect("/")


app.run(debug=True)