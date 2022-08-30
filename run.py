"""
----------------------------------------------------------------------
Bedrock Svc - Phill Johntony
Summary:
	Python Flask wrapper for Minecraft Bedrock servers
----------------------------------------------------------------------
"""

import webbrowser
from threading import Timer
from bedrocksvc import app, args
import atexit

"""
TODO

?Reference
https://www.youtube.com/playlist?list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH
https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog
https://github.com/TommyCox/bedrock-server-wrapper

https://betterprogramming.pub/create-exit-handlers-for-your-python-appl-bc279e796b6b
^ includes a scheduler
https://werkzeug.palletsprojects.com/en/2.0.x/serving/#shutting-down-the-server
https://www.techcoil.com/blog/how-to-use-nssm-to-run-a-python-3-application-as-a-windows-service-in-its-own-python-3-virtual-environment/
https://gist.github.com/ruedesign/5218221
https://pyquestions.com/how-to-kill-a-child-thread-with-ctrl-c
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
	atexit.register(OnExitApp)
	app.run(debug=args.debug, port=args.port) # use_reloader=False