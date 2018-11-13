from flask import Flask, render_template
from flask import request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy 
from bcrypt import hashpw, gensalt

fle=open('db.properties')
property=fle.readlines()[2]
fle.close()

#reading DB properties from the file
app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = property
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

db=SQLAlchemy(app)

#user info table for the db
class Users(db.Model):
	__tablename__="users_info"
	id=db.Column('id', db.Integer, primary_key=True)
	username=db.Column('username', db.String(20), unique=True)
	email = db.Column('email', db.String(30))
	password = db.Column('password', db.String(100))

	def __init__(self, username, email, password):
		self.username=username
		self.email=email
		self.password=password

def convert(pas):
	pas=pas.encode()
	new_pas=hashpw(pas, gensalt())
	return new_pas

#Main Page for the site
@app.route("/")
def index():
	return render_template('index.html')

#Sign Up Page for the site
@app.route("/signup")
def signup():
	return render_template('signup.html')

#Sending data to the database 
@app.route('/register', methods=["POST"])
def register():
	username=request.form['username']
	email=request.form['email']
	password=request.form['password']
	new_pass=convert(password)
	sign=Users(username=username, email=email, password=new_pass)
	db.session.add(sign)
	db.session.commit()
	return redirect(url_for('home_page'))

#Validating a user for login
@app.route('/validate', methods=["POST"])
def validate():
	userName=request.form['username']
	password=request.form['password']
	pass1=Users.query.filter_by(username=userName).first()
	password=password.encode('utf-8')
	db_pass=pass1.password.encode()
	if hashpw(password, db_pass)==db_pass:
		return redirect(url_for('home_page'))
	else:
		return render_template('foff.html')


@app.route('/home')
def home_page():
	return render_template('home.html')

if __name__=="__main__":
	app.run(host="localhost", port=5003, debug=True)
