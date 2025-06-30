import os
import shutil
import pandas as pd
import streamlit as st
import pywhatkit as kit
import smtplib
from email.message import EmailMessage
from twilio.rest import Client
import requests
from bs4 import BeautifulSoup
import tweepy
from instagrapi import Client as InstaClient
import paramiko
import google.generativeai as genai
import speech_recognition as sr
import datetime

from my_secrets import (
    EMAIL, EMAIL_PASSWORD, WHATSAPP_NUMBER, WHATSAPP_TEST_NUMBER,
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE, TWILIO_WHATSAPP,
    INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD,
    TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET,
    GEMINI_API_KEY, SSH_IP, SSH_USER, SSH_PASS
)

# --- File System Helpers ---
def get_human_readable_size(size):
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if size < 1024.0 or unit == 'GB':
            break
        size /= 1024.0
    return f"{size:.2f} {unit}"

def list_files_df(directory):
    files = os.listdir(directory)
    data = []
    for name in files:
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            size_str = get_human_readable_size(size)
            data.append([name, "📄 File", size_str])
        else:
            data.append([name, "📁 Folder", "-"])
    df = pd.DataFrame(data, columns=["Name", "Type", "Size"])
    return df

def rename_file(directory, old_name, new_name):
    old_path = os.path.join(directory, old_name)
    new_path = os.path.join(directory, new_name)
    os.rename(old_path, new_path)
    return "Renamed Successfully"

def delete_path(directory, name):
    path = os.path.join(directory, name)
    if os.path.isfile(path):
        os.remove(path)
        return "File deleted successfully"
    elif os.path.isdir(path):
        shutil.rmtree(path)
        return "Directory deleted successfully"
    else:
        return "Enter correct path"

def create_dir(directory, folder_name):
    path = os.path.join(directory, folder_name)
    os.makedirs(path, exist_ok=True)
    return "Directory Created successfully"

def preview_file(file_path):
    try:
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            st.image(file_path)
        elif file_path.lower().endswith(('.txt', '.csv', '.md', '.py', '.json', '.xml')):
            with open(file_path, 'r') as f:
                content = f.read()
            st.code(content, language="text")
    except Exception as e:
        st.error(f"Cannot preview file: {e}")

# --- Utility Functions ---
def send_whatsapp_msg(number, message, hour, minute):
    kit.sendwhatmsg(number, message, hour, minute, wait_time=10)

def send_email(subject, body, to_email, from_email, password):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(from_email, password)
        server.send_message(msg)

def send_whatsapp_twilio(account_sid, auth_token, from_whatsapp, to_whatsapp, message):
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=message,
        from_='whatsapp:' + from_whatsapp,
        to='whatsapp:' + to_whatsapp
    )

def send_sms_twilio(account_sid, auth_token, from_number, to_number, message):
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=message,
        from_=from_number,
        to=to_number
    )

def make_call(account_sid, auth_token, from_number, to_number, twiml_url):
    client = Client(account_sid, auth_token)
    call = client.calls.create(
        to=to_number,
        from_=from_number,
        url=twiml_url
    )

def search_google(query):
    url = f"https://www.google.com/search?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.title.text

def post_instagram(username, password, image_path, caption):
    cl = InstaClient()
    cl.login(username, password)
    cl.photo_upload(image_path, caption)

def post_tweet(api_key, api_secret, access_token, access_secret, text):
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
    api = tweepy.API(auth)
    api.update_status(status=text)

def download_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.prettify()

def spoofed_email(subject, body, from_email, to_email, smtp_server, smtp_port, password):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)

# --- Gemini Linux Command ---
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

def gemini_linux_command(prompt):
    response = gemini_model.generate_content(
        f"You are a Linux engineer. Convert the user prompt into a single Linux command. "
        f"Do not use quotes or bash script, only single command like: date, ls, etc.\n"
        f"Prompt: {prompt}"
    )
    return response.text.strip()

