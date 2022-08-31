import logging
from werkzeug import serving
import re

logger = logging.getLogger(__name__)

def modify_flask_logs():
	"""Disable logs for requests to specific endpoints."""

	logger = logging.getLogger()
	disabled_endpoints = ('.*\.css', '.*\.js')
	parent_log_request = serving.WSGIRequestHandler.log_request

	def log_request(self, *args, **kwargs):
		# print(self.path)
		if not any(re.match(f"{de}$", self.path) for de in disabled_endpoints):
			# parent_log_request(self, *args, **kwargs)
			# really jank way of customizing the Flask logs, removing duplicate datetime
			logger.info(f"{self.client_address[0]} - {self.command} - {self.path}")

	serving.WSGIRequestHandler.log_request = log_request