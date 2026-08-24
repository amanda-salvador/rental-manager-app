# Rental Manager

A mobile-first web app for managing a small rental-property portfolio: expenses,
mileage, rent income, maintenance, inspections, showings, tenants, and renter
documents — all organized for an IRS **Schedule E** tax summary at year end.

It runs on free/low-cost infrastructure: a **Streamlit** front end backed by your
own **Google Sheet** (the database) and **Google Drive** (receipt/photo storage).
Your data lives entirely in your Google account — nothing is stored in this code.

## What's inside

| Page | What it does |
|---|---|
| Expense Capture | Log expenses to IRS Schedule E categories; flag tools (80%) and capital improvements |
| Mileage Tracker | Odometer or miles-only trips → deduction at the IRS standard rate |
| Insurance Vault | Read-only policy cards |
| Vendor Directory | Filterable contractor list |
| Tenant Log | Chronological tenant interaction history |
| Tax Summary | Schedule E dashboard by year & property + CSV export for your CPA |
| Lease Renewals | Expiration alerts, color-coded by urgency |
| Inspection Log | Move-in/out, annual, and ad-hoc inspections with photos |
| Showings | Prospective-tenant showing tracker |
| Property Photos | Listing/condition photo storage |
| Rent Income | Rent payments (feeds Schedule E line 3), tracks late fees |
| Vehicle Snapshots | Per-vehicle Jan 1 / Dec 31 odometer for Form 4562 |
| Move-In Packet | One-page PDF welcome packet for new renters |

## Prerequisites

- **Python 3.10+**
- A **Google account** (for Sheets + Drive)
- ~20 minutes for the one-time Google setup below

## Setup

### 1. Get the code

Clone this repository, then:

```bash
cd rental-manager
```

### 2. Create the Google service account

The app signs in to Google as a "service account" (a robot user) so it can read
and write your Sheet and Drive without you logging in each time.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a project.
2. Enable the **Google Sheets API** and **Google Drive API** for that project.
3. Create a **Service Account**, then create a **JSON key** for it and download it.
4. Save that file as `credentials.json` in the project root. *(It's gitignored.)*

### 3. Create your Sheet and Drive folders

1. Create a new **Google Spreadsheet** with one tab per data type. The tab names
   the app expects are listed in `config.py` under `SHEET_TABS`
   (Expenses, Mileage, Maintenance, Insurance, Vendors, Tenants, Inspections,
   Showings, Rent Income, Vehicle Snapshots, Move in info).
2. Create four **Drive folders**: Receipts, Maintenance Photos, Documents, Property Photos.
3. **Share** the spreadsheet and all four folders with your service account's email
   (it looks like `name@project-id.iam.gserviceaccount.com`), giving it **Editor** access.

### 4. Configure your environment

```bash
cp .env.example .env
```

Open `.env` and fill in:

- `SPREADSHEET_ID` — from the spreadsheet URL (`docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`)
- the four `DRIVE_FOLDER_*` IDs — from each folder's URL (`drive.google.com/drive/folders/FOLDER_ID`)
- **`PROPERTIES`**, **`PROPERTY_ADDRESSES`**, **`VEHICLES`**, and the **`LANDLORD_*`**
  contact fields — *this is where you put your own properties and info.* If you
  leave them out, the app falls back to generic placeholder names.
- `APP_PASSWORD` — optional; set it to require a password to open the app.

### 5. Install and run

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

The app opens at <http://localhost:8501>. To use it from your phone on the same
Wi-Fi, visit `http://YOUR_COMPUTER_IP:8501`.

## Making it yours

All of your personal details are driven by `.env` — you never have to edit the
code to set up your own portfolio:

| What | Set in `.env` |
|---|---|
| Property names | `PROPERTIES` (comma-separated) |
| Street addresses | `PROPERTY_ADDRESSES` (JSON; keys must match `PROPERTIES`) |
| Vehicles | `VEHICLES` (comma-separated) |
| Move-in packet contact | `LANDLORD_NAME`, `LANDLORD_PHONE`, `LANDLORD_EMAIL` |
| Form default property | `DEFAULT_EXPENSE_PROPERTY`, `DEFAULT_MILEAGE_PROPERTY` |

IRS categories, vendor trades, inspection types, and the mileage rate live in
`config.py` if you want to adjust them.

## Deploying to the web (optional)

The app runs free on [Streamlit Community Cloud](https://streamlit.io/cloud).
Point it at your fork, set the main file to `app.py`, and add your secrets
(service-account JSON, Drive folder IDs, and the same `PROPERTIES` /
`PROPERTY_ADDRESSES` / `VEHICLES` / `LANDLORD_*` values) in the app's **Secrets**
settings — the app reads from Streamlit secrets when no local `.env` is present.

## Notes on privacy

- Your real data (tenants, rent, expenses) lives in **your** Google Sheet/Drive,
  never in this repo.
- `.env`, `credentials.json`, and any Google token files are gitignored and are
  never committed.
