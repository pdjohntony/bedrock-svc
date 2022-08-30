import _version as version
import argparse
import os
from datetime import timedelta
from bedrocksvc.config import Config
from bedrocksvc.logger import init_logger
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_session import Session
from flask_debugtoolbar import DebugToolbarExtension
from cryptography.fernet import Fernet
from bedrocksvc.bds import BDSServer
import atexit

"""
TODO
Clean up flask log messages
	Rich might be messing these up
"""

parser = argparse.ArgumentParser(prog="bedrock-svc", description="Bedrock Svc - Web GUI for Minecraft Bedrock servers")
parser.add_argument("-d", "--debug", action="store_true", help="Displays debug logs in the console")
parser.add_argument("-p", "--port", type=int, default=5001, help="Specify custom port (default is 5001)")
# parser.add_argument("-c", "--cli", action="store_true", help="Enables CLI only mode")
# parser.add_argument("-t", "--test", action="store_true", help="Used for testing only")
args = parser.parse_args()

logger = init_logger(console_debug_lvl=Config.LOG_LEVEL_CONSOLE, retention_days=Config.LOG_RETENTION)

cwd = os.path.abspath(os.path.dirname(os.path.abspath(__name__)))

app_title = f"Bedrock Svc - Version: {version.__version__} Build: {version.__build__} Date: {version.__build_date__}"
logger.info(f"[u]{app_title}[/u]")

app = Flask(__name__)
app.debug = args.debug
app.config['SECRET_KEY'] = Config.SECRET_KEY

app.config["SESSION_TYPE"]               = "filesystem"
app.config["SESSION_PERMANENT"]          = True
app.config["SESSION_FILE_THRESHOLD"]     = 50
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=6)

db_name = f"{__name__}.db"
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(cwd, db_name)}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

bcrypt = Bcrypt(app) # for hashing not encryption
crypt = Fernet(app.config['SECRET_KEY'])

# toolbar = DebugToolbarExtension(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

Session(app)

global session_data
session_data = {}

# create db if none exists
if not os.path.isfile(os.path.join(cwd, db_name)):
	db.create_all()
	logger.debug(f"'{db_name}' created")

def OnExitApp():
	print(f"OnExitApp() {__name__}")
	# BDSServer.send_input("stop")

# if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
#   # The reloader has already run - do what you want to do here

if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
	# The app is not in debug mode or we are in the reloaded process
	BDSServer = BDSServer()
	BDSServer.start_server()
	atexit.register(OnExitApp)

from bedrocksvc import routes # needed to bring routes to app