def run_ssh_command(command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(SSH_IP, 22, SSH_USER, SSH_PASS)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()
        return output if output else error
    except Exception as e:
        return f"SSH Error: {e}"

# --- Linux Menu SSH (50 Commands) ---
LINUX_MENU_50 = {
    "Show date": "date",
    "Show time": "date +%T",
    "List directory": "ls -l",
    "Current user": "whoami",
    "System info": "uname -a",
    "Running tasks": "top -b -n 1 | head -15",
    "IP config": "ip a",
    "Active connections": "ss -tuln",
    "ARP table": "ip neigh",
    "All users": "cut -d: -f1 /etc/passwd",
    "Logged in users": "who",
    "Environment variables": "printenv",
    "List services": "systemctl list-units --type=service --state=running",
    "Running processes": "ps aux --sort=-%mem | head -10",
    "Installed packages (dpkg)": "dpkg -l | head -20",
    "Installed packages (rpm)": "rpm -qa | head -20",
    "Battery status": "acpi -b || echo 'No battery info'",
    "Disk usage": "df -h",
    "Startup programs": "ls /etc/init.d/",
    "BIOS info": "dmidecode -t bios",
    "CPU info": "lscpu",
    "Memory info": "free -h",
    "Motherboard info": "dmidecode -t baseboard",
    "Network adapters": "lshw -class network",
    "Uptime": "uptime",
    "Routing table": "ip route",
    "Kernel version": "uname -r",
    "Hostname": "hostname",
    "Check internet": "ping -c 4 8.8.8.8",
    "Show open ports": "netstat -tulpn",
    "Show firewall rules": "iptables -L",
    "Show SSH config": "cat /etc/ssh/sshd_config",
    "Show crontab": "crontab -l",
    "List users with UID 0": "awk -F: '$3 == 0 {print $1}' /etc/passwd",
    "Show last logins": "last -a | head -10",
    "Show failed logins": "lastb -a | head -10",
    "Show system reboot history": "last reboot | head -10",
    "Show dmesg errors": "dmesg | grep -i error | tail -20",
    "List open files": "lsof | head -20",
    "Show processes by user": "ps -u $USER",
    "Show disk partitions": "lsblk",
    "Show PCI devices": "lspci",
    "Show USB devices": "lsusb",
    "Show hardware info": "lshw | head -20",
    "Show systemd failed units": "systemctl --failed",
    "Show SELinux status": "sestatus",
    "Show journal logs": "journalctl -n 20",
    "Show top memory processes": "ps aux --sort=-%mem | head -10",
    "Show top CPU processes": "ps aux --sort=-%cpu | head -10",
    "Show swap usage": "swapon --show",
    "Show temp files": "ls /tmp",
    # Add more as needed (already 50+ with some options)
}

# --- Voice Task Menu ---
def voice_task(command):
    command = command.lower()
    if "open notepad" in command:
        os.system("notepad" if os.name == "nt" else "gedit")
        return "Opening Notepad."
    elif "open vs code" in command or "open vscode" in command:
        os.system("code")
        return "Opening VS Code."
    elif "shutdown" in command:
        os.system("shutdown now" if os.name != "nt" else "shutdown /s /t 1")
        return "System shutting down."
    else:
        return "Sorry, this basic voice task is not recognized."

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙 Listening... (Check terminal for output)")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio)
            return command
        except Exception as e:
            return f"Error: {e}"

# --- Streamlit UI ---
st.set_page_config(page_title="Vyuha: Multitasking Menu-Based System", layout="wide")
st.title("🛡️ Vyuha: Multitasking Menu-Based System")

menu = [
    "Home",
    "All-in-One Utility",
    "File Management",
    "Linux Gemini (Natural Language)",
    "Linux Menu SSH (50 Commands)",
    "Voice Task Menu"
]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Home":
    st.header("Welcome to Vyuha!")
    st.write("""
    - **All-in-One Utility**: WhatsApp, Email, SMS, Call, Google Search, Twitter, Instagram, Web Scraping, etc.
    - **File Management**: Upload, download, rename, delete, preview files.
    - **Linux Gemini (Natural Language)**: Describe your task, Gemini generates Linux command, runs on remote.
    - **Linux Menu SSH (50 Commands)**: Menu-based Linux commands on remote system.
    - **Voice Task Menu**: Voice-based local tasks (open notepad, VS Code, etc.).
    """)

elif choice == "All-in-One Utility":
    st.header("All-in-One Utility")
    tabs = st.tabs([
        "WhatsApp (pywhatkit)", "Email (Gmail)", "WhatsApp (Twilio)", "SMS (Twilio)",
        "Call (Twilio)", "Google Search", "Instagram Post", "Twitter (X) Post",
        "Web Scraping", "Spoofed Email"
    ])
    # WhatsApp (pywhatkit)
    with tabs[0]:
        number = st.text_input("Number with country code:", value=WHATSAPP_TEST_NUMBER)
        message = st.text_area("Message:")
        col1, col2 = st.columns(2)
        hour = col1.number_input("Hour (24h):", min_value=0, max_value=23, value=datetime.datetime.now().hour)
        minute = col2.number_input("Minute:", min_value=0, max_value=59, value=(datetime.datetime.now().minute+2)%60)
        if st.button("Send WhatsApp Message"):
            try:
                send_whatsapp_msg(number, message, hour, minute)
                st.success("WhatsApp message scheduled!")
            except Exception as e:
                st.error(f"Error: {e}")

    # Email (Gmail)
    with tabs[1]:
        to_email = st.text_input("To Email:", key="email_to")
        subject = st.text_input("Subject:", key="email_sub")
        body = st.text_area("Body:", key="email_body")
        if st.button("Send Email"):
            try:
                send_email(subject, body, to_email, EMAIL, EMAIL_PASSWORD)
                st.success("Email sent successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

    # WhatsApp (Twilio)
    with tabs[2]:
        to_whatsapp = st.text_input("To WhatsApp:", value=WHATSAPP_TEST_NUMBER, key="twilio_whatsapp")
        message = st.text_area("Message:", key="twilio_whatsapp_msg")
        if st.button("Send WhatsApp via Twilio"):
            try:
                send_whatsapp_twilio(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP, to_whatsapp, message)
                st.success("WhatsApp message sent via Twilio!")
            except Exception as e:
                st.error(f"Error: {e}")

    # SMS (Twilio)
    with tabs[3]:
        to_number = st.text_input("To Number:", value=WHATSAPP_TEST_NUMBER, key="twilio_sms")
        message = st.text_area("Message:", key="twilio_sms_msg")
        if st.button("Send SMS"):
            try:
                send_sms_twilio(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE, to_number, message)
                st.success("SMS sent via Twilio!")
            except Exception as e:
                st.error(f"Error: {e}")

    # Call (Twilio)
    with tabs[4]:
        to_number = st.text_input("To Number:", value=WHATSAPP_TEST_NUMBER, key="twilio_call")
        twiml_url = st.text_input("Twiml URL:", value
        ="http://demo.twilio.com/docs/voice.xml")
        if st.button("Make Call"):
            try:
                make_call(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE, to_number, twiml_url)
                st.success("Call initiated!")
            except Exception as e:
                st.error(f"Error: {e}")

    # Google Search
    with tabs[5]:
        query = st.text_input("Search Query:", key="google_search")
        if st.button("Search"):
            try:
                result = search_google(query)
                st.success(f"Google Search Title: {result}")
            except Exception as e:
                st.error(f"Error: {e}")

    # Instagram Post
    with tabs[6]:
        image_path = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'])
        caption = st.text_input("Caption:", key="insta_caption")
        if st.button("Post to Instagram"):
            try:
                if image_path:
                    with open("temp_insta.jpg", "wb") as f:
                        f.write(image_path.read())
                    post_instagram(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, "temp_insta.jpg", caption)
                    os.remove("temp_insta.jpg")
                    st.success("Image posted to Instagram!")
                else:
                    st.error("Please upload an image.")
            except Exception as e:
                st.error(f"Error: {e}")

    # Twitter (X) Post
    with tabs[7]:
        tweet_text = st.text_area("Tweet:", key="tweet")
        if st.button("Post Tweet"):
            try:
                post_tweet(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, tweet_text)
                st.success("Tweet posted!")
            except Exception as e:
                st.error(f"Error: {e}")

    # Web Scraping
    with tabs[8]:
        url = st.text_input("URL to scrape:", key="scrape_url")
        if st.button("Download Data"):
            try:
                data = download_data(url)
                st.code(data)
            except Exception as e:
                st.error(f"Error: {e}")

    # Spoofed Email
    with tabs[9]:
        st.warning("Use this feature responsibly and only for legitimate purposes.")
        from_email = st.text_input("From Email:", value="", key="spoof_from")
        to_email = st.text_input("To Email:", value="", key="spoof_to")
        subject = st.text_input("Subject:", key="spoof_sub")
        body = st.text_area("Body:", key="spoof_body")
        smtp_server = st.text_input("SMTP Server:", value="", key="spoof_server")
        smtp_port = st.number_input("SMTP Port:", value=587, key="spoof_port")
        password = st.text_input("Password:", type="password", key="spoof_pass")
        if st.button("Send Spoofed Email"):
            try:
                spoofed_email(subject, body, from_email, to_email, smtp_server, smtp_port, password)
                st.success("Email sent!")
            except Exception as e:
                st.error(f"Error: {e}")

elif choice == "File Management":
    st.header("📁 File System Management")
    default_dir = os.getcwd()
    dir_input = st.text_input("Enter directory path:", value=default_dir)
    current_dir = dir_input if os.path.exists(dir_input) else default_dir

    st.subheader("List of Files and Folders")
    df = list_files_df(current_dir)
    search = st.text_input("Search files/folders", key="file_search")
    if search:
        df = df[df['Name'].str.contains(search, case=False)]
    st.dataframe(df, use_container_width=True)
    selected_file = st.selectbox("Select a file/folder to preview", [""] + df['Name'].tolist(), key="preview_file")
    if selected_file:
        file_path = os.path.join(current_dir, selected_file)
        if os.path.isfile(file_path):
            preview_file(file_path)
        else:
            st.info("Folder selected. Only files can be previewed.")

    st.subheader("Rename File")
    old_name = st.text_input("Old file name:", key="rename_old")
    new_name = st.text_input("New file name:", key="rename_new")
    if st.button("Rename"):
        if old_name and new_name:
            result = rename_file(current_dir, old_name, new_name)
            st.success(result)
        else:
            st.error("Please enter both old and new names.")

    st.subheader("Delete File or Directory")
    name = st.text_input("File or directory name to delete:", key="delete_name")
    if st.button("Delete"):
        if name:
            result = delete_path(current_dir, name)
            st.success(result)
        else:
            st.error("Please enter a name.")

    st.subheader("Create Directory")
    folder_name = st.text_input("New directory name to create:", key="create_dir")
    if st.button("Create"):
        if folder_name:
            result = create_dir(current_dir, folder_name)
            st.success(result)
        else:
            st.error("Please enter a directory name.")

    st.subheader("Upload File")
    uploaded_file = st.file_uploader("Choose a file to upload", key="upload_file")
    if uploaded_file is not None:
        file_path = os.path.join(current_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    st.subheader("Download File")
    files = [f for f in os.listdir(current_dir) if os.path.isfile(os.path.join(current_dir, f))]
    if files:
        selected_file = st.selectbox("Select file to download", files, key="download_file")
        if st.button("Download"):
            file_path = os.path.join(current_dir, selected_file)
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            st.download_button("Download File", data=file_bytes, file_name=selected_file)
    else:
        st.info("No files available to download.")

elif choice == "Linux Gemini (Natural Language)":
    st.header("🧠 Linux Gemini (Natural Language to Command)")
    prompt = st.text_input("Describe your task (e.g., 'list all files', 'show memory info'):")
    if st.button("Generate & Run"):
        linux_cmd = gemini_linux_command(prompt)
        st.info(f"Generated Command: `{linux_cmd}`")
        output = run_ssh_command(linux_cmd)
        st.code(output)

elif choice == "Linux Menu SSH (50 Commands)":
    st.header("🖥️ Remote Linux Command Executor (50 Commands)")
    cmd = st.selectbox("Select Linux Command", list(LINUX_MENU_50.keys()))
    if st.button("Run on Remote"):
        output = run_ssh_command(LINUX_MENU_50[cmd])
        st.code(output)

elif choice == "Voice Task Menu":
    st.header("🎙️ Voice Task Menu (Local Machine)")
    st.write("Try saying: 'open notepad', 'open vs code', 'shutdown', etc.")
    if st.button("🎤 Use Microphone (Local Only)"):
        voice_command = recognize_speech()
        st.info(f"Voice Input: {voice_command}")
        if voice_command:
            response = voice_task(voice_command)
            st.success(response)
    command = st.text_input("Or type your command:")
    if st.button("Run Local Task"):
        response = voice_task(command)
        st.success(response)
