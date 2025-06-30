import os
import shutil
import pandas as pd
import streamlit as st
from pathlib import Path
import datetime
import subprocess
import paramiko
import pyttsx3
import speech_recognition as sr
import pyautogui
import pywhatkit
import smtplib
from email.message import EmailMessage
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Import credentials
from my_credentials import EMAIL, PASSWORD, GEMINI_API_KEY, SSH_IP, SSH_USER, SSH_PASS

# --- Gemini AI Setup ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# --- Text-to-Speech ---
engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

# --- Voice Recognition (Local use) ---
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙 Listening... (Check terminal for output)")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio)
            print(f"🗣 You said: {command}")
            return command
        except Exception as e:
            return f"Error: {e}"

# --- Email Function ---
def send_email(to, subject, body):
    msg = EmailMessage()
    msg["From"] = EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL, PASSWORD)
        smtp.send_message(msg)

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

# --- Gemini Natural Language to Linux Command ---
def nl_to_linux_cmd(prompt):
    response = model.generate_content(
        f"You are a Linux engineer. Convert the user prompt into a single Linux command. "
        f"Do not use quotes or bash script, only single command like: date, ls, etc.\n"
        f"Prompt: {prompt}"
    )
    return response.text.strip()

# --- SSH Command Execution ---
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

# --- Voice Assistant Command Processor ---
def process_command(command):
    command = command.lower()
    if "open notepad" in command:
        os.system("notepad" if os.name == "nt" else "gedit")
        return "Opening Notepad."
    elif "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."
    elif "open google" in command:
        webbrowser.open("https://www.google.com")
        return "Opening Google."
    elif "open linkedin" in command:
        webbrowser.open("https://www.linkedin.com")
        return "Opening LinkedIn."
    elif "take a screenshot" in command:
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")
        return "Screenshot taken and saved as screenshot.png."
    elif "tell me a joke" in command:
        response = model.generate_content("Tell me a joke.")
        joke = response.text.strip()
        speak(joke)
        return joke
    elif "give me a quote" in command:
        response = model.generate_content("Give me a motivational quote.")
        quote = response.text.strip()
        speak(quote)
        return quote
    elif "interesting fact" in command:
        response = model.generate_content("Tell me an interesting fact.")
        fact = response.text.strip()
        speak(fact)
        return fact
    elif "send whatsapp message" in command:
        number = st.text_input("Number with country code (e.g., +919812345678):")
        message = st.text_input("Message:")
        if st.button("Send WhatsApp Message"):
            now = datetime.datetime.now()
            hour = now.hour
            minute = now.minute + 2
            try:
                pywhatkit.sendwhatmsg(number, message, hour, minute, wait_time=15)
                return f"✅ Scheduled WhatsApp message to {number}: {message}"
            except Exception as e:
                return f"❌ Failed to send WhatsApp message: {str(e)}"
        return ""
    elif "send email" in command:
        to = st.text_input("Recipient Email:")
        subject = st.text_input("Subject:")
        body = st.text_area("Body:")
        if st.button("Send Email"):
            try:
                send_email(to, subject, body)
                return f"✅ Email sent to {to} with subject '{subject}'."
            except Exception as e:
                return f"❌ Error sending email: {str(e)}"
        return ""
    elif "search" in command:
        search_term = command.replace("search", "").strip()
        search_url = f"https://www.google.com/search?q={search_term}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            result = soup.find("div", class_="BNeawe").text
            webbrowser.open(search_url)
            speak(result)
            return f"🔍 {search_term} summary: {result}"
        except Exception as e:
            webbrowser.open(search_url)
            return f"✅ Opened Google for '{search_term}' but failed to fetch summary: {str(e)}"
    elif "download data from" in command:
        url = command.replace("download data from", "").strip()
        try:
            response = requests.get(url)
            filename = "downloaded_page.html"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(response.text)
            return f"✅ Data from {url} downloaded and saved as {filename}."
        except Exception as e:
            return f"❌ Failed to download data: {str(e)}"
    elif "time" in command:
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
        return f"The time is {now}."
    elif "date" in command:
        today = datetime.date.today().strftime("%B %d, %Y")
        speak(f"Today's date is {today}")
        return f"Today's date is {today}."
    return "Sorry, I didn't understand that."

# --- Streamlit App ---
st.set_page_config(page_title="Vyūha (व्यूह) – Unified Dashboard", layout="wide")
st.title("Vyūha (व्यूह) – Unified System Dashboard")

menu = [
    "Home",
    "AI Voice Assistant",
    "Remote Linux (Menu)",
    "Remote Linux (Natural Language)",
    "File System"
]
choice = st.sidebar.selectbox("Navigation", menu)

