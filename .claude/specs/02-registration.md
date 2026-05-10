# Spec: Registration

## Overview

This step wires up the registration form that already exists in `register.html`
to a real `POST /register` route. When a visitor submits the form, Spendly
validates their input, checks for duplicate emails, hashes the password, inserts
the new user into the database, starts a Flask session, and redirects them to the
landing page. It also establishes the `secret_key` required for all session-based
features from this point forward.

## Depends on

- Step 01 — Database Setup (`get_db()`, `init_db()`, `users` table)

## Routes

- `GET /register` — already renders `register.html` (no change needed to handler)
- `POST /register` — validates form data, creates user, starts session, redirects — public

## Database changes

No new tables or columns. The existing `users` table (id, name, email,
password_hash, created_at) covers everything needed.

## Templates

- **Modify:** `templates/register.html`
  - Fix hardcoded `action="/register"` → `action="{{ url_for('register') }}"`
  - Re-populate `name` and `email` fields on validation failure using `value="{{ request.form.get('name', '') }}"` so the user does not have to retype
  - The `{% if error %}` block is already present — no structural change needed

- **Modify:** `templates/base.html`
  - No changes required at this step (nav state for logged-in users is Step 3/4)

## Files to change

- `app.py` — add `POST` method to `/register` route; import `session`, `redirect`,
  `url_for`, `request`, `flash` from flask; set `app.secret_key`; call new db helpers
- `database/db.py` — add `get_user_by_email()` and `create_user()` helpers
- `templates/register.html` — fix hardcoded action URL; add value re-population

## Files to create

No new files.

## New dependencies

No new dependencies.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only (`?` placeholders) — never f-strings in SQL
- Passwords hashed with `werkzeug.security.generate_password_hash` — never stored plain
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- `app.secret_key` must be set before any session use; use a hardcoded dev string
  (`"spendly-dev-secret"`) — a later step can move it to an env var
- DB helpers go in `database/db.py` only — no inline queries in route functions
- Use `abort(500)` if an unexpected DB error occurs; do not return raw error strings
- After successful registration: set `session["user_id"]` and redirect to `url_for("landing")`
- After validation failure: re-render `register.html` with the `error` variable set

### `get_user_by_email(email)` contract

```python
def get_user_by_email(email: str) -> sqlite3.Row | None:
    ...
```

- Opens connection with `get_db()`
- Returns the matching row or `None`
- Closes connection before returning

### `create_user(name, email, password)` contract

```python
def create_user(name: str, email: str, password: str) -> int:
    ...
```

- Hashes the password internally with `generate_password_hash`
- Inserts the user with a parameterised `INSERT`
- Returns the new `lastrowid`
- Closes connection before returning

### Validation rules (enforce in the route, not the DB helper)

| Field    | Rule                                      | Error message                         |
|----------|-------------------------------------------|---------------------------------------|
| name     | Non-empty after `.strip()`                | "Name is required."                   |
| email    | Non-empty after `.strip()`                | "Email is required."                  |
| email    | Not already in `users` table              | "An account with that email already exists." |
| password | At least 8 characters                    | "Password must be at least 8 characters." |

## Definition of done

- [ ] Submitting the form with valid data creates a row in the `users` table with a
      hashed (not plain-text) password
- [ ] After successful registration, `session["user_id"]` is set and the browser
      redirects to the landing page
- [ ] Submitting with an email that already exists re-renders the form with the error
      "An account with that email already exists." and does not insert a duplicate row
- [ ] Submitting with a password shorter than 8 characters shows the appropriate error
- [ ] Submitting with an empty name or email shows the appropriate error
- [ ] On validation failure, the `name` and `email` fields are pre-filled with the
      values the user already typed
- [ ] The form `action` uses `url_for('register')`, not a hardcoded string
- [ ] No raw SQL strings are used in route functions — all queries are in `database/db.py`
- [ ] App starts without errors on `python app.py`
