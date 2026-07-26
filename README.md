# Digital Directorate Management System

A scalable Django project skeleton for managing directorate users, requests,
activities, approvals, documents, reports, dashboards, notifications, and audit
logs. This repository currently contains structure and placeholders only; business
logic and data models are intentionally out of scope.

## Technology stack

- Python 3.12+
- Django 6.0
- SQLite for local development
- Django Templates
- Tailwind CSS 4 through `django-tailwind`
- Vanilla JavaScript

## Project structure

```text
config/       Project URLs, ASGI/WSGI, and split settings
apps/         Domain-focused Django applications
templates/    Project-level templates
static/       Project-level CSS, JavaScript, images, and fonts
theme/        Tailwind source and compiled assets
media/        Local user-uploaded files
docs/         Architecture and delivery documentation
scripts/      Project automation scripts
tests/        Project-level tests
```

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

On macOS or Linux, activate the environment with `source .venv/bin/activate`
and copy the environment file with `cp .env.example .env`.

## Database and development server

```powershell
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/> to view the placeholder homepage.

## Tailwind CSS

This project uses Tailwind through `django-tailwind`. Node.js and npm are
required to install and build the frontend dependencies.

```powershell
python manage.py tailwind install
python manage.py tailwind start
python manage.py tailwind build
```

Run `tailwind start` while developing. Run `tailwind build` to produce a
minified stylesheet.

## Checks

```powershell
python manage.py check
python manage.py test
```

## Future roadmap

- Define the domain model and database design.
- Implement authentication and authorization.
- Add request, approval, activity, and document workflows.
- Build notifications, reports, dashboards, and audit logging.
- Add comprehensive automated tests and deployment configuration.