# --- Home ---
if choice == "Home":
    st.header("Welcome to Vyūha!")
    st.write("""
    - Use the sidebar to access different modules:
      - **AI Voice Assistant**: Use Gemini-powered voice/text assistant.
      - **Remote Linux (Menu)**: Run common Linux commands on remote server (SSH).
      - **Remote Linux (Natural Language)**: Describe your task, Gemini will convert to Linux command and run it!
      - **File System**: Manage local files/folders.
    """)
    st.info("All credentials are securely stored in `my_credentials.py`.")

# --- AI Voice Assistant ---
elif choice == "AI Voice Assistant":
    st.header("🤖 AI Voice Assistant (Gemini)")
    st.write("Type your command or use microphone (local only):")
    command = st.text_input("Your Command:")
    if st.button("Run Command"):
        response = process_command(command)
        st.success(response)
    if st.button("🎙 Use Microphone (Local Only)"):
        voice_command = recognize_speech()
        st.info(f"Voice Input: {voice_command}")
        if voice_command:
            response = process_command(voice_command)
            st.success(response)

# --- Remote Linux (Menu) ---
elif choice == "Remote Linux (Menu)":
    st.header("🖥️ Remote Linux Command Executor (Menu)")
    menu_cmds = {
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
        "Installed packages": "dpkg -l | head -20 || rpm -qa | head -20",
        "Battery status": "acpi -b || echo 'No battery info'",
        "Disk usage": "df -h",
        "Startup programs": "ls /etc/init.d/",
        "BIOS info": "dmidecode -t bios",
        "CPU info": "lscpu",
        "Memory info": "free -h",
        "Motherboard info": "dmidecode -t baseboard",
        "Network adapters": "lshw -class network",
        "Uptime": "uptime",
        "Routing table": "ip route"
    }
    cmd = st.selectbox("Select Linux Command", list(menu_cmds.keys()))
    if st.button("Run on Remote"):
        output = run_ssh_command(menu_cmds[cmd])
        st.code(output)

# --- Remote Linux (Natural Language) ---
elif choice == "Remote Linux (Natural Language)":
    st.header("🧠 Remote Linux (Natural Language to Command)")
    prompt = st.text_input("Describe your task (e.g., 'list all files', 'show memory info'):")
    if st.button("Generate & Run"):
        linux_cmd = nl_to_linux_cmd(prompt)
        st.info(f"Generated Command: `{linux_cmd}`")
        output = run_ssh_command(linux_cmd)
        st.code(output)

# --- File System ---
elif choice == "File System":
    st.header("📁 File System Management")
    # Directory Input
    default_dir = os.getcwd()
    dir_input = st.text_input("Enter directory path:", value=default_dir)
    current_dir = dir_input if os.path.exists(dir_input) else default_dir

    # List Files
    st.subheader("List of Files and Folders")
    df = list_files_df(current_dir)
    search = st.text_input("Search files/folders")
    if search:
        df = df[df['Name'].str.contains(search, case=False)]
    st.dataframe(df, use_container_width=True)
    selected_file = st.selectbox("Select a file/folder to preview", [""] + df['Name'].tolist())
    if selected_file:
        file_path = os.path.join(current_dir, selected_file)
        if os.path.isfile(file_path):
            preview_file(file_path)
        else:
            st.info("Folder selected. Only files can be previewed.")

    # Rename File
    st.subheader("Rename File")
    old_name_val = st.text_input("Old file name:")
    new_name_val = st.text_input("New file name:")
    if st.button("Rename"):
        if old_name_val and new_name_val:
            result = rename_file(current_dir, old_name_val, new_name_val)
            st.success(result)
        else:
            st.error("Please enter both old and new names.")

    # Delete File/Directory
    st.subheader("Delete File or Directory")
    name = st.text_input("File or directory name to delete:")
    if st.button("Delete"):
        if name:
            result = delete_path(current_dir, name)
            st.success(result)
        else:
            st.error("Please enter a name.")

    # Create Directory
    st.subheader("Create Directory")
    folder_name = st.text_input("New directory name to create:")
    if st.button("Create"):
        if folder_name:
            result = create_dir(current_dir, folder_name)
            st.success(result)
        else:
            st.error("Please enter a directory name.")

    # Upload File
    st.subheader("Upload File")
    uploaded_file = st.file_uploader("Choose a file to upload")
    if uploaded_file is not None:
        file_path = os.path.join(current_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    # Download File
    st.subheader("Download File")
    files = [f for f in os.listdir(current_dir) if os.path.isfile(os.path.join(current_dir, f))]
    if files:
        selected_file = st.selectbox("Select file to download", files)
        if st.button("Download"):
            file_path = os.path.join(current_dir, selected_file)
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            st.download_button("Download File", data=file_bytes, file_name=selected_file)
    else:
        st.info("No files available to download.")
