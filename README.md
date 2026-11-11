# Mission Control API

A RESTful backend service for flight directors to plan, track, and manage space exploration missions and orbital operations.

---

## Core Features (v1)
- **Mission Planning**: Create and manage space missions with destination targets and launch windows.
- **Flight Director Isolation**: User-owned missions with authenticated access controls.
- **Environment Configuration**: Multi-environment config management supporting development, testing, and production.

---

## Getting Started

### 1. Setup & Installation

Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/WPratt0211/BE106.git
cd BE106
```

Create and activate a Python virtual environment:

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (Command Prompt)
# .venv\Scripts\activate.bat
```

Install the project dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python wsgi.py
```
Or run using Flask CLI:
```bash
flask --app wsgi:app run
```

---

### 2. Environment Variables

Copy the provided example template into a local `.env` file:

```bash
cp .env.example .env
```

Configure the following variables in `.env`:

| Variable | Description | Example / Placeholder |
|---|---|---|
| `FLASK_CONFIG` | Specifies active environment (`development`, `testing`, `production`) | `development` |
| `DATABASE_URL` | SQLAlchemy connection URI for the application database | `postgresql://CHANGE_ME_USER:CHANGE_ME_PASSWORD@CHANGE_ME_HOST:5432/CHANGE_ME_DB` |
| `JWT_SECRET` | Secret key used for signing and verifying JWT authentication tokens | `CHANGE_ME_JWT_SECRET` |

---

### 3. Database Migrations

Initialize and apply database migrations using Flask-Migrate.

Run these commands after models are defined in this project:

```bash
# Initialize migrations directory (first time only)
flask --app wsgi:app db init


# Generate a migration script based on model definitions
flask --app wsgi:app db migrate -m "Initial migration"

# Apply migrations to update the database schema
flask --app wsgi:app db upgrade
```
