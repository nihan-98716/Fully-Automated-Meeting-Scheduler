# Fully Automated Meeting Scheduler

A fully automated, local-first meeting scheduler that runs silently in the background.
It reads your Gmail inbox, detects meeting-related emails, extracts dates/times/links/ICS invites, and automatically adds them to your Google Calendar — with zero manual input.

This system is privacy-first and runs **entirely on your machine** using **Windows Task Scheduler**.

---

# 📌 **Features**

* 🧠 Smart meeting detection
* 📅 Natural-language date parsing (`tomorrow at 6pm`, `next Tuesday 4pm`, etc.)
* 📎 `.ics` invite parsing
* 🔗 Google Meet / Zoom link extraction
* 🔄 Auto-sync every 5 minutes (Task Scheduler + APScheduler)
* 🔐 100% local processing (no cloud backend)
* 🔌 Offline OAuth tokens (no repeated login)
* 📁 SQLite database prevents duplicate events
* 🖥️ Runs automatically every time your computer starts

---

# 📁 **Repository Structure**

```
auto-meeting-scheduler/
│
├── google_auth_setup.py        # Run once to create token.json
├── background_runner.py        # Auto scheduler (5 min interval)
├── worker.py                   # Main Gmail → Calendar logic
├── utils.py                    # NLP + parsing helpers
├── db.py                       # SQLite processed-message tracking
│
├── run_scheduler.bat           # Used by Windows Task Scheduler
├── requirements.txt            # Python dependencies
├── credentials_desktop.json.example
├── README.md
└── .gitignore
```

---

# 🛠 **Installation Guide (Step-by-Step)**

Follow these steps in order:

---

## **1️⃣ Clone the repository**

```bash
git clone https://github.com/<your-username>/auto-meeting-scheduler.git
cd auto-meeting-scheduler
```

---

## **2️⃣ Create a virtual environment**

```bash
python -m venv venv
```

Activate it:

### Windows:

```bash
venv\Scripts\activate
```

---

## **3️⃣ Install dependencies**

```bash
pip install -r requirements.txt
```

---

# 🔐 **4️⃣ Google OAuth Setup (IMPORTANT)**

This system requires Gmail + Calendar permission.
You must generate your own OAuth credentials.

---

### **Step A — Create a Google Cloud Project**

1. Go to: [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Create a New Project
3. Go to **APIs & Services → Enabled APIs & Services**
4. Click **Enable APIs and Services**
5. Enable:

   * Gmail API
   * Google Calendar API

---

### **Step B — Create OAuth Client**

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth client ID**
3. Application type: **Desktop App**
4. Download the JSON file
5. Save it as:

```
credentials_desktop.json
```

🚫 **Never upload this file to GitHub.**

(Your repo already includes a safe: `credentials_desktop.json.example`.)

---

### **Step C — Generate secure token (Run Once)**

Run:

```bash
python google_auth_setup.py
```

This will:

* Open a browser
* Ask you to log in
* Ask for Gmail + Calendar permission
* Create `token.json`

This token enables offline access (no repeated logins).

---

# 🚀 **5️⃣ Test the system manually**

Run:

```bash
python worker.py
```

If you receive a meeting email now, it should appear in your Google Calendar.

---

# 🔄 **6️⃣ Set Up Windows Task Scheduler (Auto-Run Every 5 min)**

This makes your system **fully automated**.

---

## **Step A — Create a batch file**

Create `run_scheduler.bat` in the project folder:

```bat
@echo off
cd /d "%~dp0"
call venv\Scripts\activate
python background_runner.py
```

---

## **Step B — Add a scheduled task**

1. Open **Task Scheduler**

2. Click **Create Task**

3. General tab:

   * Name: `Auto Meeting Scheduler`
   * Check: **Run whether user is logged in or not**
   * Check: **Run with highest privileges**

4. Triggers → **New**

   * Select: **At startup**
   * Enabled: ✔

5. Actions → **New**

   * Program/script:

     ```
     run_scheduler.bat
     ```
   * Start in:
     Your project folder path

6. Conditions:

   * Disable “Start only if on AC power”

7. Settings:

   * Enable “Restart if task fails”
   * Allow task to be run on demand

Click **OK**, enter your Windows password.

✨ You now have a fully automated scheduler.

---

# 🧠 **How It Works Internally**

### **1. Gmail API**

* Searches inbox for meeting-related keywords
* Fetches full email content
* Reads body + headers + attachments

### **2. NLP-Based Detection**

* Checks for phrases like *meeting, schedule, call, invite, zoom, google meet*
* Extracts natural language timestamps using regex + dateparser
* Parses `.ics` invite files if present

### **3. Calendar API**

* Creates a fully formatted Google Calendar event
* Sets timezone automatically
* Titles event based on subject
* Prevents duplicates with SQLite

### **4. Automation Layer**

* APScheduler triggers a sync every 5 minutes
* Task Scheduler launches everything on startup
* Local token.json maintains OAuth session

---

# 🧪 **Testing Tips**

Send yourself an email like:

```
Subject: Team Sync Tomorrow

Body:
Let's have a quick meeting tomorrow at 6 PM.
Google Meet link: https://meet.google.com/xyz-123
```

Then run:

```bash
python worker.py
```

You should see:

```
📅 Added: Team Sync Tomorrow
```

And the event appears in Google Calendar.

---

# 🔒 **Security Notes**

This system is **local-first**:

* No external server
* OAuth tokens stored locally
* Emails and events never leave your computer

---

# ❤️ **Contributing**

Pull requests & issues are welcome if you'd like to improve detection logic or add more integrations.

---
