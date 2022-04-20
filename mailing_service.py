# Copyright (c) 2022 Cisco and/or its affiliates.

# This software is licensed to you under the terms of the Cisco Sample
# Code License, Version 1.1 (the "License"). You may obtain a copy of the
# License at

#                https://developer.cisco.com/docs/licenses

# All use of the material herein must be in accordance with the terms of
# the License. All rights not expressly granted by the License are
# reserved. Unless required by applicable law or agreed to separately in
# writing, software distributed under the License is distributed on an "AS
# IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.

import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

# load all environment variables
load_dotenv()

SENDER_EMAIL = os.environ['SENDER_EMAIL']
SENDER_PW = os.environ['SENDER_PW']

APP_URL = os.environ['APP_URL']


def createEmailContent(receiver_name, booking_id, tour_title, tour_date, ticket_count):
    
    title = "Successful booking of the virtual museum tour: " + tour_title
    join_link= APP_URL + "/join?booking_id=" + booking_id

    htmlContent = """\
            <html>
            <head></head>
            <body>
                <p>
                Dear """ + receiver_name + """,
                <br/><br/>
                You successfully booked the virtual tour: <b>""" + tour_title + """</b> for a group of <b>"""+ str(ticket_count) +"""</b>  guests.
                
                It is possible to join the event by clicking the following link at the """ + tour_date + """:
                <br/><br/>
                """+join_link+"""
                <br/><br/>       

                Please share the link with your group of guests. 

                We are looking forward to meeting you all!
                <br/><br/>
                Kind regards,<br/>
                Your Museum Team

                </p>
            </body>
            </html>
            """
    textContent = """Dear """ + receiver_name + """,
                You successfully booked the virtual tour: """ + tour_title + """ for a group of """+ str(ticket_count) +""" guests.
                It is possible to join the event by clicking the following link at the """ + tour_date + """:
                """+join_link+"""      
                Please share the link with your group of guests. 
                We are looking forward to meeting you all!
                Kind regards,
                Your Museum Team"""

    return title, htmlContent, textContent, join_link


def sendMail(receiver_name, booking_id, receiver_email, tour_title, tour_date, ticket_count):

    print('--------------------Send email to participant-----------------------')

    title, html, text, join_link = createEmailContent(receiver_name, booking_id, tour_title, tour_date, ticket_count)

    sender = SENDER_EMAIL
    
    # Create message container 
    msg = MIMEMultipart('alternative')
    msg['Subject'] = title
    msg['From'] = sender
    msg['To'] = receiver_email

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server.
    mail = smtplib.SMTP('smtp.gmail.com', 587)

    mail.ehlo()

    mail.starttls()

    mail.login(SENDER_EMAIL, SENDER_PW)
    mail.sendmail(sender, receiver_email, msg.as_string())
    mail.quit()

    return join_link