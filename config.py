from dotenv import load_dotenv
import os

load_dotenv()

host = os.getenv('HOST', '0.0.0.0')
port = int(os.getenv('PORT', '5000'))
reload = bool(os.getenv('RELOAD', True))
