# University of Birmingham Brazilian jiu-jitsu webapp

## Quick local demo

Requires Python 3.10+.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DEMO_MODE = "1"
py -m flask --app app run --debug
```

Open http://127.0.0.1:5000. The local demo creates `instance/demo.sqlite3` and
seeds one future event. Email is skipped unless `MAIL_KEY` is configured.

## Azure PostgreSQL

The app uses PostgreSQL whenever `DATABASE_URL` or the `AZURE_POSTGRES_*`
variables are present. For Azure Database for PostgreSQL Flexible Server, set:

```text
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE?sslmode=require
```

The app creates the three required tables automatically on its first connection.
Do not set `DEMO_MODE` when connecting to PostgreSQL.

## Render deployment

For a public two-week deployment, Render is the easiest option. The
`render.yaml` Blueprint creates a Docker web service and a small PostgreSQL
database in Frankfurt, then supplies the app with the database connection
string automatically.

1. Push this repository to GitHub or GitLab.
2. In Render, choose **New → Blueprint**, select the repository, and deploy
   `render.yaml`.
3. Choose the **Free** plans when prompted.
4. After the first deploy, add your existing domain under the web service's
   **Settings → Custom Domains** and follow Render's DNS instructions.

The account `txc282@student.bham.ac.uk` is configured as the permanent
administrator. Register that email through the normal registration page, then
log in and use **Create event**. Existing accounts with that email are
promoted during the next app startup.

If you ever need to create a different first administrator on Render's Free
plan, add these environment
variables under the service's **Environment** settings before restarting or
redeploying:

```text
INITIAL_ADMIN_EMAIL=your@email.com
INITIAL_ADMIN_PASSWORD=<a-long-unique-password>
INITIAL_ADMIN_FIRST_NAME=Your first name
INITIAL_ADMIN_LAST_NAME=Your last name
```

The app creates or promotes that account to `administrator` during startup.
Log in through the normal `/login` page, confirm that you can see **Create
event**, then remove `INITIAL_ADMIN_PASSWORD` from Render and redeploy. The
administrator role remains in the database.

The free web service can sleep after inactivity, so its first request after a
quiet period may be slow. The free PostgreSQL database is limited to 1 GB,
has no backups, and expires after 30 days; export the data before the expiry
if you need to keep it. Render's free database therefore suits this
short-lived deployment, but should not be treated as the permanent copy of
important sign-ups.

## Raspberry Pi deployment

The cheapest short-term hosting option is to run the app and PostgreSQL on a
Raspberry Pi you already own. Docker publishes only the app on
`127.0.0.1:8080`; PostgreSQL stays on the private Compose network and its data
is stored in the `postgres_data` volume.

On a 64-bit Raspberry Pi OS installation with Docker and Compose installed:

```bash
git clone <your-repository-url> uob-bjj-webapp
cd uob-bjj-webapp
cp .env.example .env
openssl rand -hex 32              # put this value in SECRET_KEY
openssl rand -base64 24           # put this value in POSTGRES_PASSWORD
docker compose up -d --build
docker compose ps
curl http://127.0.0.1:8080/healthz
```

Do not commit `.env`. Back up the database before changing hardware or the
Compose volume:

```bash
docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > backup.sql
```

For a public URL, Cloudflare Tunnel is the simplest low-cost option. Your
domain needs to use Cloudflare DNS. In Cloudflare:

1. Open Zero Trust → Networks → Tunnels and create a tunnel.
2. Add a public hostname, for example `bjj.example.com`, with service
   `http://app:5000`.
3. Copy the tunnel token into `CLOUDFLARE_TUNNEL_TOKEN` in `.env`.
4. Start the tunnel with `docker compose --profile public up -d`.

The tunnel runs inside the Compose network, so the app does not need a public
port or router port-forwarding. Tailscale is suitable when access can be
limited to people/devices in your private tailnet.

## Overview
uob-bjj-webapp is a flask webapp to replace the old sign-up system for the University of Birmingham Brazilian Jiu Jitsu taster sessions during the start of the 2024 academic year.

The current system works by collecting interest/signups via social media which is then recorded manually in a spreadsheet. 
This year there are more taster sessions running so there will be a greater number of students coming to the sessions furthermore the number of committee members managing the sessions has increased which is why I decided to improve the sign-up system.

## My approach
My approach to this project was to create a webapp in which anyone can access key information on the taster session then if they are interested, register an account and sign onto the sessions. 
I discussed with the club president, and we decided that the following key features were needed for the webapp to be useful: 
- A way to create accounts and login to the webapp.
- Committee members can create new events and add information about them.
- Users can sign up to the taster sessions.
- Committee members can then view who has signed up to the session.
  
We also discussed some additional features: 
- Users can register their interest in the session without an account.
- Being able to book a Gi for the session if the user does not have one. 
- reCAPTCHA when creating accounts to prevent automated spam sign ups. 
- Progress tracker/dashboard to see how many sessions you have signed up to.

## Frontend
![mobile-views](https://github.com/user-attachments/assets/6e36c89c-c6f2-4977-9ec0-9fa5bd127f5b)
![desktop-view+account-creation](https://github.com/user-attachments/assets/b1b09e79-fc9c-480d-8963-22729bfb251a)

## Results
- 152 students registered onto the webapp. 
- 2.14 sessions were signed up to on average by users. 
- 88% of the total 300 available spaces were filled.
- 100% of the availiable spaces for the Nogi sessions were filled. 
- 76% of the availiable spaces for the Gi sessions were filled. 
- 90% of the taster Gi’s were booked over all of the sessions.
