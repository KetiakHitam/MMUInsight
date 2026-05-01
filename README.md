<p align="center">
  <img src="hero.png" width="600" alt="MMUInsight Hero">
</p>

<h1 align="center">MMUInsight</h1>

<p align="center">
  <strong>A full-stack lecturer review platform built exclusively for Multimedia University (MMU) students to rate lecturers, submit anonymous feedback, and shape their academic future.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Backend-Flask_3.1-000000?style=flat-square&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/ORM-SQLAlchemy_2.0-D71F00?style=flat-square" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/Database-SQLite_|_PostgreSQL-336791?style=flat-square&logo=postgresql" alt="Database">
  <img src="https://img.shields.io/badge/Auth-Bcrypt_|_Flask--Login-4B8BBE?style=flat-square" alt="Auth">
  <img src="https://img.shields.io/badge/Search-RapidFuzz-orange?style=flat-square" alt="Search">
  <img src="https://img.shields.io/badge/i18n-Flask--Babel-purple?style=flat-square" alt="i18n">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="MIT License">
</p>

---

## Overview

MMUInsight is a student-driven, full-stack web application built for Multimedia University (MMU) students. It provides a secure, moderated environment where students can search for lecturers, write detailed multi-criteria reviews, view aggregated analytics, report bugs, suggest platform features, and contribute to a transparent academic feedback ecosystem.

Registration is strictly fenced to official MMU email domains (`@mmu.edu.my` and `@student.mmu.edu.my`), and all user-generated content passes through a multi-layered auto-moderation pipeline before publication.

Built for MMU Students, by MMU Students.

---

## Features

### Fuzzy Lecturer Search

- Locate lecturers by partial name or official MMU email using `RapidFuzz` fuzzy matching with weighted ratio scoring.
- Search results are ranked by relevance score (threshold: 60%) and enriched with metadata: review count, average rating, top subject taught, and avatar initials derived from the lecturer's email.
- Dual-field search: queries are matched against both the email local part and the cleaned lecturer name simultaneously, with the highest score per lecturer used for ranking.

### Multi-Criteria Review System

Instead of a single generic star rating, students rate lecturers on five specific academic dimensions:

- **Clarity** -- How well the lecturer explains concepts.
- **Engagement** -- How interactive and stimulating the classes are.
- **Punctuality** -- Adherence to class schedules and consultation hours.
- **Responsiveness** -- Speed and helpfulness in replying to student queries.
- **Fairness** -- Objectivity in grading and assessments.

Each review also includes:
- **Recommendation** -- A binary "Would you recommend?" flag.
- **Subject tagging** -- Associate a review with a specific subject code/name. Subjects are auto-suggested from the top 20 most-used entries, or students can create new ones on the fly.
- **Anonymous posting** -- Students can mask their identity per-review to encourage honest feedback.
- **Voting** -- Upvote/downvote system on reviews and replies (toggle-based, not cumulative).

### Student Analytics Dashboard

- Per-lecturer analytics page showing:
  - Overall rating (composite average of all 5 criteria).
  - Strongest and weakest categories.
  - Rating distribution histograms (1-5 per category).
  - Comparison against the global average across all lecturers (e.g., "0.8 points ABOVE AVERAGE").
  - Student's own review highlighted if it exists.

### Lecturer Profile Claiming

- Lecturers with `@mmu.edu.my` emails can **claim** their profile, verifying ownership via email domain matching.
- Claimed profiles allow the lecturer to write and edit a personal bio (40-word limit, Markdown-supported).
- Claimed status is publicly visible on the lecturer's profile card.

### Review Replies & Threads

- Both students and lecturers can reply to any review, creating threaded discussions.
- Replies support editing (with an "edited" indicator) and deletion by the author.
- Admin/Mod replies are visually distinguished with a staff badge.

### Review Reporting

- Students can flag inappropriate reviews with a written reason.
- Reports feed into the admin moderation queue (grouped by review to avoid duplicates).
- Admins can dismiss reports or delete the offending review, with full audit trail.

### Suggestions Board

- Students can propose new platform features with a title, description, and optional anonymity.
- Community-driven prioritization via upvote/downvote system with toggle mechanics.
- Sortable by "Most Upvoted" or "Newest".
- Admin panel for managing suggestion lifecycle: `Pending` -> `Reviewing` -> `Planned` / `Rejected`.

### Bug Reporting & Tracking

- Integrated ticketing system for reporting UI/UX issues or functional bugs.
- Each bug has a lifecycle: `New` -> `In Progress` -> `Resolved` -> `Closed`.
- Priority levels: `Low`, `Normal`, `High`, `Critical`.
- Admin bug detail view with internal notes, resolution notes, and a comment thread.
- Filterable and sortable admin dashboard for bug triage.

