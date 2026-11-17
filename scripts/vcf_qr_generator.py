#!/usr/bin/env python3
"""
VCF QR Code Generator
Converts contact information from CSV into standard vCard (VCF 3.0) QR codes formatted as SVG files.
Supports both CLI batch processing and an instant lightweight HTTP API server.
"""

import argparse
import csv
import io
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import zipfile
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, List, Optional, Tuple

try:
    import segno
except ImportError:
    segno = None

# -----------------------------------------------------------------------------
# Configuration and Header Aliases
# -----------------------------------------------------------------------------

HEADER_ALIASES = {
    "filename": [
        "filename", "file_name", "output_filename", "svg_filename", "svg_name", "qr_name", "file"
    ],
    "first_name": [
        "first_name", "firstname", "first", "given_name", "givenname", "fname"
    ],
    "last_name": [
        "last_name", "lastname", "last", "surname", "family_name", "familyname", "lname"
    ],
    "prefix": [
        "prefix", "salutation", "title_prefix", "honorific_prefix"
    ],
    "suffix": [
        "suffix", "honorific_suffix"
    ],
    "title": [
        "title", "job_title", "jobtitle", "position", "role", "designation", "occupation"
    ],
    "company": [
        "company", "organization", "organisation", "org", "company_name", "companyname", "employer"
    ],
    "department": [
        "department", "dept", "division", "team", "unit"
    ],
    "work_phone": [
        "work_phone", "workphone", "office_phone", "officephone", "phone_work", "tel_work",
        "phone", "telephone", "phone_number", "phonenumber"
    ],
    "mobile_phone": [
        "mobile_phone", "mobilephone", "cell_phone", "cellphone", "mobile", "cell", "tel_cell"
    ],
    "fax": [
        "fax", "fax_number", "work_fax"
    ],
    "email": [
        "email", "work_email", "workemail", "email_address", "e_mail", "mail"
    ],
    "personal_email": [
        "personal_email", "home_email", "personalemail", "email_home", "other_email"
    ],
    "company_website": [
        "company_website", "website", "url", "company_url", "web", "homepage", "web_page", "site"
    ],
    "street_address": [
        "street_address", "street", "address", "company_address", "work_address",
        "address_line_1", "address1", "streetaddress"
    ],
    "city": [
        "city", "town", "locality"
    ],
    "state": [
        "state", "province", "region"
    ],
    "postal_code": [
        "postal_code", "zip", "zipcode", "zip_code", "postcode"
    ],
    "country": [
        "country", "nation"
    ],
    "linkedin": [
        "linkedin", "linkedin_url", "linkedin_profile", "linkedinurl"
    ],
    "twitter": [
        "twitter", "x", "twitter_url", "x_url"
    ],
    "github": [
        "github", "github_url", "github_profile"
    ],
    "notes": [
        "notes", "note", "comment", "comments", "bio", "description"
    ],
}


def normalize_header(h: str) -> str:
    """Normalize a header string to alphanumeric lowercase."""
    return re.sub(r"[^a-z0-9]", "", str(h).lower())


LOOKUP_HEADER_MAP: Dict[str, str] = {}
for canonical, aliases in HEADER_ALIASES.items():
    for alias in aliases:
        LOOKUP_HEADER_MAP[normalize_header(alias)] = canonical


def ensure_segno():
    """Ensure segno is installed before proceeding."""
    global segno
    if segno is None:
        sys.stderr.write(
            "\n[Error] The 'segno' package is required to generate SVG QR codes.\n"
            "Please install it using:\n\n"
            "    pip install segno\n"
            "    # or run using the included script: ./scripts/run.sh\n\n"
        )
        sys.exit(1)


def escape_vcard_value(val: str) -> str:
    """Escape special characters in vCard text fields per RFC 2426/RFC 6350."""
    if not val:
        return ""
    val = str(val).replace("\\", "\\\\")
    val = val.replace(";", "\\;").replace(",", "\\,")
    val = val.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")
    return val.strip()


