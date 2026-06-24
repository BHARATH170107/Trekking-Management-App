# Trekking Management Application — Starter Scaffold

This is a **starting skeleton**, not the finished project. It gives you working
authentication (register/login/logout) with three roles, role-protected
dashboards, and the DB models — so you can focus your time on the actual
trek/booking features that the viva will dig into.

## How to run it

```bash
cd trekking_app
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate
pip install -r requirements.txt

python seed.py                  # creates the pre-existing Admin account
python app.py                   # starts the server on http://127.0.0.1:5000
```

Admin login (after running `seed.py`):
- email: `admin@trek.com`
- password: `admin123`

(Change this password / hardcode value before final submission — it's just a
seed default.)

Register as Staff or Trekker from the `/register` page. Staff accounts stay
in a "pending" state until an admin approves them (you still need to build
that approval page — see below).

## What's already built (and why), so you can explain it in your viva

| File | Purpose |
|---|---|
| `config.py` | DB path + secret key |
| `extensions.py` | `db` and `login_manager` instances, created separately to avoid circular imports between `models.py` and `app.py` |
| `models.py` | `User` (role column instead of 3 separate tables — simpler), `Trek`, `Booking` |
| `decorators.py` | `role_required()` — a custom decorator that returns 403 if `current_user.role` doesn't match |
| `routes/auth.py` | register / login / logout logic, including staff-approval and blacklist checks |
| `routes/admin.py`, `staff.py`, `trekker.py` | one dashboard route per role, each protected by `@login_required` + `@role_required(...)` |
| `seed.py` | creates the one pre-existing Admin row (run once) |
| `app.py` | Flask app factory — registers blueprints, calls `db.create_all()` so the DB is built **programmatically** (per the project rules) |

Every table is created via SQLAlchemy model code, not by hand in DB Browser —
that satisfies the "database must be created programmatically" requirement.

## What you still need to build

This is intentionally incomplete — these are the parts that show your actual
understanding, so build them yourself (ask me for help on any piece, but make
sure you can explain it after):

**Admin**
- [ ] Create / edit / delete treks
- [ ] List staff with pending status, approve or blacklist them
- [ ] Assign a staff member to a trek (sets `assigned_staff_id`)
- [ ] List/search users, staff, treks by name/ID
- [ ] Blacklist trekkers
- [ ] View all bookings

**Trek Staff**
- [ ] Update a trek's `available_slots` and `status` (Open/Closed)
- [ ] View list of trekkers booked on their trek
- [ ] Mark trek as started/completed

**Trekker**
- [ ] Search/filter treks by difficulty and location
- [ ] Book a trek — **must check `available_slots > 0` before creating a Booking
      and decrement it on success** (this is the overbooking-prevention logic
      the spec calls out explicitly)
- [ ] View booking status / history
- [ ] Edit profile

**Polish**
- [ ] Better Bootstrap styling on the stub templates
- [ ] Form validation (server-side, inside the Flask routes)
- [ ] ER diagram of the 3 tables for your report
- [ ] Project report (≤5 pages) + AI/LLM usage declaration + presentation video

## A note on the "Available/Optional" features
The spec mentions optional things like Flask-RESTful API endpoints and charts.
Don't add these until the core CRUD/booking flow above works end-to-end —
a working simple app beats a half-working complex one, both for grading and
for the viva.
