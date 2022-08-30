import logging
from logging.config import dictConfig
import os
import sys
import time
import datetime
import traceback
from rich import print
from rich.logging import RichHandler
from werkzeug import serving
import re

"""
In entrypoint/main module call `init_logger`. This will return the root logger.

from logger import init_logging
log = init_logging()

In other modules

import logging
log = logging.getLogger(__name__)
"""

def init_logger(console_debug_lvl=False, retention_days=180):
	"""
	Initiates logger

	- Creates log directory if none exists
	- Creates two log handlers
		- One for the log file
		- Another for the console
	- Sets debug level

	Args:
		console_debug_lvl (bool): False on prints only in log file, True on prints to log file & console
	"""
	try:
		# dictConfig({
		# 		'version': 1,
		# 		'formatters': {'default': {
		# 				'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
		# 		}},
		# 		'handlers': {'wsgi': {
		# 				'class': 'logging.StreamHandler',
		# 				'stream': 'ext://flask.logging.wsgi_errors_stream',
		# 				'formatter': 'default'
		# 		}},
		# 		'root': {
		# 				'level': 'INFO',
		# 				'handlers': ['wsgi']
		# 		}
		# })
		logger = logging.getLogger()
		cwd    = os.path.abspath(os.path.dirname(os.path.abspath(__name__)))
		# Log File Variables
		log_file_dir      = "logs"
		log_file_dir      = os.path.join(os.getcwd(), log_file_dir)
		log_file_name     = __package__
		log_file_ext      = '.log'
		log_file_date     = datetime.datetime.now().strftime("%Y%m%d")
		log_file_time     = datetime.datetime.now().strftime("%H%M%S")
		log_file_fullname = (log_file_name + '-' + log_file_date + '-' + log_file_time + log_file_ext)
		log_file_actual   = os.path.join(log_file_dir, log_file_fullname)

		# Create Log File directory if it does not exist
		if not os.path.exists(log_file_dir): os.mkdir(log_file_dir)

		# Global log FILE settings
		log_file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s -> %(message)s')
		log_file_handler   = logging.FileHandler(log_file_actual)
		log_file_handler.setFormatter(log_file_formatter)

		# Global log CONSOLE settings
		# log_console_formatter = logging.Formatter('%(asctime)s - %(message)s', '%H:%M:%S')
		log_console_formatter = logging.Formatter()
		# log_console_handler   = logging.StreamHandler()
		# log_console_handler   = RichHandler(show_level=False, show_path=False, markup=True, highlighter=None, keywords=None, log_time_format="[%H:%M:%S]")
		# log_console_handler.setFormatter(log_console_formatter)

		if console_debug_lvl == True:
			# Debug writes to log file AND displays in console
			log_console_handler = RichHandler(show_level=True, show_path=True, markup=True, highlighter=None, keywords=None, log_time_format="[%H:%M:%S]")
			log_console_handler.setFormatter(log_console_formatter)
			log_console_handler.setLevel(logging.DEBUG)
			logger.setLevel(logging.DEBUG)
		elif console_debug_lvl == False:
			# Debug only writes to log file, does not display in console
			log_console_handler = RichHandler(show_level=False, show_path=False, markup=True, highlighter=None, keywords=None, log_time_format="[%H:%M:%S]")
			log_console_handler.setFormatter(log_console_formatter)
			log_console_handler.setLevel(logging.INFO)
			logger.setLevel(logging.DEBUG)
		else:
			# Debug is completely off, doesn't write to log file
			log_console_handler = RichHandler(show_level=False, show_path=False, markup=True, highlighter=None, keywords=None, log_time_format="[%H:%M:%S]")
			log_console_handler.setFormatter(log_console_formatter)
			log_console_handler.setLevel(logging.INFO)
			logger.setLevel(logging.INFO)

		# Adds configurations to global log
		logger.addHandler(log_file_handler)
		logger.addHandler(log_console_handler)
		
		purge_files(retention_days)
		disable_endpoint_logs()
		return logger
	except IOError as e:
		errOut = "** ERROR: Unable to create or open log file %s" % log_file_name
		if e.errno == 2:    errOut += "- No such directory **"
		elif e.errno == 13: errOut += " - Permission Denied **"
		elif e.errno == 24: errOut += " - Too many open files **"
		else:
			errOut += " - Unhandled Exception-> %s **" % str(e)
			sys.stderr.write(errOut + "\n")
			traceback.print_exc()

	except Exception:
		traceback.print_exc()

def purge_files(retention_days=180, file_dir="logs", file_ext=".log"):
	"""
	Purges files past a certain date
	"""
	try:
		logger = logging.getLogger()
		if retention_days > 0:
			logger.debug(f"Purging {file_ext} files in {file_dir} folder older than {retention_days} days...")
			retention_sec = retention_days*86400
			now = time.time()
			for file in os.listdir(file_dir):
				if file.endswith(file_ext):
					file_fullpath = os.path.join(file_dir, file)
					if os.stat(file_fullpath).st_mtime < (now-retention_sec):
						os.remove(file_fullpath)
						logger.debug(f"{file} has been deleted")
	except Exception as e:
		logger.error(f"File purge error: {e}")

def disable_endpoint_logs():
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