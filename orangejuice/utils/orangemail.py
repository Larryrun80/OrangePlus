#!/usr/bin/env python
#Filename: orangejuice/utils/orangemailer.py

import configparser
import os
import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class OrangeMail:
    ''' This Class is To Simplify Send Mail matters. '''

    def __init__(self, section_name):
        # Read config file and init mail settings
        self._config_file = os.path.split(os.path.dirname(__file__))[0] 
        self._config_file += '/conf/orangejuice.conf'
        config = configparser.ConfigParser()
        config.read(self._config_file)

        self.smtp = smtplib.SMTP(config.get(section_name,'SMTP'))
        self.smtp.login(config.get(section_name,'User'), config.get(section_name,'Password'))
        self.send_from = config.get(section_name,'User')

    def send_mail(self, send_to, subject, text, files=None):
        # Check input data format
        if files and not isinstance(files, list):
            raise RuntimeError('Invalid Files, Should Pass a List!')
        if not isinstance(send_to, list):
            raise RuntimeError('Invalid Send_To Info, Should Pass a List!')

        # Build Mail info
        msg = MIMEMultipart();
        msg['From'] = self.send_from
        msg['To'] = email.utils.COMMASPACE.join(send_to)
        msg['Subject'] = subject
        msg.attach( MIMEText(text) )

        # Attach files to mail if a filename list passed
        if files:
            for file in files:
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload( open(file,"rb").read() )
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', 'attachment', filename=os.path.split(file)[1])
                msg.attach(attachment)

        # Send mail and quit
        self.smtp.send_message(msg)
        self.smtp.quit()

        # TODO: Dealing Exceptions
