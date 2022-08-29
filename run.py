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

"""
TODO

?Reference
https://www.youtube.com/playlist?list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH
https://github.com/CoreyMSchafer/code_snippets/tree/master/Python/Flask_Blog
https://github.com/TommyCox/bedrock-server-wrapper
"""

def open_browser():
	# don't open browser during debug
	if not app.debug:
		print("Opening web browser...")
		webbrowser.open_new(f"http://localhost:{args.port}/")

if __name__ == "__main__":
	Timer(1, open_browser).start();
	app.run(debug=args.debug, port=args.port)