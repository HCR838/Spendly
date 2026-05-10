# Plan: Spendly Database Setup (Step 1)

## Context

This step replaces the stub in `database/db.py` with a working SQLite data layer. All future features (auth, profile, expenses) depend on this being correctly in place. No new routes are added; only two files are changed.

---

## Files Changed

- `database/db.py` — implement all three functions from scratch
- `app.py` — add import + startup block

---

## Part 1: `database/db.py`

### `get_db()`

Opens `spendly.db` in the project root, sets `row_factory = sqlite3.Row`, enables `PRAGMA foreign_keys = ON` on every connection.

- `dirname(dirname(__file__))` resolves `database/db.py` → project root.
- PRAGMA must fire on every new connection — SQLite resets it per-connection.

### `init_db()`

Creates `users` and `expenses` tables using `CREATE TABLE IF NOT EXISTS`. Safe to call on every startup. Always commits and closes the connection.

### `seed_db()`

Idempotency guard: `SELECT COUNT(*) FROM users` — returns early if any user exists. Otherwise inserts demo user (werkzeug-hashed password) and 8 sample expenses across all 7 categories (Food ×2, Transport, Bills, Health, Entertainment, Shopping, Other) with dates 2026-05-04 → 2026-05-10.

---

## Part 2: `app.py` changes

```python
from database.db import get_db, init_db, seed_db
```

```python
with app.app_context():
    init_db()
    seed_db()
```

Placed at module level (not inside `if __name__ == "__main__":`) so DB is ready under `python app.py`, `flask run`, and pytest.

---

## Verification

1. `python app.py` — starts on port 5001, no errors.
2. `spendly.db` created in project root.
3. SQLite CLI: `.tables` → `expenses users`; `SELECT COUNT(*) FROM users` → 1; `SELECT COUNT(*) FROM expenses` → 8.
4. Restart server — counts remain 1 / 8 (idempotency confirmed).
5. FK test (Python): `get_db().execute("INSERT INTO expenses (user_id, amount, category, date) VALUES (999, 1.0, 'Food', '2026-05-10')")` raises `sqlite3.IntegrityError`.
