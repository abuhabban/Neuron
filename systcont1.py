import imaplib
import email
import os
import subprocess

# Email configuration
EMAIL_HOST = 'imap.gmail.com'
EMAIL_USERNAME = 'modulusv1.0@gmail.com'
EMAIL_PASSWORD = 'nthuxtqxmkrdglyl'
SPECIFIC_USER_EMAIL = 'abuhabban6206@gmail.com'  # Change to the specific user's email address

def mark_email_as_unread(mail, email_id):
    mail.store(email_id, '-FLAGS', '\Seen')  # Mark the email as unread

def check_emails():
    # Connect to the email server
    mail = imaplib.IMAP4_SSL(EMAIL_HOST)
    mail.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    mail.select("inbox")

    # Search for emails with the specified criteria
    status, email_ids = mail.search(None, f'(UNSEEN) (FROM "{SPECIFIC_USER_EMAIL}") (SUBJECT "shutdown" OR SUBJECT "logout" OR SUBJECT "restart")')

    if status == 'OK':
        email_id_list = email_ids[0].split()
        for email_id in email_id_list:
            # Fetch the email by ID
            status, email_data = mail.fetch(email_id, '(RFC822)')
            if status == 'OK':
                msg = email.message_from_bytes(email_data[0][1])
                subject = msg['subject'].lower()

                # Perform system actions based on email subject
                if "shutdown" in subject:
                    os.system("shutdown /s /t 1")  # Shutdown
                elif "logout" in subject:
                    os.system("shutdown -l")  # Log out
                elif "restart" in subject:
                    os.system("shutdown /r /t 1")  # Restart

                # If the email is not from the specified user, mark it as unread
                if msg['from'] != SPECIFIC_USER_EMAIL:
                    mark_email_as_unread(mail, email_id)

    # Close the connection
    mail.logout()

if __name__ == "__main__":
    check_emails()
