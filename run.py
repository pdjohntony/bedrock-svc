"""
----------------------------------------------------------------------
Bedrock Svc - Phill Johntony
Summary:
	Python Flask wrapper for Minecraft Bedrock servers
----------------------------------------------------------------------
"""

import webbrowser
from threading import Timer
from bedrocksvc import app, args, socketio
import atexit

"""
TODO

"""

def open_browser():
	# don't open browser during debug
	if not app.debug:
		print("Opening web browser...")
		webbrowser.open_new(f"http://localhost:{args.port}/")

def OnExitApp():
	print(f"OnExitApp() {__name__}")

if __name__ == "__main__":
	Timer(1, open_browser).start();
	# atexit.register(OnExitApp)
	# app.run(debug=args.debug, port=args.port) # use_reloader=False
	socketio.run(app, debug=args.debug, port=args.port, use_reloader=False)