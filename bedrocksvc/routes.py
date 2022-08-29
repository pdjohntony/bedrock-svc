import logging
from flask import url_for, render_template, flash, redirect, request, session
from bedrocksvc import app, db, crypt, session_data
from bedrocksvc.models import Server
from bedrocksvc.forms import ServerForm

logger = logging.getLogger(__name__)

"""
TODO
"""

@app.route("/")
def home():
	logger.info("Info message")
	logger.debug("Debug message")
	return render_template("home.html")