#!/usr/bin/env python
#Filename: test.py

from orangejuice.utils.orangemailer import OrangeMailer

mailer = OrangeMailer();
mailer.send_mail('guonan@doweidu.com', ['guonan@doweidu.com',], 'test', 'this is a test from python')