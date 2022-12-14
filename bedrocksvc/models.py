import logging
from datetime import datetime
from bedrocksvc import db, login_manager
from flask_login import UserMixin

logger = logging.getLogger(__name__)

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))
class User(db.Model, UserMixin):
	id       = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(120), unique=True, nullable=False)
	email    = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)

	def __repr__(self):
		return f"User('{self.username}', '{self.email}')"

class Player(db.Model):
	id       = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(120), unique=True, nullable=False)
	events   = db.relationship('PlayerEvent', backref='author', lazy=True)

	def __repr__(self):
		return f"User('{self.username}')"

class PlayerEvent(db.Model):
	id        = db.Column(db.Integer, primary_key=True)
	date      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	event     = db.Column(db.Text, nullable=False)
	player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)

	def __repr__(self):
		return f"PlayerEvent('{self.date}', '{self.player_id}', '{self.event}')"

class DiscordWebhook(db.Model):
	id                          = db.Column(db.Integer, primary_key=True)
	name                        = db.Column(db.String(120), nullable=False)
	webhook                     = db.Column(db.String, nullable=False)
	enabled                     = db.Column(db.Boolean(), nullable=False)
	announce_player_connect     = db.Column(db.Boolean(), nullable=False)
	announce_player_disconnect  = db.Column(db.Boolean(), nullable=False)
	announce_player_buffer_time = db.Column(db.Integer, nullable=False)
	announce_server_start       = db.Column(db.Boolean(), nullable=False)
	announce_server_shutdown    = db.Column(db.Boolean(), nullable=False)
	announce_update_success     = db.Column(db.Boolean(), nullable=False)
	announce_update_available   = db.Column(db.Boolean(), nullable=False)

	def __repr__(self):
		return f"DiscordWebhook('{self.name}', '{self.webhook}')"