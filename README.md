# MMUInsight

MMUInsight is a dedicated, student-driven platform designed exclusively for Multimedia University (MMU) students. It allows students to search for lecturers, leave detailed reviews, discover insights about their courses, report platform bugs, and suggest new features. By fostering an environment for constructive feedback, MMUInsight helps students make informed decisions regarding their academic journeys.

## Features

- **Lecturer Reviews & Ratings**: Students can evaluate lecturers across multiple key criteria: Clarity, Engagement, Punctuality, Responsiveness, and Fairness.
- **Advanced Search & Discovery**: Search for lecturers seamlessly by their name or MMU email address.
- **Granular Roles & Moderation**: Comprehensive role-based access control (Owner, Admin, Moderator, Student) with built-in moderation workflows for reviews to keep the platform safe, respectful, and constructive.
- **Feedback & Bug Tracking**: A transparent ecosystem where users can suggest new features through a suggestion board (complete with upvoting/downvoting) and report platform bugs directly.
- **Multi-language Support (i18n)**: Fully supported and accessible UI translations in English, Malay, and Chinese.
- **Theme Customization**: Includes a dark mode toggle to adjust the UI to user preference.
- **Rich Text & Formatting**: Support for Markdown in reviews and platform updates.
- **Centralized Changelog & Status**: Centralized changelog and system status tracking to keep users informed of the latest updates and site maintenance.

## Tech Stack

- **Backend Framework**: Flask (Python 3)
- **Database Model**: SQLAlchemy (SQLite for local development, PostgreSQL ready for production environments)
- **Authentication & Security**: Flask-Login and Flask-Bcrypt (password hashing), Flask-WTF (CSRF protection)
- **Templating**: Jinja2 (with Markdown parsing via Bleach & Markdown libraries to prevent XSS)
- **Internationalization**: Flask-Babel

## Architecture Overview

- **app.py**: Main application entry point handling configuration, environment initialization, and blueprint registration.
- **models.py**: Core SQLAlchemy database schemas defining Users, Lecturers, Reviews, Suggestions, BugReports, and Audit logs.
- **Routing Modules**: Separated into logical blueprints (`auth/`, `reviews.py`, `suggestions.py`, `bugs.py`, `changelog.py`, `status.py`) for clean architecture.

## Local Development Setup

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd MMUInsight
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables Configuration:**
   Copy the example environment file and configure your local settings.

   ```bash
   cp .env.example .env
   ```

   _Note: Ensure you generate a secure `SECRET_KEY` and define your database paths inside `.env`._

5. **Initialize the Database:**

   ```bash
   python init_db.py
   ```

   _This command will bootstrap the initial database schema and necessary administrative roles._

6. **Run the Application:**
   ```bash
   flask run
   ```
   The application will be accessible at `http://127.0.0.1:5000`.

## Contribution Guidelines

Contributions are welcome! Please ensure that:

- Any new features are accompanied by appropriate database migrations if the models change.
- Code conforms to standard Python formatting (PEP 8).
- New strings introduced to the frontend are wrapped in standard `flask_babel` translation methods (`_()` or `gettext()`).

## License

This project is licensed under the provisions listed in the `LICENSE` file.
