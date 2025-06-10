import imaplib
import smtplib
import email
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("APP_PASSWORD")

# Function to connect to the Gmail IMAP server and fetch emails
def check_inbox():
    try:
        # Connect to the IMAP server
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")

        # Search for unseen emails
        status, messages = mail.search(None, 'UNSEEN')
        if status != "OK":
            print("No new messages.")
            return []

        email_ids = messages[0].split()
        email_data = []

        # Fetch the most recent email
        for email_id in email_ids:
            _, msg_data = mail.fetch(email_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    email_data.append(msg)
        
        # Logout from the mail server
        mail.logout()
        
        return email_data
    
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []

# Function to generate a dummy reply (no OpenAI used)
def generate_reply(email_body):
    print(" Using dummy response (no OpenAI API used).")
    return "Thank you for your email. I will get back to you shortly."

# Function to send a reply email
def send_reply(to_address, subject, reply_content):
    try:
        msg = EmailMessage()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_address
        msg["Subject"] = f"Re: {subject}"
        msg.set_content(reply_content)

        # Connect to the SMTP server and send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"✅ Reply sent to: {to_address}")

    except Exception as e:
        print(f"Error sending email: {e}")

# Main function to fetch emails, generate replies, and send them
def main():
    emails = check_inbox()
    if not emails:
        return
    
    for email_msg in emails:
        from_address = email_msg["From"]
        subject = email_msg["Subject"]
        email_body = ""
        
        # Extract email body content
        if email_msg.is_multipart():
            for part in email_msg.walk():
                if part.get_content_type() == "text/plain":
                    email_body = part.get_payload(decode=True).decode()
                    break
        else:
            email_body = email_msg.get_payload(decode=True).decode()
        
        print(f"Replying to: {from_address}")
        # Generate a dummy reply
        reply = generate_reply(email_body)
        # Send the reply
        send_reply(from_address, subject, reply)

if __name__ == "__main__":
    main()
