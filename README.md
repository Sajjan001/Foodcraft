# Food Craft Institute Shahdol — Demo Website (Flask)

A demo, presentation-ready website for **Food Craft Institute Shahdol (M.P.)** built with Flask.
All content not officially confirmed (Principal name, affiliation details, achievements, etc.) is
clearly marked as placeholder / "To be updated by Institute".

## Project Structure

```
FoodCraft/
├── app/
│   ├── __init__.py          # App factory, config, DB init
│   ├── routes.py            # All page routes + form handling
│   ├── models.py            # Admission, ContactMessage (SQLite via SQLAlchemy)
│   ├── data.py               # Courses, notices, gallery, facilities content
│   ├── static/
│   │   ├── css/style.css     # Design system (deep blue + saffron theme)
│   │   ├── js/main.js        # Mobile nav, gallery lightbox/filter, form validation
│   │   └── images/
│   └── templates/
│       ├── base.html
│       ├── partials/         # navbar.html, footer.html
│       ├── legal/            # privacy, terms, disclaimer
│       └── *.html            # home, about, courses, admissions, etc.
├── instance/                 # SQLite DB + uploads (auto-created, gitignored)
├── requirements.txt
├── run.py                    # Local dev entry point / gunicorn target (run:app)
├── passenger_wsgi.py         # Hostinger (Passenger) production entry point
├── render.yaml                # Render Blueprint (web service config)
└── .env.example
```

## Run Locally

```bash
python -m venv venv
venv\Scripts\activate            # Windows
pip install -r requirements.txt
python run.py
```

Visit `http://127.0.0.1:5000`.

## Deploying to Hostinger

Hostinger's hPanel supports Python apps (Business/Cloud hosting plans) via **Setup Python App**.

1. **Upload the project** to your Hostinger account (via File Manager, Git, or FTP) — upload
   everything except `venv/`, `instance/`, and `__pycache__/` (already in `.gitignore`).
2. In **hPanel → Advanced → Python App**, click **Create Application**:
   - Python version: 3.10+ (any version listed is fine)
   - Application root: the folder you uploaded (e.g. `FoodCraft`)
   - Application startup file: `passenger_wsgi.py`
   - Application Entry point: `application`
3. Click **Create**, then open the app's **Configuration** and add `requirements.txt` — Hostinger
   will run `pip install -r requirements.txt` in the app's virtual environment automatically
   (or use the "Run pip install" button if shown).
4. Set the environment variable `SECRET_KEY` (hPanel → your Python app → Environment Variables) to
   a strong random value. Optionally set `INSTITUTE_PHONE_1`, `INSTITUTE_PHONE_2`, `INSTITUTE_EMAIL`
   if you want to override the defaults without editing code.
5. Map your domain/subdomain to the application from the Python App configuration screen.
6. Restart the application from hPanel. The SQLite database and `instance/uploads` folder are
   created automatically on first run — make sure the `instance/` folder is writable (it is, by
   default, under a Hostinger Python app).

> Note: SQLite is fine for this demo. For a real production deployment with concurrent admission
> traffic, consider migrating to MySQL (available on all Hostinger plans) by changing
> `SQLALCHEMY_DATABASE_URI` in `app/__init__.py`.

## Deploying to Render

The repo includes a `render.yaml` Blueprint, so Render can configure the whole service
automatically.

### Option A — Blueprint (recommended)

1. Push this project to a GitHub/GitLab repository.
2. In the [Render Dashboard](https://dashboard.render.com), click **New → Blueprint**, and select
   your repository. Render will read `render.yaml` and pre-fill:
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn run:app --bind 0.0.0.0:$PORT`
   - A random `SECRET_KEY` (auto-generated)
   - `INSTITUTE_PHONE_1`, `INSTITUTE_PHONE_2`, `INSTITUTE_EMAIL` env vars (edit these in
     `render.yaml` or the dashboard before deploying if they need to change)
3. Click **Apply** / **Create Web Service**. Render builds and deploys automatically; every future
   push to the connected branch redeploys the site.

### Option B — Manual Web Service

1. **New → Web Service** → connect your repository.
2. Runtime: **Python 3**
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn run:app --bind 0.0.0.0:$PORT`
5. Add environment variables: `SECRET_KEY` (any strong random string), and optionally
   `INSTITUTE_PHONE_1`, `INSTITUTE_PHONE_2`, `INSTITUTE_EMAIL`.
6. Create the service — Render assigns a `https://<your-service>.onrender.com` URL. A custom domain
   can be attached later from the service's **Settings → Custom Domains**.

### Notes for Render

- **Free plan disk is ephemeral** — the SQLite database (`instance/foodcraft.db`) and any uploaded
  admission photos/documents are wiped on every redeploy or when the service restarts after
  spinning down from inactivity. This is fine for a demo, but for a persistent production system
  either add a Render **persistent disk** (paid, mount it at `instance/`) or migrate to Render's
  managed **PostgreSQL** by changing `SQLALCHEMY_DATABASE_URI` in `app/__init__.py`.
- **Free plan spins down** after 15 minutes of inactivity — the first request after idle time takes
  a few extra seconds to wake the service back up.
- `gunicorn` does not run natively on Windows, so keep using `python run.py` for local development;
  Render's Linux containers run `gunicorn` fine via the start command above.

## Before Going Live (Official Content Checklist)

Search the codebase for the following markers and replace with verified official information:

- `app/data.py` — Principal name/photo, achievements, affiliation/recognition wording
- `app/templates/about.html` — Principal's Message, Government/Department section
- Replace all `placehold.co` image URLs with actual institute photographs
  (hero photo, course images, gallery images, facility images)
- Verify the Google Maps location in `app/templates/contact.html`
- Confirm phone numbers / email in `.env` (or hPanel environment variables)
- Replace `app/templates/legal/*.html` placeholder legal text with institute-approved policies

## Demo Environment Notes

- Admission and Contact form submissions are stored in a local SQLite database
  (`instance/foodcraft.db`) for demonstration purposes only — this is clearly labeled on both
  forms and is **not** an official government submission channel.
- Uploaded files (photograph/documents) are stored in `instance/uploads/`.
