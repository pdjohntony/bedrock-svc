import logging
import subprocess
import shlex
import threading
from threading import Lock
from pathlib import Path
import atexit

logger = logging.getLogger(__name__)

class BDS_Wrapper(subprocess.Popen):
	def __init__(self, exec_path, **kwargs):
		super().__init__(
			exec_path,
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			creationflags = subprocess.CREATE_NO_WINDOW,
			**kwargs
		)

	def read_output(self, output_handler):
		# Spawns a new thread to read the output.
		# The thread calls output_handler with the string that was read.
		# Returns the thread.
		def worker():
			for line in iter(self.stdout.readline, b''):
				output_handler(line.decode("utf-8"))

		return threading.Thread(target=worker)

	def is_running(self):
		return self.poll() == None

	def write(self, command_string, terminator = "\n"):
		if self.is_running():
			data = command_string + terminator
			self.stdin.write(data.encode())
			self.stdin.flush()
			return True
		else:
			return False

class BDSServer:
	default_server_dir = "minecraft_server"
	default_exec_name = "bedrock_server.exe"
	def __init__(self, *args, server_dir = None, exec_name = None, **kwargs):
		super().__init__(*args, **kwargs)

		self.server_instance = None
		self.server_dir = self.default_server_dir if server_dir is None else server_dir
		self.exec_name = self.default_exec_name if exec_name is None else exec_name
		self.autoscroll_log = True # Might make this setting edit-able later.
		self.locks = Locks()
		self.log_listeners = set()

	def bind_inputs(self, input_handler):
		"""Specifies what function should handle user inputs from the command lines."""
		self.server_input = input_handler
	
	def send_input(self, text):
		"""Sends an input string to the server."""
		self.server_input(text)
		self.write_console(f"[SENDING] {text}")
	
	def __output_handler(self, text):
		self.write_console(text)
		self.__interpret(text)
	
	def write_console(self, text):
		"""Writes a message to console."""
		logger.info(f"BDS {text.strip()}")
	
	def __interpret(self, message):
		"""Reads input from the server or user and calls listeners."""
		# Send server messages to listeners.
		for listener in self.log_listeners.copy():
			listener(self, message)
		pass

	def message_user(self, message):
		"""Displays a message from the wrapper to the user."""
		text = message.strip()
		if not (text == ""):
			self.write_console(f"{text}")

	def start_server(self):
		"""Starts the minecraft server."""
		if self.server_instance is None or not self.server_instance.is_running():
			self.server_instance = BDS_Wrapper(Path("bedrock_server") / "bedrock_server.exe")
			self.console_thread = self.server_instance.read_output(output_handler = self.__output_handler)
			self.console_thread.start()
			self.bind_inputs(self.server_instance.write)

			self.log_listeners.clear() # Create a set holding listening functions.
			# self.add_listener(PlayerList()) # Create a new player list and add to listeners.
	
	def is_running(self):
		if self.server_instance is None or not self.server_instance.is_running():
			return False
		return True
	
	def stop_server(self, post_stop = None, *args):
		# This is a really ugly function.
		MAX_WAIT_DEPTH = 15 # Maximum number of WAIT_INTERVAL to wait.
		WAIT_INTERVAL = 1000 # In ms.
		this_lock = self.locks.stop
		if not this_lock.acquire(False):
			return
		if self.server_instance and self.server_instance.is_running():
			self.message_user("Stopping server.")
			self.send_input("stop")

			def pause(action, depth, *args):
				if depth > MAX_WAIT_DEPTH:
					self.message_user("Server did not stop in time. Cancelling action.")
					this_lock.release()
					return
				if self.server_instance and self.server_instance.is_running():
					# Go another level.
					self.message_user("Waiting for server to stop.")
					self.after(WAIT_INTERVAL, pause, action, depth + 1, *args)
				else:
					self.message_user("Server stop confirmed.")
					this_lock.release()
					action(*args)
			if post_stop:
				self.after(WAIT_INTERVAL, pause, post_stop, 0, *args)
		else:
			this_lock.release()
			if post_stop:
				post_stop(*args)

class Locks():
	def __init__(self):
		self.lock_dict = {}

	def __getattr__(self, name):
		if name in self.lock_dict:
			return self.lock_dict[name]
		else:
			self.lock_dict[name] = Lock()
			return self.lock_dict[name]