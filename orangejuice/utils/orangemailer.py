#!/usr/bin/env python
#Filename: orangejuice/orangemailer.py

import configparser
import sys
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class OrangeMailer:
    ''' This Class is To Simplify Send Mail matters. '''

    def __init__(self):
        # Read config file and init mail settings
        self._config_file = '/orangejuice/conf/orangejuice.conf'
        config = configparser.ConfigParser()
        config.read(sys.path[0] + self._config_file)

        self.smtp = smtplib.SMTP(config.get('MAIL_INFO','SMTP'))
        self.smtp.login(config.get('MAIL_INFO','User'), config.get('MAIL_INFO','Password'))

    def send_mail(self, send_from, send_to, subject, text, files = None):
        # Check input data format
        if (files and not isinstance(files, list)) or not isinstance(send_to, list):
            raise RuntimeError('Invalid Files!')

        # Build Mail info
        msg = MIMEMultipart();
        msg['From'] = send_from
        msg['To'] = email.utils.COMMASPACE.join(send_to)
        msg['Subject'] = subject
        msg.attach( MIMEText(text) )

        # Attach files to mail if a filename list passed
        if files:
            for file in files:
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload( open(file,"rb").read() )
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', 'attachment', filename=file)
                msg.attach(attachment)

        # Send mail and quit
        self.smtp.send_message(msg)
        self.smtp.quit()

        # TODO: Dealing Exceptions
