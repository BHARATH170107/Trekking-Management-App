import os

from flask import Flask

from config import Config
from extensions import db, login_manager
from models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Make sure the instance/ folder exists before SQLite tries to write there
    os.makedirs(os.path.join(os.path.dirname(__file__), "instance"), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.staff import staff_bp
    from routes.trekker import trekker_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(trekker_bp)

    with app.app_context():
        db.create_all()  # creates tables programmatically -- no manual DB editing

    return app


app = create_app()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    app.run(debug=True,port=5002)
