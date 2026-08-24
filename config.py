# config.py — Single source of truth for all app constants.
# To add a property, IRS category, or vendor trade, edit only this file.
#
# Personal values (property names, street addresses, vehicles, landlord contact)
# are read from your .env file so they never get committed. The defaults below are
# generic placeholders — set the matching vars in .env to use your real values.
# See .env.example for the variable names.

import json
import os

from dotenv import load_dotenv

load_dotenv()


def _secret(key):
    """Read a value from the environment first, then Streamlit Cloud secrets.

    Streamlit is imported lazily so standalone scripts that import this module
    (e.g. the Gmail poller) never pull in a Streamlit dependency.
    """
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets.get(key, "")
    except Exception:
        return ""


def _list_from_env(key, default):
    """Comma-separated env var → list of trimmed strings (falls back to default)."""
    raw = (_secret(key) or "").strip()
    if not raw:
        return list(default)
    return [item.strip() for item in raw.split(",") if item.strip()]


def _json_from_env(key, default):
    """JSON-object env var → dict (falls back to default on missing/invalid)."""
    raw = (_secret(key) or "").strip()
    if not raw:
        return dict(default)
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return dict(default)


# Property display names — set PROPERTIES in .env as a comma-separated list.
PROPERTIES = _list_from_env("PROPERTIES", [
    "Property One",
    "Property Two",
    "Property Three",
    "Property Four",
])

SHEET_TABS = {
    "expenses":       "Expenses",
    "mileage":        "Mileage",
    "maintenance":    "Maintenance",
    "insurance":      "Insurance",
    "vendors":        "Vendors",
    "tenants":        "Tenants",
    "inspections":    "Inspections",
    "showings":       "Showings",
    "rent_income":    "Rent Income",
    "vehicle_snapshots": "Vehicle Snapshots",
    "move_in_info":   "Move in info",
}

# Street addresses — used on move-in packets and renter-facing documents.
# Set PROPERTY_ADDRESSES in .env as a JSON object mapping each property name to its
# address. The keys must match the names in PROPERTIES.
PROPERTY_ADDRESSES = _json_from_env("PROPERTY_ADDRESSES", {
    "Property One":   "123 Example St",
    "Property Two":   "456 Sample Ave",
    "Property Three": "789 Demo Blvd",
    "Property Four":  "101 Placeholder Ln",
})

# Property pre-selected when an entry form first opens. Set these in .env to the
# property you log against most often; anything not in PROPERTIES falls back to
# the first one.
DEFAULT_EXPENSE_PROPERTY = _secret("DEFAULT_EXPENSE_PROPERTY")
DEFAULT_MILEAGE_PROPERTY = _secret("DEFAULT_MILEAGE_PROPERTY")


def default_property_index(name):
    """Index of `name` within PROPERTIES, or 0 when unset or not found."""
    return PROPERTIES.index(name) if name in PROPERTIES else 0


# Landlord contact line shown on renter-facing PDFs (move-in packet footer).
# Set these in .env to use your real contact info.
LANDLORD_NAME  = _secret("LANDLORD_NAME")  or "Property Manager"
LANDLORD_PHONE = _secret("LANDLORD_PHONE") or "(555) 555-5555"
LANDLORD_EMAIL = _secret("LANDLORD_EMAIL") or "manager@example.com"

# IRS Schedule E categories — used on every expense entry
IRS_SCHEDULE_E_CATEGORIES = [
    "Advertising",
    "Auto and Travel",
    "Cleaning and Maintenance",
    "Commissions",
    "Insurance",
    "Legal and Professional Fees",
    "Management Fees",
    "Mortgage Interest",
    "Other Interest",
    "Repairs",
    "Supplies",
    "Taxes",
    "Utilities",
    "Depreciation",
    "Other",
]

# Sentinel category for capital improvements — NOT a Schedule E line.
# Capital improvements (new roof, HVAC, water heater, kitchen remodel, etc.)
# are depreciated over 27.5 years on Form 4562, not deducted as a current expense.
# Keeping this OUT of IRS_SCHEDULE_E_CATEGORIES means tax summary totals stay clean
# and these rows surface in a separate "For Depreciation Schedule" section.
CAPITAL_IMPROVEMENT_CATEGORY = "Capital Improvement"

# IRS standard mileage rate — update each January
IRS_MILEAGE_RATE_2024 = 0.67
IRS_MILEAGE_RATE_2025 = 0.70
IRS_MILEAGE_RATE_2026 = 0.70  # TODO: confirm 2026 rate at irs.gov when announced
IRS_MILEAGE_RATE_CURRENT = IRS_MILEAGE_RATE_2026

MAINTENANCE_STATUSES = ["Open", "In Progress", "Resolved"]
MAINTENANCE_PRIORITIES = ["Low", "Medium", "High", "Emergency"]

VENDOR_TRADES = [
    "Plumber",
    "HVAC",
    "Electrician",
    "Handyman",
    "Roofer",
    "Landscaper",
    "Pest Control",
    "Painter",
    "Appliance Repair",
    "Other",
]

PAYMENT_METHODS = ["Card", "Cash", "Check", "Zelle", "Venmo", "Bank Transfer"]

INSPECTION_TYPES = [
    "Move-In",
    "Move-Out",
    "Annual",
    "Quarterly",
    "Drive-By",
    "Insurance",
    "Other",
]

INSPECTION_CONDITIONS = ["Excellent", "Good", "Fair", "Poor"]

ENTRY_TYPES = [
    "Note",
    "Legal Notice",
    "Payment",
    "Maintenance Request",
    "Lease Renewal",
    "Move-In",
    "Move-Out",
    "Other",
]

MILEAGE_PURPOSES = [
    "Inspection",
    "Repair / Maintenance",
    "Tenant Meeting",
    "Showing / Vacancy",
    "Supply Run",
    "Bank / Financial",
    "Other",
]

# Vehicles used for mileage tracking — set VEHICLES in .env as a comma-separated list.
VEHICLES = _list_from_env("VEHICLES", [
    "Vehicle One",
    "Vehicle Two",
])

# Google Drive folder IDs — fill these in after Google Cloud setup
# See .env.example for the environment variable names
DRIVE_FOLDERS = {
    "receipts":    "REPLACE_WITH_DRIVE_FOLDER_ID",
    "maintenance": "REPLACE_WITH_DRIVE_FOLDER_ID",
    "documents":   "REPLACE_WITH_DRIVE_FOLDER_ID",
    "photos":      "REPLACE_WITH_DRIVE_FOLDER_ID",
}

# Google Spreadsheet ID — fill in after creating the sheet
# See .env.example for the environment variable name
SPREADSHEET_ID = "REPLACE_WITH_SPREADSHEET_ID"

# Sheets API read cache TTL in seconds (5 minutes)
CACHE_TTL_SECONDS = 300
