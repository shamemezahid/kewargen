# Kewargen VCF QR Code Generator & API

Batch convert contacts from a CSV file into vector **SVG vCard (VCF 3.0) QR codes** saved directly into a folder, or run as a lightweight **hosted API / Web UI**.

Everything is contained in this `scripts/` folder.

---

## 🚀 Quick Start (Local Script)

Works out of the box on **macOS**, **Linux**, or any Unix-compatible system with Python 3.

### 1. Run with the included runner script:
```bash
./scripts/run.sh --input scripts/contacts_template.csv --output output_qr
```

*What this does:*
- Automatically creates a lightweight virtual environment (`scripts/.venv`)
- Installs the single zero-C-dependency pure-Python library (`segno`)
- Parses your CSV, discards any missing contact fields, and writes crisp `.svg` QR codes into `output_qr/`.

### 2. Optional: Save both `.svg` and `.vcf` files:
```bash
./scripts/run.sh --input scripts/contacts_template.csv --output output_qr --save-vcf
```

---

## 🌐 Quick Start (Hosted API / Web UI)

Want an API you can host or access from a browser?

### 1. Start the server locally:
```bash
./scripts/run.sh --serve --port 8000
```
Then open:
👉 **[http://localhost:8000](http://localhost:8000)**

The built-in web page lets you:
- Drag-and-drop any CSV file.
- Customize QR code scale, border, foreground, and background colors.
- Download a **ZIP file** containing all generated SVG QR codes with one click.
- Download the official standard CSV template.

### 2. Call the API from the command line or any backend:

#### Convert a CSV file directly to a ZIP of SVG QR codes:
```bash
curl -X POST http://localhost:8000/api/convert \
  --data-binary @scripts/contacts_template.csv \
  -o qr_codes.zip
```

#### Generate a single SVG QR code on the fly:
```bash
curl "http://localhost:8000/api/qr.svg?first_name=John&last_name=Doe&company=Acme&email=john@acme.com" \
  -o contact.svg
```

#### Download the CSV Template:
```bash
curl -O http://localhost:8000/api/template
```

---

## 📋 Standard CSV Template

A ready-to-use template is located at [contacts_template.csv](file:///Users/shameme/Developer/home/kewargen/scripts/contacts_template.csv).

### Included Fields:
| Field Name | Description | Example |
| :--- | :--- | :--- |
| `filename` | **Custom SVG File Name** (omits `.svg` if provided, auto-generates if blank) | `john_doe_qr` |
| `first_name` | First / Given Name | `Alex` |
| `last_name` | Last / Family Name | `Mercer` |
| `prefix` | Honorific / Title Prefix | `Dr.` |
| `suffix` | Generational suffix | `Jr.` |
| `title` | Job title or role | `Chief Technology Officer` |
| `company` | Organization or company name | `Nova Innovations Inc.` |
| `department` | Team or department | `Engineering` |
| `work_phone` | Office / direct work phone | `+1-555-019-2831` |
| `mobile_phone`| Mobile / cell number | `+1-555-019-2832` |
| `fax` | Fax number | `+1-555-019-2839` |
| `email` | Primary work email | `alex.mercer@novainnovations.com` |
| `personal_email` | Secondary / personal email | `alex@personal.me` |
| `company_website` | Company or personal website | `https://novainnovations.com` |
| `street_address` | Work street address | `100 Innovation Way` |
| `city` | City / Locality | `San Francisco` |
| `state` | State / Province / Region | `CA` |
| `postal_code` | ZIP or postal code | `94107` |
| `country` | Country name | `USA` |
| `linkedin` | LinkedIn profile or URL | `https://www.linkedin.com/in/alex-mercer` |
| `twitter` | X / Twitter handle or URL | `https://x.com/alexmercer` |
| `github` | GitHub profile URL | `https://github.com/alexmercer` |
| `notes` | Bio, notes, or comments | `Keynote speaker and architect.` |

> [!NOTE]
> **Flexible Header Matching**: The parser is forgiving and automatically matches aliases like `First Name`, `firstName`, `fname`, `Company Name`, `Organization`, `Job Title`, `Cell Phone`, `ZIP`, etc.

> [!IMPORTANT]
> **Discarding Missing Information**: The parser automatically omits any field that is empty or omitted. It will **not** output empty `TEL:`, `ADR:`, `URL:`, or `ORG:` lines in the vCard.

---

## 🛠️ CLI Options Reference

```text
usage: vcf_qr_generator.py [-h] [--input INPUT] [--output OUTPUT] [--scale SCALE]
                           [--border BORDER] [--dark DARK] [--light LIGHT]
                           [--save-vcf] [--serve] [--port PORT] [--host HOST]

Convert contacts CSV to standard vCard 3.0 SVG QR codes.

options:
  --input, -i       Path to contacts CSV file (default: scripts/contacts_template.csv)
  --output, -o      Directory to write generated SVG files (default: output_qr)
  --scale, -s       Module size in pixels (default: 5)
  --border, -b      Quiet zone border in modules (default: 2)
  --dark            QR foreground color in hex or CSS name (default: #000000)
  --light           QR background color in hex or CSS name (default: #FFFFFF, or 'none')
  --save-vcf        Also write matching .vcf contact files alongside the .svg files
  --serve           Run HTTP API & Web UI instead of CLI batch mode
  --port, -p        Port for the server (default: 8000)
  --host            Host interface for the server (default: 0.0.0.0)
```

---

## ☁️ Super Simplest Way to Host in the Cloud (Free)

Because this uses Python's built-in `HTTPServer`, it requires zero extra web frameworks (no Nginx or external reverse proxy required for simple setups).

### Option A: Render / Railway / Fly.io (Using the provided Dockerfile)
1. Push your repository to GitHub.
2. In [Render](https://render.com) or [Railway](https://railway.app), click **New Web Service** and select this repo.
3. Choose **Dockerfile** (pointing to `scripts/Dockerfile`).
4. It will build and run on port 8000 with HTTPS enabled automatically!

### Option B: Any Linux VPS (Ubuntu/Debian) in 2 commands:
```bash
git clone <your-repo-url> && cd kewargen
nohup ./scripts/run.sh --serve --port 80 > server.log 2>&1 &
```

