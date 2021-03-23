import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser
import os.path

# load the config.ini file and take the email username and password from it
config = configparser.ConfigParser()

if os.path.isfile('config.ini') is not True:
    print('The config.ini file is missing, please create it')
    print('[email]')
    print('username = <username>')
    print('password = <password>')

config.read('config.ini')

# Credentials
username = config['email']['username']
password = config['email']['password']

from_address = username


def send_email(to_address, code):
    """
    Sends an email to an address with the secret code
    :param to_address the address to send the email to
    :param code the secret code
    """
    if "@" not in to_address:
        print(f"{to_address} is not a valid email address, not sending the email")
        return

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "DrawPy verification code"
    msg['From'] = from_address
    msg['To'] = to_address
    # Create the message (HTML).
    html = f"Your verification code is {code}"
    # Record the MIME type - text/html.
    part1 = MIMEText(html, 'html')
    # Attach parts into message container
    msg.attach(part1)
    # Sending the email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(from_address, to_address, msg.as_string())
    server.quit()
