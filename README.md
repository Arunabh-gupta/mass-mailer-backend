# Mass Mailer Backend

Mass Mailer is a lightweight campaign management app for creating reusable email templates, organizing contact lists, and sending email campaigns to selected recipients.

This backend is built with FastAPI and exposes APIs for contacts, email templates, campaigns, and authentication-backed user ownership.

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Clerk JWT verification

## Prerequisites

- Python 3.10+
- PostgreSQL
- A virtual environment for the backend

## Environment Variables

Create a `.env` file in the backend root.

```env
ENV=local
APP_NAME=Mass Mailer Backend
DEBUG=true
DATABASE_URL=postgresql+psycopg2://resume_user:resume_pass@localhost:5432/mass_mailer
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

AUTH_PROVIDER_NAME=clerk
AUTH_JWT_KEY="-----BEGIN PUBLIC KEY-----
...
-----END PUBLIC KEY-----"
AUTH_JWT_ALGORITHM=RS256
AUTH_JWT_ISSUER=https://your-clerk-instance.clerk.accounts.dev
AUTH_AUTHORIZED_PARTIES=http://localhost:5173
```

Notes:
- `AUTH_JWT_KEY` should be the Clerk public key used to verify frontend session tokens.
- `AUTH_AUTHORIZED_PARTIES` should include the frontend origin that requests the token.

## Local Setup

```bash
cd mass-mailer-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Database Setup

Make sure PostgreSQL is running and the database in `DATABASE_URL` already exists.

Run migrations:

```bash
alembic upgrade head
```

Check current migration version:

```bash
alembic current
```

## Run the Server

```bash
uvicorn app.main:app --reload
```

Default local URL:

```text
http://127.0.0.1:8000
```

Interactive API docs:

```text
http://127.0.0.1:8000/docs
```

## Available Routes

### Health

- `GET /health`
- `GET /db-health`

### Auth

- `GET /auth/me`

### Contacts

- `POST /contacts`
- `GET /contacts`
- `GET /contacts/{contact_id}`
- `PUT /contacts/{contact_id}`
- `DELETE /contacts/{contact_id}`

### Email Templates

- `POST /email_template`
- `GET /email_template`
- `GET /email_template/{template_id}`
- `PUT /email_template/{template_id}`
- `DELETE /email_template/{template_id}`

### Campaigns

- `POST /campaigns`
- `GET /campaigns`
- `GET /campaigns/{campaign_id}`
- `GET /campaigns/{campaign_id}/contacts`
- `PUT /campaigns/{campaign_id}`
- `DELETE /campaigns/{campaign_id}`
- `POST /campaigns/{campaign_id}/send`

## Authentication

The resource routers are protected with bearer-token auth. The frontend signs users in with Clerk and sends a JWT to the backend in the `Authorization` header.

The backend:
- verifies the JWT
- finds or creates an internal user in the `users` table
- scopes contacts, templates, and campaigns to that internal user

## Migrations

Create a new migration:

```bash
alembic revision -m "describe_change"
```

Apply all pending migrations:

```bash
alembic upgrade head
```

Roll back one migration:

```bash
alembic downgrade -1
```
