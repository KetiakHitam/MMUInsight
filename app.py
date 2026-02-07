from flask import Flask, get_flashed_messages, render_template_string, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, current_user, login_required
from flask_babel import Babel, gettext
from datetime import datetime
import os
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Ensure DATABASE_PATH is set (same as init_db_safe.py does)
if 'DATABASE_PATH' not in os.environ:
    db_directory = os.path.join(os.path.dirname(BASE_DIR), 'mmuinsight_data')
    os.makedirs(db_directory, exist_ok=True)
    os.environ['DATABASE_PATH'] = os.path.join(db_directory, 'mmuinsight.db')

from extensions import db, bcrypt, login_manager, limiter, csrf, mail
from models import User, Subject, Review, Suggestion, SuggestionVote
from auth import auth_bp
from reviews import reviews_bp
from suggestions import suggestions_bp
from bugs import bugs_bp
from changelog import changelog_bp
from lecturer_search import search_lecturers_by_email

app = Flask(__name__)

debug_mode = os.environ.get("DEBUG", "False").lower() in ["true", "1", "yes"]

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-please-change-in-production")

# Session Cookie Security (Flask-Login handles persistence via database)
app.config["PERMANENT_SESSION_LIFETIME"] = 7 * 24 * 3600  # 7 days
app.config["SESSION_COOKIE_SECURE"] = not debug_mode  # HTTPS only in production
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Prevent CSRF

# Use PostgreSQL in production (Railway), SQLite in development
db_url = os.environ.get('DATABASE_URL')
if db_url:
    # Convert old psycopg2 dialect to new psycopg dialect for SQLAlchemy 2.0+
    if db_url.startswith('postgresql://'):
        db_url = db_url.replace('postgresql://', 'postgresql+psycopg://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    # Fallback to SQLite for local development
    db_path = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(BASE_DIR), 'mmuinsight_data', 'mmuinsight.db'))
    db_dir = os.path.dirname(db_path)
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.abspath(db_path)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path.replace('\\', '/')
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
# Flask-Session disabled: Flask-Login handles user persistence via database
babel = Babel(app, locale_selector=get_locale)

# Create database tables on startup
with app.app_context():
    db.create_all()
    
    # Seed lecturers from scraped_lecturers.txt if table is empty
    from models import Lecturer
    lecturer_count_before = Lecturer.query.count()
    if lecturer_count_before == 0:
        import re
        lecturers_file = os.path.join(BASE_DIR, 'scraped_lecturers.txt')
        try:
            print(f"Loading lecturers from {lecturers_file}...")
            # Try multiple encodings
            content = None
            for encoding in ['utf-8-sig', 'utf-16', 'utf-16-le', 'utf-8', 'latin-1']:
                try:
                    with open(lecturers_file, 'r', encoding=encoding) as f:
                        content = f.read()
                    print(f"  Decoded as {encoding}")
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if content is None:
                raise ValueError("Could not decode file with any encoding")
            
            pattern = r'^\s*\d+\.\s+(.+?)\n.*?\|\s*([a-zA-Z0-9.@-]+@mmu\.edu\.my)'
            for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
                name = re.sub(r'\s+', ' ', match.group(1).strip())
                email = match.group(2).strip()
                
                if name and email and not Lecturer.query.filter_by(email=email).first():
                    db.session.add(Lecturer(name=name, email=email, department='FCI'))
            
            db.session.commit()
            final_count = Lecturer.query.count()
            print(f"✓ Seeded {final_count - lecturer_count_before} lecturers (total: {final_count})")
        except FileNotFoundError:
            print(f"✗ File not found: {lecturers_file}")
        except Exception as e:
            print(f"✗ Error seeding lecturers: {type(e).__name__}: {e}")
    
    # Create admin/owner accounts from env vars (always regenerate hashes)
    admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin')
    owner_pass = os.environ.get('OWNER_PASSWORD', 'owner')
    
    for email, role, password in [
        ("admin@mmu.edu.my", "ADMIN", admin_pass),
        ("owner@mmu.edu.my", "OWNER", owner_pass),
    ]:
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, user_type="admin", role=role, is_verified=True, is_claimed=True)
            db.session.add(user)
        
        # Always regenerate password hash to ensure it's valid (encode bytes to string)
        pw_hash = bcrypt.generate_password_hash(password)
        user.password_hash = pw_hash.decode('utf-8') if isinstance(pw_hash, bytes) else pw_hash
        db.session.add(user)
    
    db.session.commit()


@app.before_request
def enforce_https():
    current_debug_mode = os.environ.get("DEBUG", "False").lower() in ["true", "1", "yes"]
    if current_debug_mode:
        return
    if request.is_secure:
        return
    return redirect(request.url.replace("http://", "https://", 1), code=301)


@app.after_request
def add_security_headers(response):
    if not debug_mode and request.is_secure:
        response.headers.setdefault(
            "Strict-Transport-Security",
            "max-age=31536000; includeSubDomains",
        )
    return response

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_bp)
app.register_blueprint(reviews_bp)
app.register_blueprint(suggestions_bp)
app.register_blueprint(bugs_bp)
app.register_blueprint(changelog_bp)

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
    recent_searches = []
    if current_user.is_authenticated and current_user.user_type == 'student' and current_user.search_history:
        id_strs = current_user.search_history.split(',')
        # Convert to integers for PostgreSQL type compatibility
        ids = []
        for id_str in id_strs:
            try:
                ids.append(int(id_str.strip()))
            except ValueError:
                continue
        
        # Fetch users and preserve order
        if ids:
            lecturers = {u.id: u for u in User.query.filter(User.id.in_(ids)).all()}
            recent_searches = [lecturers[uid] for uid in ids if uid in lecturers]
        
    return render_template('index.html', recent_searches=recent_searches)

@app.route("/search", methods=["GET"])
def search_page():
    q = request.args.get("q", "").strip()
    if not q:
        return render_template(
            "index.html",
            search_query="",
            search_results=None,
        )

    matches = search_lecturers_by_email(q)  # list of (User, score) sorted by score descending
    results = [u for u, s in matches]

    return render_template(
        "index.html",
        search_query=q,
        search_results=results,
    )


@app.route("/search/results", methods=["GET"])
@login_required
def search_results_page():
    q = request.args.get("q", "").strip()
    matches = search_lecturers_by_email(q) if q else []
    results = [u for u, s in matches]
    return render_template(
        "results.html",
        q=q,
        results=results,
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
    return render_template('professor-info.html')

@app.route("/terms-of-service")
def terms_of_service():
    return render_template('terms_of_service.html')

@app.route("/privacy-policy")
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route("/about")
def about_us():
    return render_template('about_us.html')

@app.route("/faq")
def faq():
    return render_template('FAQ.html')

if __name__ == "__main__":
    debug_mode = os.environ.get("DEBUG", "False").lower() in ['true', '1', 'yes']
    app.run(debug=debug_mode)