def build_vcard_3(contact: Dict[str, str]) -> str:
    """
    Constructs a standards-compliant vCard 3.0 string.
    Any empty or missing field is completely discarded.
    """
    lines: List[str] = ["BEGIN:VCARD", "VERSION:3.0"]

    # Name fields
    last = contact.get("last_name", "").strip()
    first = contact.get("first_name", "").strip()
    prefix = contact.get("prefix", "").strip()
    suffix = contact.get("suffix", "").strip()

    has_name = any([last, first, prefix, suffix])
    if has_name:
        # N:LastName;FirstName;MiddleName;Prefix;Suffix
        n_val = f"{escape_vcard_value(last)};{escape_vcard_value(first)};;{escape_vcard_value(prefix)};{escape_vcard_value(suffix)}"
        lines.append(f"N:{n_val}")

        # Formatted Name (FN)
        fn_parts = [p for p in [prefix, first, last, suffix] if p]
        fn_val = " ".join(fn_parts)
        lines.append(f"FN:{escape_vcard_value(fn_val)}")
    else:
        # If no personal name, check company
        company = contact.get("company", "").strip()
        if company:
            lines.append(f"FN:{escape_vcard_value(company)}")

    # Organization / Company & Department
    company = contact.get("company", "").strip()
    dept = contact.get("department", "").strip()
    if company or dept:
        org_val = escape_vcard_value(company)
        if dept:
            org_val += f";{escape_vcard_value(dept)}"
        lines.append(f"ORG:{org_val}")

    # Title / Position
    title = contact.get("title", "").strip()
    if title:
        lines.append(f"TITLE:{escape_vcard_value(title)}")

    # Telephones
    work_phone = contact.get("work_phone", "").strip()
    if work_phone:
        lines.append(f"TEL;TYPE=WORK,VOICE:{escape_vcard_value(work_phone)}")

    mobile_phone = contact.get("mobile_phone", "").strip()
    if mobile_phone:
        lines.append(f"TEL;TYPE=CELL,VOICE:{escape_vcard_value(mobile_phone)}")

    fax = contact.get("fax", "").strip()
    if fax:
        lines.append(f"TEL;TYPE=FAX:{escape_vcard_value(fax)}")

    # Emails
    email = contact.get("email", "").strip()
    if email:
        lines.append(f"EMAIL;TYPE=WORK,INTERNET:{escape_vcard_value(email)}")

    personal_email = contact.get("personal_email", "").strip()
    if personal_email:
        lines.append(f"EMAIL;TYPE=HOME,INTERNET:{escape_vcard_value(personal_email)}")

    # Website / URL
    website = contact.get("company_website", "").strip()
    if website:
        if not re.match(r"^https?://", website, re.IGNORECASE):
            website = "https://" + website
        lines.append(f"URL:{website}")

    # Address: ADR;TYPE=WORK:;;Street;City;State;Zip;Country
    street = contact.get("street_address", "").strip()
    city = contact.get("city", "").strip()
    state = contact.get("state", "").strip()
    postal = contact.get("postal_code", "").strip()
    country = contact.get("country", "").strip()

    if any([street, city, state, postal, country]):
        adr_val = (
            f";;{escape_vcard_value(street)};{escape_vcard_value(city)};"
            f"{escape_vcard_value(state)};{escape_vcard_value(postal)};{escape_vcard_value(country)}"
        )
        lines.append(f"ADR;TYPE=WORK:{adr_val}")

    # Social Profiles: LinkedIn, Twitter, GitHub
    linkedin = contact.get("linkedin", "").strip()
    if linkedin:
        if not re.match(r"^https?://", linkedin, re.IGNORECASE):
            linkedin = "https://" + linkedin
        lines.append(f"X-SOCIALPROFILE;type=linkedin:{linkedin}")
        lines.append(f"URL;TYPE=LinkedIn:{linkedin}")

    twitter = contact.get("twitter", "").strip()
    if twitter:
        if not re.match(r"^https?://", twitter, re.IGNORECASE):
            twitter = "https://" + twitter
        lines.append(f"X-SOCIALPROFILE;type=twitter:{twitter}")

    github = contact.get("github", "").strip()
    if github:
        if not re.match(r"^https?://", github, re.IGNORECASE):
            github = "https://" + github
        lines.append(f"URL;TYPE=GitHub:{github}")

    # Notes
    notes = contact.get("notes", "").strip()
    if notes:
        lines.append(f"NOTE:{escape_vcard_value(notes)}")

    lines.append("END:VCARD")
    return "\r\n".join(lines)


