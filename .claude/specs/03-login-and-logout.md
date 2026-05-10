# Spec: Login and Logout

## Overview

This step wires up the login form to a real `POST /login` route and replaces
the `GET /logout` stub with a working implementation. When a user submits the
login form, Spendly looks up their email, verifies the password hash, starts
a Flask session, and redirects to the landing page. Logout clears the session
and redirects to landing. The nav bar in `base.html` is updated to reflect
session state — showing "Sign in / Get started" for guests and "Logout" for
authenticated users. This is the first step where the UI is aware of who
is logged in.

## Depends on

- Step 01 — Database Setup (`get_db()`, `users` table)
- Step 02 — Registration (`create_user()`, `get_user_by_email()`, `session["user_id"]` convention)

## Routes

- `GET /login` — already renders `login.html`; add `POST` method support — public
- `POST /login` — validates credentials, sets `session["user_id"]`, redirects to landing — public
- `GET /logout` — clears `session["user_id"]`, redirects to landing — public (harmless if not logged in)

## Database changes

No new tables or columns. All needed data is already in the `users` table.

Add one new helper to `database/db.py`:

### `get_user_by_id(user_id)` contract

```python
def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    ...
```

- Opens connection with `get_db()`
- Returns the matching row or `None`
- Closes connection before returning
- Needed by `base.html` (via `g` or template context) to display the logged-in user's name; also required by Step 4 (Profile)

## Templates

- **Modify:** `templates/login.html`
  - Fix hardcoded `action="/login"` → `action="{{ url_for('login') }}"`
  - Re-populate the `email` field on validation failure using `value="{{ email or '' }}"`
  - Do **not** re-populate the password field (security)
  - The `{% if error %}` block is already present — no structural change needed

- **Modify:** `templates/base.html`
  - Replace the static nav links with session-aware conditional:
    - If `session.get('user_id')` → show only a "Sign out" link pointing to `url_for('logout')`
    - Else → show "Sign in" and "Get started" links (current behaviour)

## Files to change

- `app.py` — add `POST` method to `/login` route; add logic to `logout` route; import `check_password_hash` from `werkzeug.security`; import `get_user_by_id` from `database.db`
- `database/db.py` — add `get_user_by_id()` helper
- `templates/login.html` — fix hardcoded action URL; add email value repopulation
- `templates/base.html` — add session-aware nav block

## Files to create

No new files.

## New dependencies

No new dependencies. `werkzeug.security.check_password_hash` is already part of the installed `werkzeug` package.

## Rules for implementation

- No SQLAlchemy or ORMs
- Parameterised queries only (`?` placeholders) — never f-strings in SQL
- Passwords verified with `werkzeug.security.check_password_hash` — never compare plain text
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Login validation: use a **single generic error** for both "email not found" and "wrong password" — never reveal which field is wrong. Error message: `"Invalid email or password."`
- After successful login: set `session["user_id"] = user["id"]` and redirect to `url_for("landing")`
- After validation failure: re-render `login.html` with `error` set and `email` pre-populated
- Logout must use `session.pop("user_id", None)` — do not call `session.clear()` (preserves any future flash messages)
- `get_user_by_id()` goes in `database/db.py` — no inline queries in route functions

### Validation rules for `POST /login`

| Field    | Rule                       | Error message              |
|----------|----------------------------|----------------------------|
| email    | Non-empty after `.strip()` | `"Email is required."`     |
| password | Non-empty                  | `"Password is required."`  |
| credentials | Email exists AND password matches hash | `"Invalid email or password."` |

## Definition of done

- [ ] Submitting the login form with a valid email and correct password sets `session["user_id"]` and redirects to the landing page
- [ ] Submitting with a valid email but wrong password re-renders `login.html` with `"Invalid email or password."` and does not set a session
- [ ] Submitting with an email that does not exist re-renders `login.html` with `"Invalid email or password."` and does not set a session
- [ ] Submitting with an empty email or empty password shows the appropriate field-specific error
- [ ] On validation failure, the email field is pre-filled with the value the user typed
- [ ] Visiting `/logout` clears `session["user_id"]` and redirects to the landing page
- [ ] Visiting `/logout` when not logged in redirects to landing without error
- [ ] The nav bar shows "Sign out" when `session["user_id"]` is set
- [ ] The nav bar shows "Sign in" and "Get started" when no session exists
- [ ] The form `action` uses `url_for('login')`, not a hardcoded string
- [ ] No raw SQL strings are used in route functions — all queries are in `database/db.py`
- [ ] App starts without errors on `python app.py`
- [ ] The demo user (`demo@spendly.com` / `demo123`) can log in successfully
