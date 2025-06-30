# 🛡️ Vyuha: AI-Powered Multitasking Utility and Linux Remote Manager

> "Vyuha" is a versatile, intelligent, and menu-driven utility system built with **Streamlit** that integrates communication tools, Linux remote management via SSH, voice command automation, and AI-powered command generation using **Google Gemini**. Ideal for DevOps, automation, and personal productivity tasks.

---

## 🚀 Features

### 🧰 All-in-One Utility Dashboard:
- 📱 Send WhatsApp messages (PyWhatKit + Twilio)
- 📧 Send Emails (Gmail & Spoofed SMTP)
- 📞 Make calls via Twilio
- 💬 Send SMS using Twilio
- 🔍 Google Search scraping
- 📸 Post to Instagram
- 🐦 Tweet on Twitter (X)
- 🌐 Web scraping with BeautifulSoup

### 📂 File System Manager:
- Upload, download, preview, rename, and delete files
- Create directories
- Human-readable file sizes
- Live file preview for `.txt`, `.csv`, `.json`, `.py`, and images

### 💻 Linux Remote Execution:
- ✅ **Natural Language to Command (via Gemini AI)**
- ✅ **Menu-based 50+ Predefined Linux SSH Commands**
- Remote execution via `paramiko` (password-based SSH)

### 🎤 Voice Task Automation (Local):
- Run basic system-level tasks like:
  - `open notepad`
  - `open vs code`
  - `shutdown`

---

## ⚙️ Tech Stack

- **Frontend:** Streamlit
- **AI & NLP:** Google Gemini Pro (via `google.generativeai`)
- **Communication APIs:** Twilio, PyWhatKit, SMTP
- **Social Media:** Instagrapi, Tweepy
- **Linux SSH:** Paramiko
- **Voice Recognition:** SpeechRecognition + Google Speech API
- **Web Scraping:** Requests + BeautifulSoup
- **Data Handling:** Pandas
- **Utilities:** OS, shutil, datetime, etc.

---

## 🔐 Secrets Configuration (`my_secrets.py`)

Create a file named `my_secrets.py` and include the following:

```python
EMAIL = "your_email@gmail.com"
EMAIL_PASSWORD = "your_password"

WHATSAPP_NUMBER = "+91xxxxxxxxxx"
WHATSAPP_TEST_NUMBER = "+91xxxxxxxxxx"

TWILIO_ACCOUNT_SID = "your_sid"
TWILIO_AUTH_TOKEN = "your_token"
TWILIO_PHONE = "+1234567890"
TWILIO_WHATSAPP = "+14xxxxxxx"

INSTAGRAM_USERNAME = "your_username"
INSTAGRAM_PASSWORD = "your_password"

TWITTER_API_KEY = "your_key"
TWITTER_API_SECRET = "your_secret"
TWITTER_ACCESS_TOKEN = "your_token"
TWITTER_ACCESS_TOKEN_SECRET = "your_token_secret"

GEMINI_API_KEY = "your_gemini_api_key"

SSH_IP = "your_remote_ip"
SSH_USER = "username"
SSH_PASS = "password"

```

##✅ Also Add:

## `requirements.txt` Example:
```txt
streamlit
pandas
pywhatkit
smtplib
email
twilio
requests
beautifulsoup4
tweepy
instagrapi
paramiko
google-generativeai
SpeechRecognition
```


## 📫 Contact

If you have any questions, feedback, or ideas to improve Saundarya, feel free to reach out!

- 📧 Email: [rprajapati00017@gmail.com](mailto:rprajapati00017@gmail.com)
- 💼 LinkedIn: [linkedin.com/in/rahul-prajapat-a86839255](https://www.linkedin.com/in/rahul-prajapat-a86839255/)