### Versioned Changelog

- Admin-managed changelog system with semantic versioning (`1.0.0`, `1.0.1`, etc.).
- Entries support Markdown formatting and publish/unpublish toggling.
- Public-facing changelog page renders only published entries, sorted newest-first.

### System Status Page

- Public status page showing overall system health (`Operational`, `Degraded`, `Warning`).
- 30-day uptime percentage calculation.
- Active and resolved incident history.
- Admin status dashboard with system-wide metrics: total users, total reviews, reviews this week, flagged content, pending bugs, bio completion percentage, claimed profile percentage, profanity detections, ASCII art detections, and average moderation turnaround time.

### Dark Mode

- Persistent dark/light theme toggle stored in the user session.
- Single-click switching without page reload artifacts.

### Internationalization (i18n)

- Full translation support for **English**, **Malay**, and **Chinese** using `Flask-Babel`.
- Language selector in the navbar, persisted in the session.
- All user-facing strings wrapped in `gettext()` / `_()` for translation extraction.

---

## Content Moderation Pipeline

Every piece of user-generated content (reviews, suggestions, bug reports) passes through a multi-stage moderation system before it becomes publicly visible.

### Auto-Moderation Engine (`moderation.py`)

The `ContentModerator` class runs six sequential checks on submitted text:

1. **Length Validation** -- Rejects content shorter than 10 characters, longer than 5,000, or with fewer than 3 words.
2. **Profanity Detection** -- Comprehensive dictionary-based filter with:
   - Direct word matching against an extensive blocklist.
   - **Leetspeak normalization** -- Translates `@`->`a`, `$`->`s`, `0`->`o`, etc., then re-checks.
   - **Spaced-out word detection** -- Catches `f u c k` style obfuscation by collapsing single-char-spaced sequences.
   - **Vowel-removal detection** -- Generates consonant skeletons of words and compares against the profanity list.
   - **Misspelling lookup table** -- Maps 60+ common deliberate misspellings (`fuk`, `shyt`, `biotch`, etc.) to their base forms.
3. **Spam Pattern Detection** -- Flags content with 3+ URLs, excessive character repetition (6+ consecutive identical chars), or 10+ @mentions.
4. **CAPS LOCK Abuse** -- Flags content where >30% of alphabetic characters are uppercase.
5. **Word Repetition** -- Flags any word (3+ letters) repeated more than 5 times.
6. **Gibberish Detection** -- Samples text for excessive consonant sequences (4+ consecutive consonants) to detect keyboard mashing.

### ASCII Art Detector (`ascii_detector.py`)

A secondary filter specifically for detecting ASCII art abuse in reviews:

- **Line Structure Analysis** -- Checks for leading/trailing whitespace combined with special symbols.
- **Dense Symbol Detection** -- Flags lines where >50% of characters are art-specific symbols (`~^|/*+=[]{}<>@#$%&`).
- **Repetition Patterns** -- Detects 4+ consecutive identical non-alphanumeric characters.
- **Indentation Patterns** -- Identifies code-block-like formatting (>40% of lines with leading spaces).
- Multi-factor scoring: flags content when 2+ factors trigger AND text exceeds 100 characters.

### Moderation Outcomes

- **Clean content** -- Published immediately with no restrictions.
- **Soft violations** (medium severity: caps, repetition, gibberish) -- Published with a warning banner, flagged for optional human review.
- **Hard violations** (profanity detected, high/critical severity) -- Blocked from public view, requires explicit admin approval before becoming visible.

---

## Security & Access Control

### Authentication

- **Domain-fenced registration** -- Only `@mmu.edu.my` and `@student.mmu.edu.my` emails are accepted.
- **Email verification** -- Mandatory token-based verification via `Flask-Mail` before account activation.
- **Password requirements** -- Minimum 8 characters, must include uppercase, lowercase, digit, and special character.
- **Password hashing** -- `Bcrypt` with automatic salt generation.
- **Session security** -- `HttpOnly`, `SameSite=Lax`, `Secure` (in production) cookies with 7-day expiry.
- **Temporary passwords** -- Admin-issued password resets generate a UUID-based temporary password, flagged for mandatory change on next login.

### Role-Based Access Control (RBAC)

A strict hierarchical permission model with four tiers:

