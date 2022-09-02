import _version as version
import argparse
import os
import time
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
from flask_migrate import Migrate # flask db init, flask db migrate, flask db upgrade
from bedrocksvc.flasklog import modify_flask_logs
import atexit
from flask_socketio import SocketIO, send, emit, disconnect

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
args, unknown = parser.parse_known_args()

logger = init_logger(console_debug_lvl=Config.LOG_LEVEL_CONSOLE, retention_days=Config.LOG_RETENTION)
modify_flask_logs()

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
migrate = Migrate(app, db)

bcrypt = Bcrypt(app) # for hashing not encryption
crypt = Fernet(app.config['SECRET_KEY'])

socketio = SocketIO(app, logger=False, engineio_logger=False)

# toolbar = DebugToolbarExtension(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

Session(app)

global session_data
session_data = {}

def OnExitApp():
	logger.info(f"Checking BDS status before exiting...")
	if BDSServer.is_running():
		BDSServer.stop_server()
		time.sleep(2)

# if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
#   # The reloader has already run - do what you want to do here

if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
	# The app is not in debug mode or we are in the reloaded process
	# atexit.register(OnExitApp)
	pass

from bedrocksvc.bds import BDSServer # import bds after socketio
BDSServer = BDSServer()
atexit.register(OnExitApp)
# # BDSServer.start_server()

from bedrocksvc import routes        # import routes after app
from bedrocksvc import socketevents  # import socketevents after app
from bedrocksvc import models        # import models before db creation

# create db if none exists
if not os.path.isfile(os.path.join(cwd, db_name)):
	db.create_all()
	logger.debug(f"'{db_name}' created")