from flask import Flask, get_flashed_messages, render_template_string, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, current_user
from flask_babel import Babel, gettext
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

from extensions import db, bcrypt, login_manager, limiter, csrf, mail
from models import User, Subject, Review, Suggestion, SuggestionVote
from auth import auth_bp
from reviews import reviews_bp
from suggestions import suggestions_bp
from lecturer_search import search_lecturers_by_email

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-please-change-in-production")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, 'database', 'mmuinsight.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@mmuinsight.edu.my')
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
app.config['LANGUAGES'] = {
    'en': 'English',
    'ms': 'Malay',
    'zh': 'Chinese'
}

def get_locale():
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or 'en'

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
limiter.init_app(app)
csrf.init_app(app)
mail.init_app(app)
babel = Babel(app, locale_selector=get_locale)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(reviews_bp)
app.register_blueprint(suggestions_bp)

@app.route("/set-language/<language>")
def set_language(language):
    if language in app.config['LANGUAGES']:
        session['language'] = language
    return redirect(request.referrer or url_for('index'))

@app.route("/set-theme/<theme>")
def set_theme(theme):
    if theme in ['light', 'dark']:
        session['theme'] = theme
    return redirect(request.referrer or url_for('index'))

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

@app.route("/terms-of-service")
def terms_of_service():
    return render_template('terms_of_service.html')

@app.route("/privacy-policy")
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route("/about")
def about_us():
    return render_template('about_us.html')

if __name__ == "__main__":
    # use DEBUG from environment variable (.env file)
    # never hardcode debug=True - it's a critical security risk in production
    debug_mode = os.environ.get("DEBUG", "False").lower() in ['true', '1', 'yes']
    app.run(debug=debug_mode)