def slugify(text: str) -> str:
    """Sanitize strings into safe file names."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "_", text).strip("-_")


def generate_filename(contact: Dict[str, str], index: int) -> str:
    """Generate a readable, unique base filename for a contact."""
    custom = contact.get("filename", "").strip()
    if custom:
        if custom.lower().endswith(".svg"):
            custom = custom[:-4]
        cleaned = slugify(custom)
        if cleaned:
            return cleaned

    first = slugify(contact.get("first_name", ""))
    last = slugify(contact.get("last_name", ""))
    company = slugify(contact.get("company", ""))

    parts = [p for p in [first, last, company] if p]
    if parts:
        return "_".join(parts)
    return f"contact_{index:03d}"


def parse_csv_stream(stream: io.TextIOBase) -> List[Dict[str, str]]:
    """Parse CSV data into list of normalized contact dictionaries."""
    reader = csv.reader(stream)
    try:
        raw_headers = next(reader)
    except StopIteration:
        return []

    # Map raw CSV header column index to canonical field name
    header_mapping: Dict[int, str] = {}
    for idx, h in enumerate(raw_headers):
        clean = normalize_header(h)
        if clean in LOOKUP_HEADER_MAP:
            header_mapping[idx] = LOOKUP_HEADER_MAP[clean]
        else:
            header_mapping[idx] = clean

    contacts: List[Dict[str, str]] = []
    for row in reader:
        if not row or not any(field.strip() for field in row):
            continue
        contact: Dict[str, str] = {}
        for col_idx, val in enumerate(row):
            if col_idx in header_mapping:
                clean_val = val.strip()
                if clean_val:
                    contact[header_mapping[col_idx]] = clean_val
        if contact:
            contacts.append(contact)

    return contacts


def generate_svg_string(
    vcard_text: str,
    scale: int = 5,
    border: int = 2,
    dark: str = "#000000",
    light: Optional[str] = "#FFFFFF",
) -> str:
    """Generates an SVG QR code string from vCard content."""
    ensure_segno()
    qr = segno.make(vcard_text, error="m")
    out = io.BytesIO()
    qr.save(out, kind="svg", scale=scale, border=border, dark=dark, light=light)
    return out.getvalue().decode("utf-8")


# -----------------------------------------------------------------------------
# Batch Processing Logic
# -----------------------------------------------------------------------------

def process_contacts_csv(
    csv_file_path: str,
    output_dir: str,
    scale: int = 5,
    border: int = 2,
    dark: str = "#000000",
    light: Optional[str] = "#FFFFFF",
    save_vcf: bool = False,
) -> List[Tuple[str, str]]:
    """Reads a CSV file and writes SVG QR codes into output_dir."""
    ensure_segno()
    os.makedirs(output_dir, exist_ok=True)

    with open(csv_file_path, "r", encoding="utf-8-sig") as f:
        contacts = parse_csv_stream(f)

    results: List[Tuple[str, str]] = []
    used_names: Dict[str, int] = {}

    for idx, contact in enumerate(contacts, start=1):
        base_name = generate_filename(contact, idx)
        if base_name in used_names:
            used_names[base_name] += 1
            filename = f"{base_name}_{used_names[base_name]}"
        else:
            used_names[base_name] = 1
            filename = base_name

        vcard_text = build_vcard_3(contact)
        svg_filename = f"{filename}.svg"
        svg_filepath = os.path.join(output_dir, svg_filename)

        svg_content = generate_svg_string(
            vcard_text, scale=scale, border=border, dark=dark, light=light
        )

        with open(svg_filepath, "w", encoding="utf-8") as svg_out:
            svg_out.write(svg_content)

        if save_vcf:
            vcf_filepath = os.path.join(output_dir, f"{filename}.vcf")
            with open(vcf_filepath, "w", encoding="utf-8") as vcf_out:
                vcf_out.write(vcard_text)

        results.append((svg_filename, vcard_text))

    return results


def process_csv_to_zip(
    csv_text: str,
    scale: int = 5,
    border: int = 2,
    dark: str = "#000000",
    light: Optional[str] = "#FFFFFF",
    include_vcf: bool = False,
) -> bytes:
    """Processes CSV content in memory and returns a ZIP file containing SVG QRs."""
    ensure_segno()
    stream = io.StringIO(csv_text)
    contacts = parse_csv_stream(stream)

    zip_buffer = io.BytesIO()
    used_names: Dict[str, int] = {}

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for idx, contact in enumerate(contacts, start=1):
            base_name = generate_filename(contact, idx)
            if base_name in used_names:
                used_names[base_name] += 1
                filename = f"{base_name}_{used_names[base_name]}"
            else:
                used_names[base_name] = 1
                filename = base_name

            vcard_text = build_vcard_3(contact)
            svg_content = generate_svg_string(
                vcard_text, scale=scale, border=border, dark=dark, light=light
            )
            zf.writestr(f"{filename}.svg", svg_content)
            if include_vcf:
                zf.writestr(f"{filename}.vcf", vcard_text)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


# -----------------------------------------------------------------------------
# Embedded Web Interface & Lightweight API Handler
# -----------------------------------------------------------------------------

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Kewargen - Batch VCF QR Code Generator</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Recursive:slnt,wght,CASL,CRSV,MONO@-15..0,300..1000,0..1,0..1,0..1&display=swap" rel="stylesheet" />
  <style>
    * {
      box-sizing: border-box;
      font-family: "Recursive", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    html, body {
      margin: 0;
      padding: 0;
      height: 100%;
    }
    body {
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      background: linear-gradient(135deg, #fffbeb 0%, #fafaf9 40%, rgba(253, 230, 138, 0.35) 100%);
      min-height: 100dvh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
    }
    .card {
      width: 100%;
      max-width: 580px;
      background: #ffffff;
      border-radius: 1.25rem;
      border: 1px solid rgba(231, 229, 228, 0.6);
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
                  0 8px 10px -6px rgba(0, 0, 0, 0.1),
                  0 4px 12px rgba(120, 53, 15, 0.08);
      padding: 2rem;
      animation: cardUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes cardUp {
      from { opacity: 0; transform: translateY(14px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
      gap: 1rem;
    }
    .app-title {
      font-size: 1.5rem;
      font-weight: 700;
      color: #1c1917;
      letter-spacing: -0.02em;
      margin: 0;
    }
    .app-subtitle {
      font-size: 0.875rem;
      color: #78716c;
      margin-top: 0.25rem;
    }
    .btn-secondary {
      display: inline-flex;
      align-items: center;
      gap: 0.375rem;
      padding: 0.45rem 0.85rem;
      font-size: 0.75rem;
      font-weight: 600;
      border-radius: 0.5rem;
      border: 1px solid #e7e5e4;
      color: #57534e;
      background: #fafaf9;
      text-decoration: none;
      transition: all 0.2s ease;
      cursor: pointer;
    }
    .btn-secondary:hover {
      background: #f5f5f4;
      border-color: #d6d3d1;
      color: #1c1917;
    }
    .dropzone {
      border: 2px dashed #d6d3d1;
      border-radius: 0.875rem;
      background: #fafaf9;
      padding: 3rem 1.5rem;
      text-align: center;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
    .dropzone:hover, .dropzone.dragover {
      border-color: #d97706;
      background: rgba(253, 230, 138, 0.15);
    }
    .dropzone-icon-wrap {
      width: 3.75rem;
      height: 3.75rem;
      border-radius: 0.875rem;
      background: #ffffff;
      border: 1px solid #e7e5e4;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 0.875rem;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .dropzone svg {
      width: 1.75rem;
      height: 1.75rem;
      stroke: #d97706;
    }
    .dropzone-title {
      font-size: 0.9375rem;
      font-weight: 500;
      color: #1c1917;
      margin: 0;
    }
    .dropzone-sub {
      font-size: 0.8125rem;
      color: #a8a29e;
      margin-top: 0.35rem;
    }
    .checkbox-row {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.875rem;
      color: #57534e;
      cursor: pointer;
      margin-top: 1.25rem;
      user-select: none;
    }
    .checkbox-row input {
      accent-color: #d97706;
      width: 1.1rem;
      height: 1.1rem;
      cursor: pointer;
    }
    .generate-btn {
      width: 100%;
      min-height: 48px;
      padding: 0.75rem 1.5rem;
      font-size: 0.9375rem;
      font-weight: 600;
      color: #fff;
      border: none;
      border-radius: 0.75rem;
      background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
      cursor: pointer;
      transition: all 0.25s ease;
      box-shadow: 0 2px 8px rgba(180, 83, 9, 0.3);
      position: relative;
      overflow: hidden;
      margin-top: 1.25rem;
      font-family: inherit;
      -webkit-tap-highlight-color: transparent;
    }
    .generate-btn::after {
      content: "";
      position: absolute;
      inset: 0;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, transparent 60%);
      pointer-events: none;
    }
    .generate-btn:hover:not(:disabled) {
      transform: translateY(-1px);
      box-shadow: 0 4px 16px rgba(180, 83, 9, 0.35);
    }
    .generate-btn:active:not(:disabled) {
      transform: translateY(0);
      box-shadow: 0 1px 4px rgba(180, 83, 9, 0.3);
    }
    .generate-btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
    .status {
      margin-top: 1rem;
      padding: 0.75rem 1rem;
      border-radius: 0.5rem;
      font-size: 0.875rem;
      display: none;
      line-height: 1.4;
    }
    .status.info {
      display: block;
      background: #fffbeb;
      border: 1px solid #fde68a;
      color: #92400e;
    }
    .status.error {
      display: block;
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #b91c1c;
    }
    .status.success {
      display: block;
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      color: #166534;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="card-header">
      <div>
        <h1 class="app-title">Kewargen Batch QR</h1>
        <p class="app-subtitle">Convert contacts CSV into SVG VCF QR codes</p>
      </div>
      <a href="/api/template" class="btn-secondary" download="contacts_template.csv">
        <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
        </svg>
        CSV Template
      </a>
    </div>

    <div class="dropzone" id="dropzone">
      <div class="dropzone-icon-wrap">
        <svg fill="none" viewBox="0 0 24 24" stroke-width="1.75" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
        </svg>
      </div>
      <p class="dropzone-title" id="dropTitle">Drag & drop your contacts <strong>.csv</strong> here</p>
      <p class="dropzone-sub" id="dropSub">or click to browse your files</p>
      <input type="file" id="fileInput" accept=".csv,text/csv" style="display: none;">
    </div>

    <!-- Hidden configuration inputs with optimal defaults -->
    <input type="hidden" id="scale" value="5">
    <input type="hidden" id="border" value="2">
    <input type="hidden" id="dark" value="#000000">
    <input type="hidden" id="light" value="#ffffff">

    <label class="checkbox-row">
      <input type="checkbox" id="includeVcf" checked>
      Also include raw <code>.vcf</code> contact cards in the ZIP
    </label>

    <button id="convertBtn" class="generate-btn">
      Convert & Download SVG QR Codes (ZIP)
    </button>

    <div id="status" class="status"></div>
  </div>

  <script>
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('fileInput');
    const dropTitle = document.getElementById('dropTitle');
    const dropSub = document.getElementById('dropSub');
    const convertBtn = document.getElementById('convertBtn');
    const statusDiv = document.getElementById('status');

    let selectedFile = null;

    dropzone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });

    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
    });

    function handleFile(file) {
      if (!file.name.toLowerCase().endsWith('.csv')) {
        showStatus('Please select a valid .csv file', 'error');
        return;
      }
      selectedFile = file;
      dropTitle.innerHTML = `Loaded: <strong>${file.name}</strong>`;
      dropSub.textContent = `${(file.size / 1024).toFixed(1)} KB — Ready to convert`;
      showStatus(`File "${file.name}" ready. Click below to generate your QR codes.`, 'info');
    }

    function showStatus(msg, type) {
      statusDiv.textContent = msg;
      statusDiv.className = 'status ' + type;
    }

    convertBtn.addEventListener('click', async () => {
      if (!selectedFile) {
        showStatus('Please select a CSV file first.', 'error');
        return;
      }

      showStatus('Generating vector SVG QR codes...', 'info');
      convertBtn.disabled = true;

      const scale = document.getElementById('scale').value;
      const border = document.getElementById('border').value;
      const dark = document.getElementById('dark').value;
      const light = document.getElementById('light').value;
      const vcf = document.getElementById('includeVcf').checked;

      const url = `/api/convert?scale=${scale}&border=${border}&dark=${encodeURIComponent(dark)}&light=${encodeURIComponent(light)}&vcf=${vcf}`;

      try {
        const textData = await selectedFile.text();
        const response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'text/csv' },
          body: textData
        });

        if (!response.ok) {
          const err = await response.text();
          throw new Error(err || 'Failed to generate QR codes');
        }

        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = selectedFile.name.replace(/\\.csv$/i, '') + '_vcf_qrcodes.zip';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(downloadUrl);

        showStatus('Successfully generated and downloaded QR codes archive!', 'success');
      } catch (err) {
        showStatus('Error: ' + err.message, 'error');
      } finally {
        convertBtn.disabled = false;
      }
    });
  </script>
</body>
</html>
"""


class APIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Quiet standard HTTP access logs in server console
        pass

    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/" or path == "/index.html":
            body = INDEX_HTML.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(body)
            return

        elif path == "/health":
            data = json.dumps({"status": "ok", "service": "kewargen-vcf-qr-api"}).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(data)
            return

        elif path == "/api/template":
            # Stream the template CSV
            script_dir = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(script_dir, "contacts_template.csv")
            if os.path.exists(template_path):
                with open(template_path, "rb") as tf:
                    data = tf.read()
            else:
                data = (
                    "first_name,last_name,title,company,work_phone,mobile_phone,email,company_website,linkedin,notes\n"
                    "John,Doe,Engineer,Acme Corp,+1234567890,+1987654321,john@acme.com,https://acme.com,https://linkedin.com/in/johndoe,Sample contact\n"
                ).encode("utf-8")

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="contacts_template.csv"')
            self.send_header("Content-Length", str(len(data)))
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(data)
            return

        elif path in ("/api/qr.svg", "/api/generate-single"):
            # Generates a single SVG QR from query parameters
            contact = {k: v[0] for k, v in query.items() if v}
            scale = int(query.get("scale", [5])[0])
            border = int(query.get("border", [2])[0])
            dark = query.get("dark", ["#000000"])[0]
            light = query.get("light", ["#FFFFFF"])[0]

            vcard = build_vcard_3(contact)
            try:
                svg_data = generate_svg_string(vcard, scale=scale, border=border, dark=dark, light=light)
                body = svg_data.encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                err = f"Error generating QR code: {str(e)}".encode("utf-8")
                self.send_response(HTTPStatus.BAD_REQUEST)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", str(len(err)))
                self.end_headers()
                self.wfile.write(err)
            return

        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)

        if path == "/api/convert":
            scale = int(query.get("scale", [5])[0])
            border = int(query.get("border", [2])[0])
            dark = query.get("dark", ["#000000"])[0]
            light = query.get("light", ["#FFFFFF"])[0]
            include_vcf = query.get("vcf", ["false"])[0].lower() in ("true", "1", "yes")

            try:
                # Handle text/csv or standard multipart form uploads
                content_type = self.headers.get("Content-Type", "")
                if "multipart/form-data" in content_type:
                    # Quick boundary extract
                    boundary = content_type.split("boundary=")[-1].strip()
                    parts = raw_body.split(f"--{boundary}".encode("utf-8"))
                    csv_text = ""
                    for p in parts:
                        if b"filename=" in p:
                            header_end = p.find(b"\r\n\r\n")
                            if header_end != -1:
                                file_bytes = p[header_end + 4 :].rstrip(b"\r\n-")
                                csv_text = file_bytes.decode("utf-8", errors="replace")
                                break
                    if not csv_text:
                        csv_text = raw_body.decode("utf-8", errors="replace")
                else:
                    csv_text = raw_body.decode("utf-8", errors="replace")

                zip_bytes = process_csv_to_zip(
                    csv_text,
                    scale=scale,
                    border=border,
                    dark=dark,
                    light=light,
                    include_vcf=include_vcf,
                )

                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Disposition", 'attachment; filename="vcf_qrcodes.zip"')
                self.send_header("Content-Length", str(len(zip_bytes)))
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(zip_bytes)
            except Exception as e:
                err = f"Failed to process CSV: {str(e)}".encode("utf-8")
                self.send_response(HTTPStatus.BAD_REQUEST)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", str(len(err)))
                self.end_headers()
                self.wfile.write(err)
            return

        elif path in ("/api/generate-single", "/api/qr.svg"):
            try:
                payload = json.loads(raw_body.decode("utf-8"))
                contact = payload.get("contact", payload)
                scale = int(payload.get("scale", 5))
                border = int(payload.get("border", 2))
                dark = payload.get("dark", "#000000")
                light = payload.get("light", "#FFFFFF")

                vcard = build_vcard_3(contact)
                svg_data = generate_svg_string(vcard, scale=scale, border=border, dark=dark, light=light)
                body = svg_data.encode("utf-8")

                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "image/svg+xml; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                err = f"Failed to generate QR: {str(e)}".encode("utf-8")
                self.send_response(HTTPStatus.BAD_REQUEST)
                self.send_header("Content-Type", "text/plain")
                self.send_header("Content-Length", str(len(err)))
                self.end_headers()
                self.wfile.write(err)
            return

        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()


