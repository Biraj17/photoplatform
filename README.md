# PhotoPlat

A photographer booking marketplace for Nepal — browse portfolios by style and city, compare pricing, and send booking requests directly to photographers.

**Live site:** https://photoplat.onrender.com/

## Features

**For clients**
- Browse photographers by specialty (Wedding, Portrait, Family, Fashion, Travel), city, and name
- View a photographer's portfolio, completed projects, rating, and current offers
- Save favorite photographers to a personal list
- Send a booking request with shoot date, package, and phone number — only available for identity-verified photographers
- Get emailed automatically when a photographer accepts or declines a request

**For photographers**
- Public profile with portfolio images, project history, pricing, and bio
- KYC identity verification (citizenship number + document photos), reviewed by an admin
- A "Verified" badge unlocks once KYC is approved — required before clients can book or see the photographer's offers
- Publish and cancel time-limited promotional offers
- Add and remove completed projects
- Accept or reject incoming booking requests, which notifies the client by email

**Admin**
- Full Django admin for managing photographers, bookings, offers, and portfolio content
- Dedicated KYC review workflow: bulk verify/reject actions, document photo previews, and a restricted "KYC Reviewer" role that can only update verification status — nothing else
- `create_kyc_reviewer` management command to provision a review-only staff account

## Tech stack

- **Backend:** Django 6
- **Database:** PostgreSQL (production) / SQLite (local dev)
- **Media storage:** Cloudinary (production) / local disk (local dev)
- **Email:** SMTP (Gmail) for booking decision notifications
- **Static files:** WhiteNoise
- **Styling:** Tailwind CSS (CDN) with a custom editorial theme
- **Hosting:** Render (web service + managed Postgres)

## Local setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

### Optional local environment variables

Everything works locally with sane defaults (SQLite, local media storage, console email backend). To exercise the production integrations locally, set:

| Variable | Purpose |
|---|---|
| `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` | Persistent media storage |
| `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Real SMTP email delivery |
| `DATABASE_URL` | Point at a Postgres instance instead of SQLite |

## Deployment

Deployed on [Render](https://render.com) via `render.yaml` (Infrastructure as Code) — a free web service plus a free managed Postgres database, wired together automatically. Pushing to `main` triggers an automatic redeploy.

## Project structure

- `main/` — public-facing marketplace: home, photographer listings/profiles, offers, bookings, static assets
- `accounts/` — photographer auth, dashboard, KYC, and profile management
- `project/` — Django settings, URL routing, WSGI entrypoint
