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

from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
import time
import os

import mailing_service
import api_service

#Load All Environment Variables
load_dotenv()

app = Flask(__name__)


scheduled_tours=[]
"""
[{
"meeting_id": ,
"meeting_title": ,
"meeting_start_date": ,
"meeting_end_date": ,
"meeting_speaker_email": ,
"meeting_sip": ,
"space_title":,
"space_id":,
"joined_guests": [
    {
    "guest_id":
    "name":
    "guest_token":
    }
]
}]
"""

bookings=[]
"""
[{
"booking_id":,
"booking_person_name": ,
"booking_person_email": ,
"ticket_count": ,
"booked_tour": 
}]
"""


def get_associated_list_element_or_none(valueToCompareTo, identifier, listToScan):
    '''
    Returns the information for the first element with a specific value and key pair.
    If no associated pair is available, none is returned.
    '''

    print('----------------Find element in storage lists --------------------')

    found_element = None
    
    for listElement in listToScan:
        if listElement[identifier] == valueToCompareTo:
            found_element = listElement
            break

    print(found_element)

    return found_element


def speaker_is_logged_in_check(speaker_email):
    '''
    Checks if the provided user token in the .env file (= person who is logged in) is the same person as the speaker for the event.
    If not, retrieve the email address of the logged in user. 
    '''

    speaker_is_logged_in = False
    
    user_info = api_service.getOwnDetails('user_token')
    logged_in_email = user_info['emails'][0]
    
    for email in user_info['emails']:
        if email == speaker_email:
            speaker_is_logged_in = True
            logged_in_email = speaker_email

    print("Logged in user: " + str(logged_in_email) + " is speaker: " + str(speaker_is_logged_in))
                
    return speaker_is_logged_in, logged_in_email


@app.route('/', methods=['GET', 'POST'])
def schedule():
    '''
    Step 1: Create meeting and space/room based on user input. 
    This step is typically done by an admin or presenter of the museum.
    '''
    global scheduled_tours

    if request.method == 'POST':

        try:
            tour_title = request.form.get("tour_title")
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")
            speaker_email = request.form.get("speaker_email")

            room_title = f"{tour_title} at {start_date}"

            #Create room (via bot token). Bot will automatically be participant in the room and be able to add more participants to it
            room = api_service.createRoom(room_title)
            room_id= room['id']
            
            #Add speaker to room (via bot token)
            membership = api_service.createMembership(room_id, speaker_email, None, True)

            #Create welcome message (via bot token)
            message_text = f"Welcome to our digital tour: {tour_title}"
            message = api_service.createMessage(room_id, message_text)

            #Check if the provided user token in the .env file (= user logged in) is the speaker (via user token)
            speaker_is_logged_in, logged_in_email = speaker_is_logged_in_check(speaker_email)

            #Create meeting (via user token)
            meeting = api_service.createMeeting(room_title, start_date, end_date, speaker_email, logged_in_email, speaker_is_logged_in)

            #Save scheduled tour date in a list with dicts
            scheduled_tour = {
                                "meeting_id": meeting['id'],
                                "meeting_title": meeting['title'],
                                "meeting_start_date": start_date,
                                "meeting_end_date": end_date,
                                "meeting_speaker_email": meeting['hostEmail'],
                                "meeting_sip": meeting['sipAddress'],
                                "space_title": room['title'],
                                "space_id": room_id,
                                "joined_guests": []
                            }

            scheduled_tours.append(scheduled_tour)

            return render_template('step2_bookTour.html', scheduled_tour=scheduled_tour)
        
        except Exception as e: 
            print(f'EXCEPTION!! {e}')  
            return render_template('step1_scheduleTour.html', error=True, errormessage=e)

    return render_template('step1_scheduleTour.html')



