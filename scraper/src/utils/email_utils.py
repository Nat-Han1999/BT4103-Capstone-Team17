import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body, to_email):
    """Send an email notification if a change in hash is detected."""
    from_email = "your_email@gmail.com"
    password = "your_email_password"

    # Set up the email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Establish a secure session with Gmail's outgoing SMTP server using your email and password
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)

        # Send the email
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()

        print(f"Email sent to {to_email}.")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")