| Role        | Capabilities |
| ----------- | ------------ |
| **Student** | Read/write/edit own reviews, upvote/downvote, report reviews, submit suggestions and bugs |
| **Moderator (MOD)** | All Student capabilities + hide/delete reviews, resolve reports, pin/unpin reviews, view audit logs |
| **Admin** | All MOD capabilities + manage users (verify, suspend, delete, reset passwords), manage suggestions lifecycle, manage changelogs, manage bugs, view admin dashboard |
| **Owner** | All Admin capabilities + promote/demote Admins, absolute system override, cannot be suspended or deleted |

Permission checks are enforced at both the decorator level (`@admin_required`) and the model level (`can_manage_user()`, `can_change_role()`, `can_delete_user()`, `can_suspend_user()`).

### Content Sanitization

- **Markdown rendering** -- Converts Markdown to HTML via the `markdown` library with `extra` and `codehilite` extensions.
- **XSS prevention** -- All rendered HTML is sanitized through `Bleach` with a strict allowlist of safe tags (`p`, `br`, `strong`, `em`, `code`, `a`, etc.) and attributes (`href`, `title` only on anchors).
- **Input sanitization** -- Raw user input (suggestions, bug reports) is scrubbed via `sanitize_user_content()` which strips all non-whitelisted HTML tags entirely.

### Transport Security

- **HTTPS enforcement** -- Automatic HTTP->HTTPS redirect in production via `enforce_https()` middleware.
- **HSTS headers** -- `Strict-Transport-Security: max-age=31536000; includeSubDomains` on all secure responses.
- **CSRF protection** -- Global `Flask-WTF` CSRF token enforcement on all form submissions.
- **Rate limiting** -- `Flask-Limiter` with configurable per-route limits (e.g., 5 suggestions/hour, 30 votes/minute).
- **Reverse proxy support** -- `ProxyFix` middleware for correct client IP resolution behind load balancers.

### Audit Trail

- Every destructive admin/mod action (verify, suspend, delete, role change, report dismiss, review approve/reject, changelog CRUD, suggestion status change) is permanently logged in the `AuditLog` table with timestamp, actor ID, role, action description, and target type.
- Searchable audit log viewer in the admin panel with filters for email, action, and target type.

---

## Architecture

```text
MMUInsight/
|-- app.py                     # Flask app factory, middleware, route registration, DB bootstrap
|-- models.py                  # SQLAlchemy ORM (User, Lecturer, Review, Reply, Report, Suggestion,
|                              #   SuggestionVote, ReviewVote, ReplyVote, AuditLog, BugReport,
|                              #   BugComment, Changelog, Subject, StatusLog)
|-- extensions.py              # Centralized Flask extension instances (db, bcrypt, login, limiter, csrf, mail)
|-- moderation.py              # Auto-moderation engine (profanity, spam, leetspeak, misspelling detection)
|-- ascii_detector.py          # ASCII art abuse detection via multi-factor scoring
|-- sanitize.py                # XSS sanitization layer (Bleach-based HTML stripping)
|-- audit.py                   # Audit logging helpers for admin/mod actions
|-- lecturer_search.py         # RapidFuzz-powered fuzzy search across lecturer names and emails
|-- reviews.py                 # Reviews blueprint (CRUD, replies, reports, voting, analytics, bio, pinning)
|-- suggestions.py             # Suggestions blueprint (CRUD, voting, admin lifecycle management)
|-- bugs.py                    # Bug reporting blueprint (CRUD, admin triage, comments)
|-- changelog.py               # Changelog blueprint (versioned entries, publish/unpublish)
|-- status.py                  # System status blueprint (public status page, admin metrics dashboard)
|-- auth/
|   |-- __init__.py            # Auth blueprint registration
|   |-- routes.py              # Admin panel (dashboard, users, moderation, audit logs, role management)
|   |-- decorators.py          # @login_required, @admin_required decorators
|   |-- login.py               # Login route handler
|   |-- register.py            # Registration route handler (domain validation, email verification)
|   |-- verify.py              # Email verification token handler
|   |-- logout.py              # Logout route handler
|   |-- reset_password.py      # Password reset flow
|   |-- resend_verification.py # Re-send verification email
|-- templates/                 # 38 Jinja2 HTML templates (base layout + modular pages)
|-- static/
|   |-- css/                   # base.css (light theme) + dark.css (dark mode overrides)
|   |-- js/                    # Client-side JavaScript
|   |-- screenshots/           # README visual assets
|-- translations/
|   |-- en/                    # English translations
|   |-- ms/                    # Malay translations
|   |-- zh/                    # Chinese translations
|-- migrations/                # Alembic database migration scripts
|-- requirements.txt           # Pinned Python dependencies
|-- .env.example               # Environment variable template
|-- Procfile                   # Gunicorn deployment configuration
```

### Data Flow

