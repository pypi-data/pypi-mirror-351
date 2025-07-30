'''
Author: Kevin Zhu
The main functions for kzutil
'''

import datetime
import smtplib
import time
import pytz

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(sender_email,
               sender_email_app_password,
               recipient,
               main_subject,
               html,
               server_info = ('smtp.gmail.com', 587),
               timezone = 'US/Eastern'):

    '''
    Attempts to send an email from the sender email to the recipient with a subject of main_subject @ Date Time.

    Parameters
    ----------
    string sender_email:
        the email to send from
    string sender_email_app_password:
        the app password of the sender
    string recipient:
        the email of the recipient
    string main_subject:
        the main title of the email (excluding date/time)
    string html:
        the html to send
    tuple server_info, defaults to ('smtp.gmail.com', 587):
        the server name and the port to use
    string timezone, optional:
        the appropriate pytz name
    '''

    try:
        print('Connecting to Server...')
        server = smtplib.SMTP(*server_info)
        server.ehlo()
        server.starttls()
        server.login(sender_email, sender_email_app_password)

        email = MIMEMultipart('related')
        email['From'] = sender_email
        latest_time = datetime.datetime.now(pytz.timezone(timezone))
        current_date = datetime.datetime.strftime(latest_time, '%b %d, %Y')
        email_time = datetime.datetime.strftime(latest_time, '%I:%M:%S %p %Z')

        full_subject = f'{main_subject} @ {current_date} {email_time}'
        print(f'({full_subject})')

        email['To'] = recipient
        email['Subject'] = full_subject

        email.attach(MIMEText(html, 'html'))

        server.sendmail(sender_email, [recipient], email.as_string())

        time.sleep(3)

    except Exception as e:
        print(f'Error encountered when sending email: {e}')

    finally:
        server.quit()