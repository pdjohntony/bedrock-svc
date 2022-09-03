import logging
from flask import url_for, render_template, flash, redirect, request, session
from flask_login import login_user, current_user, logout_user, login_required
from bedrocksvc import app, db, bcrypt, crypt, session_data, BDSServer
from bedrocksvc.models import User, Player, PlayerEvent, DiscordWebhook
from bedrocksvc.forms import RegistrationForm, LoginForm, DiscordWebhookForm

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
	else:
		for field, error in form.errors.items():
			logger.error(f"Form invalid: {field.capitalize()}: {error}")
			flash(f'{field.capitalize()}: {error[0]}', 'danger')
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

@app.route("/discordwebhook", methods=['GET', 'POST'])
@login_required
def discord_webhooks():
	webhooks = DiscordWebhook.query.all()
	form     = DiscordWebhookForm()

	if form.validate_on_submit():
		new_webhook = DiscordWebhook(
			name                        = form.name.data,
			webhook                     = form.webhook.data,
			enabled                     = form.enabled.data,
			announce_player_connect     = form.announce_player_connect.data,
			announce_player_disconnect  = form.announce_player_disconnect.data,
			announce_player_buffer_time = form.announce_player_buffer_time.data,
			announce_server_start       = form.announce_server_start.data,
			announce_server_shutdown    = form.announce_server_shutdown.data,
			announce_update_success     = form.announce_update_success.data,
			announce_update_available   = form.announce_update_available.data
		)
		db.session.add(new_webhook)
		db.session.commit()
		flash('Discord Webhook created!', 'success')
		logger.info(f"Discord Webhook '{form.name.data}' has been created!")
		return redirect(url_for("discord_webhooks"))
	else:
		for field, error in form.errors.items():
			logger.error(f"Form invalid: {field.capitalize()}: {error}")
			flash(f'{field.capitalize()}: {error[0]}', 'danger')
	return render_template('discordwebhook.html', title='Discord Webhooks', form=form, webhooks=webhooks, action='new')

@app.route("/discordwebhook/<int:id>", methods=['GET', 'POST'])
@login_required
def discord_webhook(id):
	webhook = DiscordWebhook.query.get_or_404(id)
	form    = DiscordWebhookForm()

	if form.validate_on_submit():
		if form.delete.data == True:
			db.session.delete(webhook)
			db.session.commit()
			logger.info(f"Discord Webhook '{webhook.name}' deleted")
			flash(f"Discord Webhook '{webhook.name}' deleted", "success")
			return redirect(url_for("discord_webhooks"))
		webhook.name                        = form.name.data
		webhook.webhook                     = form.webhook.data
		webhook.enabled                     = form.enabled.data
		webhook.announce_player_connect     = form.announce_player_connect.data
		webhook.announce_player_disconnect  = form.announce_player_disconnect.data
		webhook.announce_player_buffer_time = form.announce_player_buffer_time.data
		webhook.announce_server_start       = form.announce_server_start.data
		webhook.announce_server_shutdown    = form.announce_server_shutdown.data
		webhook.announce_update_success     = form.announce_update_success.data
		webhook.announce_update_available   = form.announce_update_available.data
		db.session.commit()
		flash('Discord Webhook updated!', 'success')
		logger.info(f"Discord Webhook '{form.name.data}' has been updated!")
		return redirect(url_for("discord_webhooks"))
	else:
		for field, error in form.errors.items():
			logger.error(f"Form invalid: {field.capitalize()}: {error}")
			flash(f'{field.capitalize()}: {error[0]}', 'danger')
	return render_template('discordwebhook.html', title='Discord Webhooks', form=form, webhook=webhook, action='edit')
	form = DiscordWebhookForm()
	if len(DiscordWebhook.query.all()) > 0:
		pass
	if form.validate_on_submit():
		dwh = User(username=form.username.data, email=form.email.data)
		db.session.add(dwh)
		db.session.commit()
		flash('Discord Webhook created!', 'success')
		logger.info(f"Discord Webhook '{form.name.data}' has been created!")
	return render_template('discordwebhook.html', title='Discord Webhook', form=form)