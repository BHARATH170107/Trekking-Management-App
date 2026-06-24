from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Created here (not inside app.py) so models.py and routes/*.py
# can import `db` / `login_manager` without circular-import issues.
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
