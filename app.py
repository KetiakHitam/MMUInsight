from flask import Flask, get_flashed_messages, render_template_string, render_template, request, jsonify
from flask_login import LoginManager, current_user
import os

from extensions import db, bcrypt, login_manager
from models import User, Subject, Review
from auth import auth_bp
from reviews import reviews_bp
from lecturer_search import search_lecturers_by_email

app = Flask(__name__)

app.config["SECRET_KEY"] = "isac_is_a_monkey67"
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, 'database', 'mmuinsight.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(reviews_bp)

@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')

@app.route("/search", methods=["GET"])
def search_page():
    q = request.args.get("q", "").strip()
    results = search_lecturers_by_email(q)

    return render_template(
        "index.html",
        search_query=q,
        search_results=results
    )

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

if __name__ == "__main__":
    app.run(debug=True)