def start_server(port: int = 8000, host: str = "0.0.0.0"):
    """Starts the lightweight HTTP API server."""
    ensure_segno()
    server_address = (host, port)
    httpd = HTTPServer(server_address, APIHandler)
    print(f"\n=======================================================")
    print(f" Kewargen VCF QR Server & API Running")
    print(f" URL: http://localhost:{port}")
    print(f" API Endpoints:")
    print(f"   - Web UI:         GET  http://localhost:{port}/")
    print(f"   - CSV Template:   GET  http://localhost:{port}/api/template")
    print(f"   - Convert CSV:    POST http://localhost:{port}/api/convert")
    print(f"   - Single QR SVG:  GET  http://localhost:{port}/api/qr.svg")
    print(f"=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()


# -----------------------------------------------------------------------------
# Main CLI Entrypoint
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Convert contacts CSV to standard vCard 3.0 SVG QR codes."
    )
    parser.add_argument(
        "--input", "-i",
        help="Path to contacts CSV file",
        default="scripts/contacts_template.csv",
    )
    parser.add_argument(
        "--output", "-o",
        help="Directory to write generated SVG QR code files",
        default="output_qr",
    )
    parser.add_argument(
        "--scale", "-s",
        type=int,
        default=5,
        help="QR module scale in pixels (default: 5)",
    )
    parser.add_argument(
        "--border", "-b",
        type=int,
        default=2,
        help="Quiet zone border in modules (default: 2)",
    )
    parser.add_argument(
        "--dark",
        default="#000000",
        help="Foreground color (hex or CSS name, default: #000000)",
    )
    parser.add_argument(
        "--light",
        default="#FFFFFF",
        help="Background color (hex or CSS name, default: #FFFFFF). Use None for transparent.",
    )
    parser.add_argument(
        "--save-vcf",
        action="store_true",
        help="Also write matching .vcf files alongside the .svg files",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Launch the lightweight web UI and HTTP API server instead of batch CLI",
    )
    default_port = int(os.environ.get("PORT", 8000))
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=default_port,
        help=f"Port to listen on when running with --serve (default: {default_port})",
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host address to bind to when running with --serve (default: 0.0.0.0)",
    )

    args = parser.parse_args()

    if args.serve:
        start_server(port=args.port, host=args.host)
        return

    # Batch file mode
    csv_path = args.input
    if not os.path.exists(csv_path):
        sys.stderr.write(f"Error: Input file '{csv_path}' does not exist.\n")
        sys.exit(1)

    print(f"Processing contacts from: {csv_path}")
    print(f"Output directory:         {args.output}")

    light_color = None if args.light.lower() in ("none", "transparent", "") else args.light

    results = process_contacts_csv(
        csv_file_path=csv_path,
        output_dir=args.output,
        scale=args.scale,
        border=args.border,
        dark=args.dark,
        light=light_color,
        save_vcf=args.save_vcf,
    )

    print(f"\nSuccessfully generated {len(results)} SVG QR code(s) in '{args.output}':")
    for filename, _ in results:
        print(f"  - {filename}")


if __name__ == "__main__":
    main()
