import logging
import functools
from bedrocksvc import socketio, send, emit, disconnect
from bedrocksvc import BDSServer
# from bedrocksvc.models import User, Player, PlayerEvent
from flask_login import login_user, current_user, logout_user, login_required

logger = logging.getLogger(__name__)

def authenticated_only(f):
	@functools.wraps(f)
	def wrapped(*args, **kwargs):
		if not current_user.is_authenticated:
			disconnect()
			logger.info(f"Disconnected unauthenticated user from socket")
		else:
			return f(*args, **kwargs)
	return wrapped

@socketio.on('admin-connect')
@authenticated_only
def admin_connect(json):
	logger.debug(f"Socket received: {json}")
	bdsstatus = BDSServer.is_running()
	bdsloghistory = BDSServer.get_log_history()

	emit('bds-log-msg', {'data':'Connected to log...'})
	emit('bds-status', {'data':bdsstatus})
	logger.debug(f"Socket sent: bds-status - data: {bdsstatus}")
	for msg in bdsloghistory:
		emit('bds-log-msg', {'data':msg})

# def modulesend(x):
# 	socketio.send({'data':x}, broadcast=True)

@socketio.on('bds-status')
@authenticated_only
def bds_status():
	bdsstatus = BDSServer.is_running()
	emit('bds-status', {'data':bdsstatus})
	# logger.debug(f"Socket sent: bds-status - data: {bdsstatus}")

@socketio.on('bds-startup')
@authenticated_only
def bds_startup(data):
	logger.info(f"User '{current_user.username}' initiated startup.")
	BDSServer.start_server()
	# BDSServer.write_console("PRETEND STARTUP")

@socketio.on('bds-shutdown')
@authenticated_only
def bds_shutdown(data):
	logger.info(f"User '{current_user.username}' initiated shutdown.")
	BDSServer.stop_server()
	# BDSServer.write_console("PRETEND SHUTDOWN")

@socketio.on('bds-send-input')
@authenticated_only
def bds_send_input(data):
	logger.debug(f"Socket received: {data}")
	BDSServer.send_input(data["command"])