@app.route('/book', methods=['GET', 'POST'])
def book():
    '''
    Step 2 and 3: Send out invitiation email with joining link to person that was booking 1 or more guest tickets. 
    This step is typically triggered by the museum visiter when booking a tour for 1 person or a group.
    '''
    global scheduled_tours, bookings

    if request.method == 'POST':
        try:
            booking_person_name = request.form.get("booking_person_name")
            booking_person_email = request.form.get("booking_person_email")
            tour_id = request.form.get("tour_id")
            ticket_count = int(request.form.get("ticket_count"))

            #Retrieve associated tour data
            scheduled_tour = get_associated_list_element_or_none(tour_id, "meeting_id", scheduled_tours)
            meeting_end_time = scheduled_tour['meeting_end_date']

            #Send email to guest
            booking_id = str(len(bookings) + 1)
            meeting_title = scheduled_tour['meeting_title']
            start_date = scheduled_tour['meeting_start_date']
            join_link = mailing_service.sendMail(booking_person_name, booking_id, booking_person_email, meeting_title, start_date, ticket_count)
            
            #Save booking data in a list with dicts
            booking = {
                                "booking_id": booking_id,
                                "booking_person_name": booking_person_name,
                                "booking_person_email": booking_person_email,
                                "ticket_count": ticket_count,
                                "booked_tour": tour_id
                            }

            bookings.append(booking)

            return render_template('step3_sendEmail.html', scheduled_tour=scheduled_tour , booking=booking, join_link=join_link)

        except Exception as e: 
            print(f'EXCEPTION!! {e}')  
            return render_template('step1_scheduleTour.html', error=True, errormessage=e)

    return render_template('step1_scheduleTour.html')


app.route('/join?booking_id=<booking_id>')
@app.route('/join', methods=["POST", "GET"])
def join():
    '''
    Step 4: Show guest registration page, when guests click the join link from the invitation email. 
    Request name of the guest to create a guest token and add the guest to the Webex Space for the booked event.
    This step is typically done by the museums tour guest itself.
    '''
    global scheduled_tours, bookings

    booking_id = request.args.get('booking_id')

    #Retrieve information about guest based on booking id URl parameter
    booking_data = get_associated_list_element_or_none(booking_id, "booking_id", bookings)

    #Retrieve associated tour data
    tour_id = booking_data['booked_tour']
    scheduled_tour = get_associated_list_element_or_none(tour_id, "meeting_id", scheduled_tours)
    meeting_end_time = scheduled_tour['meeting_end_date']  

    if request.method == 'GET':

         #Check if 1 or more tickets for this booking are not in use yet. A ticket is in use whenever a guest registers/joins the event via the shared link.
        if len(scheduled_tour["joined_guests"]) >= booking_data['ticket_count']:
            return render_template('step4_guestInfo.html', booking_id = booking_id, scheduled_tour=scheduled_tour, no_free_tickets=True)
        #If there are still free tickets available for this booking.
        else:
            return render_template('step4_guestInfo.html', booking_id = booking_id, scheduled_tour=scheduled_tour)

    elif request.method == 'POST':

        guest_name = request.form.get("guest_name")

        # Create guest issuer/user
        guest = api_service.createGuestIssuer(guest_name, meeting_end_time)
        
        # Retrieve ID of guest user
        guest_token = guest['token']
        guest_user = api_service.getOwnDetails(guest_token)

        #Add guest user based on its ID to the chat room of the booked tour (via bot token)
        person_id = guest_user['id']
        space_id = scheduled_tour['space_id']
        membership = api_service.createMembership(space_id, None, person_id, False)

        guest_id = str(len(scheduled_tour["joined_guests"]) + 1)

        joining_guest = {
                        "guest_id": guest_id,
                        "guest_name": guest_name, 
                        "guest_token": guest_token
                        }

        scheduled_tour["joined_guests"].append(joining_guest)

        return redirect('/meeting?booking_id='+booking_id+'&guest_id='+guest_id)


app.route('/meeting?booking_id=<booking_id>&guest_id=<guest_id>')
@app.route('/meeting', methods=["POST", "GET"])
def meeting():
    """
    Step 5: Show meetings widget page.
    This step is typically done by the museums tour guest itself.
    """

    global scheduled_tours, bookings

    #Retrieve information about guest based on booking id URL parameter
    booking_id = request.args.get('booking_id')
    booking_data = get_associated_list_element_or_none(booking_id, "booking_id", bookings)

    #Retrieve information about booked tour based on the meeting id
    tour_id = booking_data['booked_tour']
    tour_data = get_associated_list_element_or_none(tour_id, "meeting_id", scheduled_tours)

    #Get info/token for specific guest
    guest_id = request.args.get('guest_id')
    guest_data = get_associated_list_element_or_none(guest_id, "guest_id", tour_data["joined_guests"])

    #Information required for the join view
    guest_token = guest_data['guest_token']
    meeting_sip = tour_data['meeting_sip']
    space_id = tour_data['space_id'] 

    return render_template('step5_joinTour.html', guest_token = guest_token, tour_space = space_id, meeting_sip = meeting_sip)


if __name__ == '__main__':

    # Start the Flask web server
    app.run(ssl_context='adhoc')


    
