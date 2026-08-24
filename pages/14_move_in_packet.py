"""
pages/14_move_in_packet.py — Move-In Packet Generator

Generate a one-page PDF welcome / onboarding sheet for new renters.
Pulls utility and insurance links from the "Move in info" Google Sheet tab.
"""

import io
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)

import pathlib

from utils.auth_gate import require_auth
from config import (
    PROPERTIES,
    PROPERTY_ADDRESSES,
    LANDLORD_NAME,
    LANDLORD_PHONE,
    LANDLORD_EMAIL,
)
from sheets.move_in_info import get_move_in_info

_ASSETS = pathlib.Path(__file__).parent.parent / "assets"

require_auth()

st.set_page_config(page_title="Move-In Packet", page_icon="🏠", layout="centered")
st.title("🏠 Move-In Packet Generator")
st.caption("Generate a one-page PDF welcome sheet for new renters.")

# ---------------------------------------------------------------------------
# PDF builder
# ---------------------------------------------------------------------------

_TEAL  = colors.HexColor("#1C97A6")
_GRAY  = colors.HexColor("#777777")
_BODY  = colors.HexColor("#222222")
_DARK  = colors.HexColor("#0a3d42")

_PAGE_W = letter[0] - 1.3 * inch   # usable width (margins 0.65" each side)
_CB_W   = 16                        # checkbox cell width in points
_TEXT_W = _PAGE_W - _CB_W - 6      # text column width


