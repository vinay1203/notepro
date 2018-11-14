import os
from flask import Flask, render_template
from flask import request, redirect, url_for
from flask import session
from flask_sqlalchemy import SQLAlchemy 
from bcrypt import hashpw, gensalt

fle=open('db.properties')
property=fle.readlines()[2]
fle.close()

#reading DB properties from the file
app=Flask(__name__)
app.config['SECRET_KEY']='e5ac358c-f0bf-11e5-9e39-d3b532c10a28'
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
	session['user']=userName
	password=request.form['password']
	pass1=Users.query.filter_by(username=userName).first()
	if pass1==None:
		return render_template('foff.html')
	else:
		password=password.encode('utf-8')
		db_pass=pass1.password.encode()
		if hashpw(password, db_pass)==db_pass:
			return redirect(url_for('home_page'))
		else:
			return render_template('foff.html')

#Displaying the home page for the user.
#creating a directory "senotes" in the home folder of the user and stores files 
@app.route('/home')
def home_page():
	user=session.get('user')
	home=os.path.expanduser("~")
	os.chdir(home)
	if os.path.exists('senotes') and os.path.isdir('senotes'):
		os.chdir('senotes')
	else:
		os.mkdir('senotes')
		os.chdir('senotes')

	files=os.listdir()
	if len(files)==0:
		no_files="noem"
		return render_template('home.html', user=user, no_files=no_files)
	else:
		no_files="em"
		return render_template('home.html', user=user, no_files=no_files, files=files)

#Presents the user with a file where he can make changes
@app.route('/notes/', methods=["GET"])
def notes():
	fileName=""
	home=os.path.expanduser("~")+ "/senotes/"
	os.chdir(home)
	fle_name=request.args.get('file_name')
	user=session.get('user')
	fileName=home+fle_name+".txt"
	#open_file=open(fileName,'w')
	return render_template('notes.html', user=user, fle_name=fle_name)

#The textarea data is stored in the file as the user specifies
@app.route("/save_notes/<fileName>", methods=["POST"])
def save_notes(fileName):
	os.chdir(os.path.expanduser("~")+"/senotes/")
	content=request.form['content']
	open_fle= open(fileName, 'a')
	open_fle.write(content)
	open_fle.close()
	return render_template('saved_note.html')

if __name__=="__main__":
	app.run(host="localhost", port=5003, debug=True)
