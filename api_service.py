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

import datetime
import os
import requests
import base64
import json
import jwt
import time
import random

from dotenv import load_dotenv

# load all environment variables
load_dotenv()

'''Global variables'''
BOT_TOKEN = os.environ.get('BOT_TOKEN')
USER_TOKEN = os.environ.get('USER_TOKEN')

HOST = os.environ.get('HOST')

GUEST_ISSUER_SECRET = os.environ.get('GUEST_ISSUER_SECRET')
GUEST_ISSUER_ID = os.environ.get('GUEST_ISSUER_ID')

BOT_HEADERS = {
'Content-Type': 'application/json',
'Authorization': 'Bearer ' +  BOT_TOKEN
}

USER_HEADERS = {
'Content-Type': 'application/json',
'Authorization': 'Bearer ' +  USER_TOKEN
}

'''
Create a meeting.
'''
def createMeeting(room_title, start_date, end_date, speaker_email, logged_in_email, speaker_is_logged_in):

    print('-------------Create Meeting: '+ room_title +'-------------------')

    #If an admin creates the meeting for a speaker, we add the admin as cohost to later on have access to the meeting data
    if speaker_is_logged_in:
        payload = {
                    "title": room_title,
                    "start": start_date,
                    "end": end_date,
                    "allowAnyUserToBeCoHost": False,
                    "enabledJoinBeforeHost": False,
                    "joinBeforeHostMinutes": 0,
                    "publicMeeting": False,
                    "invitees": [
                    ],
                    "sendEmail": True,
                    "hostEmail": speaker_email,
                    "timezone": "Europe/Berlin"
                    }
    else:
        payload = {
                    "title": room_title,
                    "start": start_date,
                    "end": end_date,
                    "allowAnyUserToBeCoHost": False,
                    "enabledJoinBeforeHost": False,
                    "joinBeforeHostMinutes": 0,
                    "publicMeeting": False,
                    "invitees": [
                                {
                                "email": logged_in_email,
                                "displayName":"Admin User",
                                "coHost":"true"
                                }
                    ],
                    "sendEmail": True,
                    "hostEmail": speaker_email,
                    "timezone": "Europe/Berlin"
                    }
    
    
    url = HOST +"/meetings"
    method = "POST"
    response = requests.request(method, url, headers=USER_HEADERS, data=json.dumps(payload))
    response_text = json.loads(response.text)

    print('Response Code: ' + str(response.status_code))
    print(response_text)

    #If an admin creates the meeting for a speaker, he only has full access to the meeting data by retrieving it with the get meetings endpoint. 
    if not speaker_is_logged_in:
        meeting_id = response_text['id']
        response_text = getMeetingInfo(meeting_id)
        
    return response_text


'''
Get information of a meeting
'''
def getMeetingInfo(meeting_id):

    print('-------------Retrieve Meeting Info for meeting: '+ meeting_id +'-------------------')

    url = HOST +"/meetings/" + str(meeting_id)

    method = "GET"
    response = requests.request(method, url, headers=USER_HEADERS)
    response_text = json.loads(response.text)

    print('Response Code: ' + str(response.status_code))
    print(response_text)

    return response_text


'''
Create a room/space.
'''
def createRoom(room_title):

    print('-------------Create Room: '+ room_title +'-------------------')
    
    payload = {
                "title": room_title
                }

    url = HOST +"/rooms"
    method = "POST"
    response = requests.request(method, url, headers=BOT_HEADERS, data=json.dumps(payload))
    response_text = json.loads(response.text)

    print('Response Code: ' + str(response.status_code))
    print(response_text)
    
    return response_text


'''
Create a membership.
'''
def createMembership(room_id, person_email, person_id , is_moderator):

    print('-------------Create Membership-------------------')

    if person_email != None:
        payload = {
                    "roomId": room_id,
                    "personEmail": person_email,
                    "isModerator": is_moderator
                    }
    elif person_id != None:
        payload = {
                    "roomId": room_id,
                    "personId": person_id,
                    "isModerator": is_moderator
                    }

    print(payload)

    url = HOST +"/memberships"
    method = "POST"
    response = requests.request(method, url, headers=BOT_HEADERS, data=json.dumps(payload))
    response_text = json.loads(response.text)

    print('Response Code: ' + str(response.status_code))
    print(response_text)
    
    return response_text


'''
Create a message.
'''
def createMessage(room_id, message_text):

    print('-------------Create Message: '+ message_text +'-------------------')
    
    global USER_HEADERS

    payload = {
                "roomId": room_id,
                "text": message_text
                }

    url = HOST +"/messages"
    method = "POST"
    response = requests.request(method, url, headers=BOT_HEADERS, data=json.dumps(payload))
    response_text = json.loads(response.text)

    print('Response Code: ' + str(response.status_code))
    print(response_text)
    
    return response_text


'''
Create a guest issuer.
'''
def createGuestIssuer(guest_name, meeting_end_time):

    print('-------------Create Guest Issuer for:' + guest_name + '-------------------')

    # The subject is initialized with a large random number to ensure uniqueness
    subject = f"{guest_name}-{random.getrandbits(128)}" 
    
    # Make the gi valid until one hour after the virtual tour meeting
    now = datetime.datetime.now()
    delta = datetime.timedelta(hours=1)
    meeting_end_time = datetime.datetime.strptime(meeting_end_time, '%Y-%m-%d %H:%M:%S')
    token_expire_date = meeting_end_time + delta
    token_end_validity_in_seconds = (token_expire_date - now).total_seconds()  
    exp = str(int(time.time() + token_end_validity_in_seconds)) 

    # Create a JWT payload object
    # 'sub' (subject) will be use to create the Webex Teams user email (sub@org-uuid)
    # 'name' will be the user's display name
    payload = {
            "sub": subject,
            "name": guest_name,
            "iss": GUEST_ISSUER_ID,
            "exp": exp
            }
    
    # Base64 decode the Guest Issuer secret
    secret = base64.b64decode(GUEST_ISSUER_SECRET)
    # Use the jwt library to encode, assemble and sign the JWT
    jwtToken = jwt.encode(payload, secret)

    headers = {
             'Authorization': 'Bearer ' + jwtToken.decode('utf-8')
            }
    
    url = "https://api.ciscospark.com/v1/jwt/login"
    method = "POST"
    response = requests.request(method, url, headers=headers)
    response_text = json.loads(response.text)

    print('Response Code: ' + str(response.status_code))
    print(response_text)
    
    return response_text


'''
Get own people data.
'''
def getOwnDetails(token):

    print('-------------Get people me data------------')
    
    payload={}
    
    headers = {
    'Authorization': 'Bearer ' + token
    }

    url = HOST + "/people/me"
    method = "GET"
    response = requests.request(method, url, headers=headers, data=json.dumps(payload))
    response_text = json.loads(response.text)

    print('Response Code: ' + str(response.status_code))
    print(response_text)

    
    return response_text


