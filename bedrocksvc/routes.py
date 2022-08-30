import logging
from flask import url_for, render_template, flash, redirect, request, session
from flask_login import login_user, current_user, logout_user, login_required
from bedrocksvc import app, db, bcrypt, crypt, session_data, BDSServer
from bedrocksvc.models import User, Player, PlayerEvent
from bedrocksvc.forms import RegistrationForm, LoginForm

logger = logging.getLogger(__name__)

"""
TODO
"""

@app.route("/")
@login_required
def home():
	bdsstatus = BDSServer.is_running()
	return render_template("home.html", bdsstatus=bdsstatus)

@app.route("/register", methods=['GET', 'POST'])
def register():
	if len(User.query.all()) > 0:
		logger.info(f"Admin account already exists! Registration is disabled!")
		return redirect(url_for('login'))
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created!', 'success')
		logger.info(f"Account '{form.username.data}' has been created!")
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
	if len(User.query.all()) == 0:
		logger.info(f"No users exist, redirecting to first time admin registration.")
		return redirect(url_for('register'))
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			logger.info(f"'{form.email.data}' logged in!")
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			logger.info(f"Unsuccessful login attempt for '{form.email.data}'!")
			flash('Login Unsuccessful. Please check email and password.', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
	logger.info(f"User '{User.query.get(current_user.get_id())}' manually logged out.")
	logout_user()
	return redirect(url_for('login'))

# def shutdown_server():
# 	func = request.environ.get('werkzeug.server.shutdown')
# 	if func is None:
# 		raise RuntimeError('Not running with the Werkzeug Server')
# 	func()

@app.route("/startup")
@login_required
def startup():
	logger.info(f"User '{User.query.get(current_user.get_id())}' initiated startup.")
	BDSServer.start_server()
	flash('Bedrock server started!', 'success')
	return redirect(url_for('home'))

@app.route("/shutdown")
@login_required
def shutdown():
	logger.info(f"User '{User.query.get(current_user.get_id())}' initiated shutdown.")
	# func = request.environ.get('werkzeug.server.shutdown')
	# if func is None:
	# 	logger.error(f"Not running with the Werkzeug Server")
	# 	flash('Not running with the Werkzeug Server', 'danger')
	# 	return redirect(url_for('home'))
	# func()
	BDSServer.stop_server()
	flash('Bedrock server shutdown!', 'success')
	return redirect(url_for('home'))