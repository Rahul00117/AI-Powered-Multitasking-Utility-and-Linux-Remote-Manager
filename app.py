import streamlit as st
import pywhatkit as kit
import smtplib
from email.message import EmailMessage
from twilio.rest import Client
import requests
from bs4 import BeautifulSoup
import tweepy
import paramiko
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import cv2
import time

# Gemini API setup (direct key as you requested)
genai.configure(api_key="hide")
model = genai.GenerativeModel('gemini-1.5-flash')

engine = pyttsx3.init()

# ======================
# Utility Functions
# ======================

def send_whatsapp_twilio(account_sid, auth_token, from_whatsapp, to_whatsapp, message):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_='whatsapp:' + from_whatsapp,
        to='whatsapp:' + to_whatsapp
    )
    return message.sid

def send_email_gmail(subject, body, to_email, from_email, password):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(from_email, password)
        server.send_message(msg)

def send_sms_twilio(account_sid, auth_token, from_number, to_number, message):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=from_number,
        to=to_number
    )
    return message.sid

def make_call(account_sid, auth_token, from_number, to_number, twiml_url):
    client = Client(account_sid, auth_token)
    call = client.calls.create(
        to=to_number,
        from_=from_number,
        url=twiml_url
    )
    return call.sid

def post_tweet(api_key, api_secret, access_token, access_secret, text):
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
    api = tweepy.API(auth)
    api.update_status(status=text)
    return "Tweet posted successfully!"

def download_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.prettify()

def send_whatsapp_kit(number, message):
    kit.sendwhatmsg_instantly(number, message, wait_time=15, tab_close=True)
    return "WhatsApp message sent!"

def droidcam_stream(ip, port):
    url = f"http://{ip}:{port}/video"
    cap = cv2.VideoCapture(url)
    placeholder = st.empty()
    stop_stream = False
    stop_button = st.button("Stop Stream")
    while cap.isOpened() and not stop_stream:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to grab frame")
            break
        placeholder.image(frame, channels="BGR")
        time.sleep(0.1)
        if stop_button:
            stop_stream = True
    cap.release()
    cv2.destroyAllWindows()
    placeholder.empty()

def yoursarthi(prompt):
    response = model.generate_content(
        f'''You are a Linux engineer. Convert the user prompt into a single Linux command.
        Do not use quotes or bash script, only single command like: date, ls, etc.
        Prompt: {prompt}'''
    )
    return response.text.strip()

def get_voice_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Speak now...")
        audio = r.listen(source)
        try:
            return r.recognize_google(audio)
        except sr.UnknownValueError:
            st.error("Could not understand audio")
        except sr.RequestError as e:
            st.error(f"Speech recognition error: {e}")
    return ""

# ======================
# Streamlit UI
# ======================

st.set_page_config(page_title="Vyuha - All-in-One Utility", layout="wide")
st.title("🚀 Vyuha - Universal Utility Platform")

# Sidebar navigation
menu = st.sidebar.selectbox("Navigation", [
    "Home", 
    "WhatsApp Messaging", 
    "Email", 
    "SMS", 
    "Voice Call", 
    "Google Search", 
    "Twitter", 
    "Web Scraping",
    "Linux Command (Vyuha)",
    "DroidCam"
])

if menu == "Home":
    st.subheader("Welcome to Vyuha!")
    st.write("""
    **Vyuha** is an all-in-one utility platform that integrates:
    - Messaging (WhatsApp/SMS)
    - Email communications
    - Voice calls
    - AI-powered web search
    - Social media posting
    - Web scraping
    - Remote Linux command execution
    - Mobile camera streaming
    """)
    st.image("https://via.placeholder.com/800x400?text=Vyuha+Interface", use_column_width=True)

elif menu == "WhatsApp Messaging":
    st.subheader("WhatsApp Messaging")
    method = st.radio("Select Method", ["Twilio", "pywhatkit"])
    if method == "Twilio":
        st.write("### Send WhatsApp via Twilio")
        account_sid = st.text_input("Twilio Account SID")
        auth_token = st.text_input("Twilio Auth Token", type="password")
        from_num = st.text_input("From Number (Twilio WhatsApp)")
        to_num = st.text_input("To Number (with country code)")
        message = st.text_area("Message")
        if st.button("Send WhatsApp"):
            sid = send_whatsapp_twilio(account_sid, auth_token, from_num, to_num, message)
            st.success(f"Message sent! SID: {sid}")
    else:
        st.write("### Send WhatsApp via pywhatkit")
        number = st.text_input("Recipient Number (with country code)")
        message = st.text_area("Message")
        if st.button("Send WhatsApp"):
            result = send_whatsapp_kit(number, message)
            st.success(result)

