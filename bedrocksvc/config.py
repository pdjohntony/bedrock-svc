import os
import sys
from dotenv import load_dotenv

class Config:
	load_dotenv()

	def str2bool(x):
		if x == None:
			pass
		elif x.lower() == "true":
			x = True
		elif x.lower() == "false":
			x = False
		return x
	
	def str2int(x):
		if x == None:
			pass
		else:
			x = int(x)
		return x
	
	SECRET_KEY        = os.environ.get("SECRET_KEY")
	LOG_LEVEL_CONSOLE = str2bool(os.environ.get("LOG_LEVEL_CONSOLE"))
	LOG_RETENTION     = str2int(os.environ.get("LOG_RETENTION"))
	# DB_NAME         = os.environ.get("DB_NAME")

	if SECRET_KEY == None:
		print("Missing SECRET_KEY environment variable!")
		sys.exit(1)
	
	if LOG_LEVEL_CONSOLE == None:
		print("Defaulting LOG_LEVEL_CONSOLE to False")
		LOG_LEVEL_CONSOLE = False
	
	if LOG_RETENTION == None:
		print("Defaulting LOG_RETENTION to 180")
		LOG_RETENTION = 180