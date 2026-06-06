# AGENTS.md

## Cursor Cloud specific instructions

### Product overview

IconProperty is a minimal Django 6.0.6 scaffold (`django-admin startproject`). The only user-facing surface today is **Django Admin** at `/admin/`. There is no custom app logic, frontend, or API layer yet.

### Virtual environment

The committed `venv/` directory was created on macOS and **does not work on Linux** (its `pyvenv.cfg` points at macOS paths). Use a local `.venv` instead:

```bash
python3 -m venv .venv
.venv/bin/pip install 'django==6.0.6'
```

Fresh Ubuntu VMs need the system package `python3.12-venv` before `python3 -m venv` works (`sudo apt-get install -y python3.12-venv`). This is a one-time VM setup step, not part of the update script.

### Running the app

```bash
.venv/bin/python manage.py migrate
DJANGO_SUPERUSER_PASSWORD=admin123 .venv/bin/python manage.py createsuperuser --noinput --username admin --email admin@example.com
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

- Admin UI: http://127.0.0.1:8000/admin/
- Dev superuser (created during setup): `admin` / `admin123`
- Database: SQLite (`db.sqlite3` in repo root, created by `migrate`)

### Lint / test

- **Lint:** No linter configuration (no `ruff`, `flake8`, `pylint`, etc.) in this repo.
- **Tests:** `python manage.py test` runs successfully but finds **0 tests** (no test modules exist yet).
- **Checks:** `python manage.py check` validates Django configuration.

### Services

Only one service is required for end-to-end development:

| Service | Command | Port |
|---------|---------|------|
| Django dev server | `.venv/bin/python manage.py runserver 0.0.0.0:8000` | 8000 |

No Docker, Redis, Celery, or external database is configured.