elif menu == "Email":
    st.subheader("Email Services")
    email_type = st.radio("Select Email Type", ["Gmail", "Custom SMTP"])
    if email_type == "Gmail":
        st.write("### Send Email via Gmail")
        sender = st.text_input("Your Gmail")
        password = st.text_input("App Password", type="password")
        receiver = st.text_input("Recipient Email")
        subject = st.text_input("Subject")
        body = st.text_area("Body")
        if st.button("Send Email"):
            send_email_gmail(subject, body, receiver, sender, password)
            st.success("Email sent successfully!")
    else:
        st.write("### Send Email via Custom SMTP")
        st.info("Custom SMTP not implemented in this version.")

elif menu == "SMS":
    st.subheader("SMS Services")
    account_sid = st.text_input("Twilio Account SID")
    auth_token = st.text_input("Twilio Auth Token", type="password")
    from_num = st.text_input("From Number (Twilio)")
    to_num = st.text_input("To Number (with country code)")
    message = st.text_area("Message")
    if st.button("Send SMS"):
        sid = send_sms_twilio(account_sid, auth_token, from_num, to_num, message)
        st.success(f"SMS sent! SID: {sid}")

elif menu == "Voice Call":
    st.subheader("Voice Call Services")
    account_sid = st.text_input("Twilio Account SID")
    auth_token = st.text_input("Twilio Auth Token", type="password")
    from_num = st.text_input("From Number (Twilio)")
    to_num = st.text_input("To Number (with country code)")
    twiml_url = st.text_input("TwiML URL")
    if st.button("Make Call"):
        sid = make_call(account_sid, auth_token, from_num, to_num, twiml_url)
        st.success(f"Call initiated! SID: {sid}")

elif menu == "Google Search":
    st.subheader("Google Search (AI Powered)")
    query = st.text_input("Search Query")
    if st.button("Search") and query:
        with st.spinner("Thinking..."):
            try:
                response = model.generate_content(f"Answer as a Google search result: {query}")
                st.subheader("AI Search Result")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error: {e}")

elif menu == "Twitter":
    st.subheader("Twitter Post")
    api_key = st.text_input("API Key")
    api_secret = st.text_input("API Secret", type="password")
    access_token = st.text_input("Access Token")
    access_secret = st.text_input("Access Token Secret", type="password")
    tweet = st.text_area("Tweet Content")
    if st.button("Post Tweet"):
        result = post_tweet(api_key, api_secret, access_token, access_secret, tweet)
        st.success(result)

elif menu == "Web Scraping":
    st.subheader("Web Scraping")
    url = st.text_input("URL to Scrape")
    if st.button("Scrape"):
        data = download_data(url)
        st.code(data)

elif menu == "Linux Command (Vyuha)":
    st.subheader("Vyuha - Linux Command Execution")
    col1, col2 = st.columns(2)
    with col1:
        st.write("### SSH Connection")
        host = st.text_input("Remote IP")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
    with col2:
        st.write("### Command Input")
        input_method = st.radio("Input Method", ["Text", "Voice"])
        command = ""
        if input_method == "Voice":
            if st.button("Start Voice Command"):
                command = get_voice_input()
                st.text_area("Voice Command", value=command)
        else:
            command = st.text_input("Your Command (e.g., 'list files')")
        if st.button("Execute Command"):
            linux_cmd = yoursarthi(command)
            st.write(f"Generated Command: `{linux_cmd}`")
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, 22, username, password)
                stdin, stdout, stderr = ssh.exec_command(linux_cmd)
                output = stdout.read().decode()
                error = stderr.read().decode()
                st.subheader("Command Output")
                if output:
                    st.code(output)
                if error:
                    st.error(error)
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

elif menu == "DroidCam":
    st.subheader("DroidCam Streaming")
    ip = st.text_input("Device IP", "192.168.0.0")
    port = st.text_input("Port", "4747")
    if st.button("Start Stream"):
        droidcam_stream(ip, port)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Vyuha v1.0 | All-in-One Utility Platform")
