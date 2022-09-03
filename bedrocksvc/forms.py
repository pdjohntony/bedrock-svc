import logging
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField, IntegerField
from wtforms.validators import DataRequired, InputRequired, Length, EqualTo, Email, ValidationError, URL, NumberRange
from bedrocksvc.models import User

logger = logging.getLogger(__name__)

class RegistrationForm(FlaskForm):
	username         = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email            = StringField('Email', validators=[DataRequired(), Email()])
	password         = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit           = SubmitField('Sign Up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
	email    = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit   = SubmitField('Login')

class DiscordWebhookForm(FlaskForm):
	# id                          = IntegerField('id', validators=[DataRequired()])
	name                        = StringField('Name', validators=[DataRequired(), Length(min=1, max=120)])
	webhook                     = StringField('Webhook', validators=[DataRequired(), URL()])
	enabled                     = BooleanField('Enable', validators=[])
	announce_player_connect     = BooleanField('Announce Player Connect', validators=[])
	announce_player_disconnect  = BooleanField('Announce Player Disconnect', validators=[])
	announce_player_buffer_time = IntegerField('Announce Player Buffer Time', validators=[InputRequired(), NumberRange(min=0, max=600)], default=0)
	announce_server_start       = BooleanField('Announce Server Start', validators=[])
	announce_server_shutdown    = BooleanField('Announce Server Shutdown', validators=[])
	announce_update_success     = BooleanField('Announce Update Success', validators=[])
	announce_update_available   = BooleanField('Announce Update Available', validators=[])
	submit                      = SubmitField('Save')
	update                      = SubmitField('Update')
	delete                      = SubmitField('Delete')