def _styles():
    return {
        "title": ParagraphStyle(
            "PktTitle",
            fontName="Helvetica-Bold",
            fontSize=22,
            textColor=_TEAL,
            alignment=TA_CENTER,
            spaceAfter=4,
            leading=26,
        ),
        "subtitle": ParagraphStyle(
            "PktSubtitle",
            fontName="Helvetica",
            fontSize=10,
            textColor=_GRAY,
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "callout": ParagraphStyle(
            "Callout",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=_DARK,
            leading=14,
        ),
        "item_title": ParagraphStyle(
            "ItemTitle",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=_TEAL,
            leading=13,
            spaceAfter=2,
        ),
        "body": ParagraphStyle(
            "PktBody",
            fontName="Helvetica",
            fontSize=9,
            textColor=_BODY,
            leading=13,
            spaceAfter=2,
        ),
        "footer": ParagraphStyle(
            "PktFooter",
            fontName="Helvetica",
            fontSize=8.5,
            textColor=_GRAY,
            alignment=TA_CENTER,
        ),
        "footer_bold": ParagraphStyle(
            "PktFooterBold",
            fontName="Helvetica-Bold",
            fontSize=9,
            textColor=_BODY,
            alignment=TA_CENTER,
            spaceAfter=2,
        ),
    }


def _link(url: str, label: str | None = None) -> str:
    display = label or url
    return f'<link href="{url}" color="#1C97A6"><u>{display}</u></link>'


def _checklist_row(s, title: str, body: str) -> Table:
    """One checklist row: empty checkbox square on left, title + body on right."""
    checkbox_cell = Table([[""]], colWidths=[_CB_W], rowHeights=[_CB_W])
    checkbox_cell.setStyle(TableStyle([
        ("BOX",           (0, 0), (0, 0), 1, _BODY),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    content = [Paragraph(title, s["item_title"])]
    if body:
        content.append(Paragraph(body, s["body"]))
    row = Table([[checkbox_cell, content]], colWidths=[_CB_W + 6, _TEXT_W])
    row.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return row


def build_pdf(property_name: str, address: str, info: dict,
              deposit_due: str = "", move_in: str = "") -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )

    s = _styles()
    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    story.append(Paragraph(f"Welcome to {address}!", s["title"]))
    story.append(Paragraph(f"{property_name} — Move-In Information", s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=_TEAL, spaceAfter=8))

    # ── Callout box ──────────────────────────────────────────────────────────
    due_phrase = f" <b>by {deposit_due}</b>" if deposit_due else " <b>as soon as possible</b>"
    callout = Table([[Paragraph(
        "<b>Action Required — Secure Your Home</b><br/>"
        "Your lease has been sent via Avail. Please look it over and let us know if you "
        "have any questions or concerns. To hold your spot, please sign and return the "
        f"lease via Avail and pay your deposit(s) and first month's rent{due_phrase}. "
        "Your unit will not be taken off the market until payment is received.",
        s["callout"],
    )]], colWidths=[_PAGE_W])
    callout.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#d6f0f3")),
        ("BOX",           (0, 0), (-1, -1), 1.2, _TEAL),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(callout)
    story.append(Spacer(1, 8))

    # ── Checklist header ─────────────────────────────────────────────────────
    story.append(Paragraph(
        "YOUR MOVE-IN CHECKLIST",
        ParagraphStyle("ChkHead", fontName="Helvetica-Bold", fontSize=9,
                       textColor=_GRAY, spaceAfter=6, leading=11),
    ))

    # ── Pull sheet data ───────────────────────────────────────────────────────
    pet_url      = (info.get("Pet Insurance")        or "").strip()
    water_co     = (info.get("Water")                or "").strip()
    water_url    = (info.get("Water URL")             or "").strip()
    garbage_co   = (info.get("Garbage Company")       or "").strip()
    garbage_url  = (info.get("Garbage")               or "").strip()
    electric_co  = (info.get("Electricity Company")   or "").strip()
    electric_url = (info.get("Electricity URL")       or "").strip()

    def util_line(label, company, url):
        name = f" ({company})" if company else ""
        link = _link(url) if url else "contact your local provider"
        return f"<b>{label}{name}:</b> {link}"

    move_in_phrase  = f" on <b>{move_in}</b>"      if move_in      else " on your move-in date"
    deposit_phrase  = f" by <b>{deposit_due}</b>"  if deposit_due  else " as soon as possible"

    # ── 1. Avail ──────────────────────────────────────────────────────────────
    story.append(_checklist_row(s,
        "Sign Your Lease &amp; Set Up Rent Payment — Avail",
        f"Sign and return your lease and pay your deposit(s){deposit_phrase}. "
        "You will then use Avail to pay rent each month. "
        "<b>There is no additional fee to you</b> — we cover the cost of Avail. "
        f"Visit {_link('https://www.avail.co', 'avail.co')} to create your account.",
    ))

    # ── 2. Pet Policy ─────────────────────────────────────────────────────────
    story.append(_checklist_row(s,
        "Pet Policy (if applicable)",
        "A <b>pet addendum</b> is included in your lease package and attached to your move-in "
        f"email. Please review and sign it before moving in{move_in_phrase}.",
    ))

    # ── 3. Renters Insurance ──────────────────────────────────────────────────
    story.append(_checklist_row(s,
        "Renters Insurance — Required Before Move-In",
        "Provide <b>proof of active renters insurance</b> before receiving your keys"
        f"{move_in_phrase}. Email your policy declaration page to us prior to move-in.",
    ))

    # ── 4. Pet Liability Insurance ────────────────────────────────────────────
    pet_body = (
        "If you have a pet, your policy must include at least "
        "<b>$300,000 in personal liability coverage.</b>"
    )
    if pet_url:
        pet_body += f" Example providers: {_link(pet_url)}."
    story.append(_checklist_row(s,
        "Pet Personal Liability Insurance — $300,000 Minimum (if applicable)",
        pet_body,
    ))

    # ── 5. Utilities ──────────────────────────────────────────────────────────
    util_body = "<br/>".join([
        util_line("Water",       water_co,   water_url),
        util_line("Garbage",     garbage_co, garbage_url),
        util_line("Electricity", electric_co, electric_url),
    ])
    story.append(_checklist_row(s,
        "Set Up Utilities in Your Name",
        util_body,
    ))

    # ── 6. Walk-Through ───────────────────────────────────────────────────────
    story.append(_checklist_row(s,
        "Complete Your Move-In Walk-Through — Within 72 Hours of Move-In",
        "The checklist is <b>attached to this email</b>. Please complete and return it within "
        f"72 hours of receiving your keys{move_in_phrase} — this protects both you and us at move-out.",
    ))

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=_GRAY, spaceAfter=6))
    story.append(Paragraph("Questions? We're here to help.", s["footer_bold"]))
    story.append(Paragraph(
        f"{LANDLORD_NAME} &nbsp;|&nbsp; {LANDLORD_PHONE} &nbsp;|&nbsp; {LANDLORD_EMAIL}",
        s["footer"],
    ))

    doc.build(story)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------

property_name = st.selectbox("Select property", PROPERTIES)
address = PROPERTY_ADDRESSES.get(property_name, property_name)

st.divider()

with st.spinner("Loading move-in info…"):
    try:
        info = get_move_in_info(property_name) or {}
    except Exception as e:
        st.error(f"Could not read Move in info sheet: {e}")
        info = {}

if info:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pet Insurance", "✓" if info.get("Pet Insurance")   else "—")
    col2.metric("Water URL",     "✓" if info.get("Water URL")       else "—")
    col3.metric("Garbage URL",   "✓" if info.get("Garbage")         else "—")
    col4.metric("Electric URL",  "✓" if info.get("Electricity URL") else "—")
else:
    st.warning(
        f"No row found for **{property_name}** in the 'Move in info' tab. "
        "The PDF will generate without utility links.",
        icon="⚠️",
    )

st.divider()

col_a, col_b = st.columns(2)
with col_a:
    deposit_due_date = st.date_input("Lease & deposit due by", value=None)
with col_b:
    move_in_date = st.date_input("Move-in date", value=None)

def _fmt_date(d) -> str:
    return d.strftime("%B %d, %Y").replace(" 0", " ") if d else ""

deposit_due_str = _fmt_date(deposit_due_date)
move_in_str     = _fmt_date(move_in_date)

st.divider()

if st.button("Generate Move-In Packet", use_container_width=True, type="primary"):
    with st.spinner("Building PDF…"):
        pdf_bytes = build_pdf(property_name, address, info, deposit_due_str, move_in_str)
    st.session_state["packet_pdf"]  = pdf_bytes
    st.session_state["packet_prop"] = property_name

if "packet_pdf" in st.session_state:
    st.success("All three documents are ready to download.", icon="✅")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            label="⬇️ Move-In Packet",
            data=st.session_state["packet_pdf"],
            file_name=f"Move-In Packet — {st.session_state['packet_prop']}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    with col2:
        checklist_path = _ASSETS / "WalkThrough Checklist.pdf"
        if checklist_path.exists():
            st.download_button(
                label="⬇️ Walk-Through Checklist",
                data=checklist_path.read_bytes(),
                file_name="Walk-Through Checklist.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.warning("Walk-through checklist not found in assets/.")

    with col3:
        addendum_path = _ASSETS / "Pet Addendum.pdf"
        if addendum_path.exists():
            st.download_button(
                label="⬇️ Pet Addendum",
                data=addendum_path.read_bytes(),
                file_name="Pet Addendum.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.warning("Pet addendum not found in assets/.")
