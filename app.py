from flask import Flask, get_flashed_messages, render_template_string, render_template, request, jsonify
from flask_login import LoginManager, current_user
import os

from extensions import db, bcrypt
from models import User, Subject, Review
from auth import auth_bp
from reviews import reviews_bp

app = Flask(__name__)

app.config["SECRET_KEY"] = "isac_is_a_monkey67"
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, 'database', 'mmuinsight.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(reviews_bp)

@app.route("/", methods=["GET"])
def index():
    if current_user.is_authenticated:
        lecturers = User.query.filter_by(user_type='lecturer').all()
        return render_template('index.html', lecturers=lecturers)
    return render_template('index.html')

@app.get("/test")
def test():
    return "<h1>TESTING WORKS</h1>"

@app.route("/login.html")
def login():
    return render_template('login.html')

@app.route("/register.html")
def register():
    return render_template('register.html')

@app.route("/Professor-info.html")
def Professors():
    return render_template('Professor-info.html')


@app.route('/search')
def search():
    """Search users by email (case-insensitive partial match).

    Query param: q
    Returns JSON list of objects: {id, email, user_type}
    """
    q = request.args.get('q', '')
    q = q.strip()
    if not q:
        return jsonify([])

    # only return lecturers so student emails aren't exposed
    matches = User.query.filter(User.user_type == 'lecturer', User.email.ilike(f"%{q}%")).limit(20).all()
    results = [{'id': u.id, 'email': u.email, 'user_type': u.user_type} for u in matches]
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
