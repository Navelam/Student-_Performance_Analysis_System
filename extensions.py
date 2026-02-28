# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()  # CSRF protection enabled
mail = Mail()
migrate = Migrate()

@login_manager.user_loader
def load_user(user_id):
    from model import User
    return User.query.get(int(user_id))