from datetime import datetime
from bedrocksvc import db

class Server(db.Model):
	id           = db.Column(db.Integer, primary_key=True)
	cluster      = db.Column(db.String(), nullable=True)
	host         = db.Column(db.String(), unique=True, nullable=False)
	host_type    = db.Column(db.String(), nullable=False)
	app_username = db.Column(db.String(), nullable=False)
	app_password = db.Column(db.String(), nullable=False)
	os_username  = db.Column(db.String(), nullable=False)
	os_password  = db.Column(db.String(), nullable=False)
	version      = db.Column(db.Float(), nullable=False)
	enabled      = db.Column(db.Boolean(), nullable=False, default=False)

	def __repr__(self):
		return f"Server('{self.cluster}, {self.host}, {self.version}')"