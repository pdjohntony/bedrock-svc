import logging
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from bedrocksvc.models import Server

logger = logging.getLogger("global")

class ServerForm(FlaskForm):
	cluster      = StringField("Cluster Name", description="Production, Lab, etc...", validators=[DataRequired()])
	host         = StringField("Host", validators=[DataRequired()])
	host_type    = SelectField("Host Type", choices=["CUCM", "CUC"], default="CUCM", coerce=str, validators=[DataRequired()])
	app_username = StringField("App Username", validators=[DataRequired()])
	app_password = PasswordField("App Password", validators=[DataRequired()])
	os_username  = StringField("OS Username", validators=[DataRequired()])
	os_password  = PasswordField("OS Password", validators=[DataRequired()])
	version      = SelectField("Version", choices=[12.5, 14.0], default=14.0, coerce=float, validators=[DataRequired()])
	save         = SubmitField("Save")
	update       = False
	update_host  = None

	def validate_host(self, host):
		if self.update:
			if self.update_host == host.data: # if DB matches Form do nothing
				return

		server = Server.query.filter_by(host=host.data).first()
		if server:
			raise ValidationError(f"Host {server.host} already exists!")