```text
[Student Browser]
      |
      v
[Flask Route Handler]  -----> [CSRF Validation (Flask-WTF)]
      |
      v
[Content Sanitization (Bleach)]
      |
      v
[Auto-Moderation Pipeline]
  |-- ContentModerator (6 checks)
  |-- AsciiArtDetector (4-factor scoring)
      |
      v
[SQLAlchemy ORM] -----> [SQLite (dev) / PostgreSQL (prod)]
      |
      v
[Audit Logger] -----> [AuditLog table]
      |
      v
[Jinja2 Template] -----> [Rendered HTML + Markdown (Bleach-sanitized)]
```

---

## Installation

### Prerequisites

- Python 3.9+
- `pip` and `venv`
- (Optional) PostgreSQL for production deployments

### Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/KetiakHitam/MMUInsight.git
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

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   ```bash
   cp .env.example .env
   ```

   Open `.env` and set:
   - `SECRET_KEY` -- A cryptographically secure random string (required for CSRF and session signing).
   - `DATABASE_PATH` -- Path to your SQLite database file (defaults to `../mmuinsight_data/mmuinsight.db`).
   - `DATABASE_URL` -- (Optional) PostgreSQL connection string for production.
   - `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD` -- SMTP credentials for email verification.
   - `ADMIN_PASSWORD`, `OWNER_PASSWORD` -- Initial passwords for bootstrap admin accounts.

5. **Initialize the database:**

   ```bash
   python init_db_safe.py
   ```

   This creates all tables, bootstraps the admin/owner accounts, and seeds the lecturer directory from the bundled data file.

6. **Run the application:**

   ```bash
   python app.py
   ```

   The server will start at `http://127.0.0.1:5000`.

---

## Tech Stack

| Layer               | Technology                              | Purpose                                                          |
| ------------------- | --------------------------------------- | ---------------------------------------------------------------- |
| **Web Framework**   | Flask 3.1                               | Routing, session management, blueprint-based modular architecture |
| **ORM**             | SQLAlchemy 2.0 + Flask-Migrate (Alembic)| Object-Relational Mapping and schema migrations                  |
| **Database**        | SQLite (dev) / PostgreSQL (prod)        | Relational data storage for all entities                         |
| **Authentication**  | Flask-Login + Flask-Bcrypt              | Session cookies, RBAC enforcement, salted password hashing       |
| **Search**          | RapidFuzz                               | Fuzzy string matching for lecturer discovery                     |
| **Templating**      | Jinja2                                  | Server-side HTML rendering with template inheritance             |
| **Frontend**        | Vanilla HTML/CSS/JS                     | Lightweight responsive UI, dark mode, AJAX voting                |
| **Security**        | Flask-WTF + Bleach + Flask-Limiter      | CSRF protection, XSS sanitization, rate limiting                 |
| **Email**           | Flask-Mail                              | SMTP-based email verification and password reset                 |
| **Localization**    | Flask-Babel                             | Multi-language support (EN, MS, ZH)                              |
| **Markdown**        | Python-Markdown                         | Rich text rendering for changelogs and bios                      |
| **Deployment**      | Gunicorn + ProxyFix                     | Production WSGI server with reverse proxy support                |

---

## Deployment

The application includes a `Procfile` for deployment on platforms like Railway or Heroku:

```
web: gunicorn app:app
```

For production, set `DATABASE_URL` to your PostgreSQL connection string. The app automatically converts `postgresql://` to `postgresql+psycopg://` for SQLAlchemy 2.0+ compatibility.

HTTPS is enforced automatically when `DEBUG` is not set to `true`.

---

## Contribution Guidelines

Contributions are welcome. Please follow these standards:

- **Migrations** -- Any changes to `models.py` must include an Alembic migration (`flask db migrate -m "description"`). Do not manually alter the database schema.
- **Code Style** -- Python code must conform to PEP 8.
- **i18n** -- All user-facing strings in Python must be wrapped in `gettext()` or `_()`. Jinja2 templates must use `{{ _('String') }}`.
- **Security** -- Do not commit `.env` files, database files, or any credentials. Ensure all user input passes through the sanitization layer.

---

## Limitations

- **Single review per lecturer per student.** Students can only submit one review per lecturer. Subsequent attempts redirect to the existing review for editing.
- **Fuzzy search loads all lecturers into memory.** The current search implementation queries all lecturer records for fuzzy matching. This works well for MMU's faculty size but would need pagination or indexing for significantly larger datasets.
- **Email verification requires SMTP.** Without configured SMTP credentials in `.env`, email verification will fail silently and new accounts cannot be activated.

---

## License

This project is open-source and licensed under the **MIT License**.
