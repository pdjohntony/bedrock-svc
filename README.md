# Bedrock Svc
Python Flask wrapper for Minecraft Bedrock servers.

.env
SECRET_KEY=xxx
DB_NAME=config.db

To generate a FLASK_KEY
>>> import secrets
>>> secrets.token_hex(16)
'xxx'

To generate a SECRET_KEY
>>> from cryptography.fernet import Fernet
>>> Fernet.generate_key()
b'xxx'