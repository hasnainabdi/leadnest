# LeadNest v2.3

**Professional Freelancer CRM Software**

Built with [Orbit Galax](https://orbitgalax.space-z.ai/)

---

## What is LeadNest?

LeadNest is a lightweight, local CRM built for freelancers and small agencies.  
Manage clients, leads, projects, invoices, time tracking, tasks and reports — all in one place.

- Runs on your computer (data stays with you)
- Multi-currency (40+ currencies)
- 14 languages
- Client portal
- Dark mode
- Invoice PDF export
- Tax & Excel reports

---

## Features

### Core
| Module | Description |
|--------|-------------|
| **Dashboard** | KPIs, profit, goals, charts, overdue follow-ups |
| **Clients** | Full client database, ratings, portal password |
| **Leads** | Sales pipeline with stages & priorities |
| **Projects** | Budget, progress, deadlines, profitability |
| **Payments** | Invoices, payment status, recurring invoices |
| **Expenses** | Business costs for net profit calculation |
| **Time Tracker** | Daily hours linked to projects |
| **Tasks** | To-do list with priority & status |
| **Reminders** | Follow-up reminders |
| **Calendar** | Combined view of follow-ups, deadlines, tasks |
| **Reports** | Excel export + yearly tax summary PDF |
| **Activity Log** | History of user actions |
| **Settings** | Goals, hourly rate, company info, backup |
| **Database Schema** | Full structure viewer |

### Advanced
- **Top header** — Logo, global search, notifications, logged-in user
- **Login / Create Account** — Admin, manager, staff roles
- **Client Portal** — Clients view their projects & download invoices
- **Invoice PDF** — Generate and download professional PDFs
- **Multi-currency** — USD storage, display in PKR, EUR, GBP, AED, INR, JPY, and 40+ more
- **14 languages** — English, Urdu, Hindi, Hebrew, Arabic, German, French, Spanish, Portuguese, Turkish, Chinese, Japanese, Korean, Russian
- **Dark mode** — Comfortable for long sessions
- **Search & filters** — On main lists + global header search
- **File attachments** — On clients/projects (local storage)
- **User roles** — admin / manager / staff

---

## System Requirements

- Windows 10/11 (also works on macOS / Linux)
- Python 3.10 or newer
- ~100 MB free disk space
- Internet only needed once to install Python packages

---

## Installation (Windows)

### 1. Install Python
1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download the latest Python 3
3. Run installer
4. **Important:** enable **Add python.exe to PATH**
5. Click Install Now

### 2. Extract LeadNest
Extract the ZIP to a folder, for example:

```text
C:\Users\YourName\Downloads\LeadNest
```

### 3. Install required packages
Open PowerShell or Command Prompt in that folder:

```powershell
cd C:\Users\YourName\Downloads\LeadNest
python -m pip install streamlit pandas plotly fpdf2 openpyxl
```

If `pip` fails, try:

```powershell
python -m ensurepip --upgrade
python -m pip install --upgrade pip
python -m pip install streamlit pandas plotly fpdf2 openpyxl
```

### 4. Run LeadNest

```powershell
python -m streamlit run app.py
```

Browser will open at:

```text
http://localhost:8501
```

If it does not open automatically, paste that URL in your browser.

---

## First-time setup

1. Open the app
2. Go to **Create Account**
3. Create your admin account (full name, username, email, password)
4. Login
5. (Optional) Open **Settings** and set:
   - Monthly earning goal
   - Default hourly rate
   - Company name / email (for invoices)
6. Use the **sidebar** to switch **language** and **currency**

---

## How to use (recommended workflow)

1. **Leads** — Add new inquiries (stage: New → Contacted → Proposal → Negotiation → Won/Lost)
2. When a lead is **Won** — Add them under **Clients**
3. **Projects** — Create a project linked to the client
4. **Time Tracker** — Log hours while you work
5. **Payments** — Create invoices; generate PDF when needed
6. **Expenses** — Record tools, internet, marketing costs
7. **Dashboard** — Check profit, goals, overdue follow-ups
8. **Client Portal** — Set a portal password on a client so they can log in and view their projects/invoices

---

## Client Portal

1. Open **Clients** → edit a client
2. Set **Portal Password**
3. Share with the client:
   - Their email (as saved in Clients)
   - Portal password
4. Client opens the app → **Client Portal** tab → logs in
5. They can view projects, progress, and download invoice PDFs

---

## Folder structure

```text
LeadNest/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── run.sh                 # Optional helper script
├── crm_data.db            # Created automatically (your data)
└── attachments/           # Uploaded files (created when needed)
```

**Important:** Keep `crm_data.db` safe — this is your database.  
Use **Settings → Download DB Backup** regularly.

---

## requirements.txt

```text
streamlit
pandas
plotly
fpdf2
openpyxl
```

Install all at once:

```powershell
python -m pip install -r requirements.txt
```

---

## Common issues

| Problem | Solution |
|---------|----------|
| `pip` not recognized | Use `python -m pip ...` or reinstall Python with PATH enabled |
| `No module named pip` | Run `python -m ensurepip --upgrade` |
| `app.py` not found | `cd` into the folder that actually contains `app.py` (sometimes nested after ZIP extract) |
| `logged_in` AttributeError | Use the latest `app.py` (session state is initialized at startup) |
| Tax PDF error / bytearray | Use the latest `app.py` (PDF output converted to `bytes`) |
| Login text not visible | Use the latest light-mode CSS fix |
| Port already in use | `python -m streamlit run app.py --server.port 8502` |

---

## Public demo (optional)

You can deploy LeadNest online with **Streamlit Community Cloud**:

1. Put `app.py` + `requirements.txt` on GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from your repository
4. Share the public URL

Note: A public deploy shares one app instance unless you add stronger multi-user isolation later.

---

## Branding & copyright

- **Product name:** LeadNest  
- **Version:** 2.3  
- **Built with:** Orbit Galax  
- **Website:** [https://orbitgalax.space-z.ai/](https://orbitgalax.space-z.ai/)

```text
Copyright by LeadNest v2.3
Built with Orbit Galax (https://orbitgalax.space-z.ai/)
```

---

## Privacy

- Data is stored locally in `crm_data.db` (SQLite)
- No required cloud account for normal desktop use
- You control backups and files on your machine

---

## Support/contact

For custom CRM work, branding, or deployment help, reach out via Orbit Galax:

**https://orbitgalax.space-z.ai/**

---

## Changelog (summary)

### v2.3
- Product renamed to **LeadNest**
- Light mode contrast fixed
- 40+ currencies
- 14 languages (including Hebrew & Hindi)
- Tax PDF download fixed
- Top header: logo, search, notifications, user name

### v2.2
- Proper icons, better UI
- Search & filters, activity log, tasks
- Attachments, recurring invoices
- Calendar, tax report, roles, schema viewer

### v2.1
- Login/accounts
- Client portal
- Invoice PDF
- Dark mode
- Reports export

### v2.0
- Multi-sheet CRM foundation (Dashboard, Clients, Leads, Projects, Payments, Expenses, Time)

---

**LeadNest — manage leads, clients, and work in one nest.**
