# Webex Virtual Museum

The purpose of this sample code is to show how the Webex Meetings Widget and Webex API can support a museum to provide virtual tours for remote visitors. Besides the workflow around guest user, meeting and space creation for preparation, the demo covers the embedding of the Meetings and Space Widget to deliver the actual event. 

   >  This demo uses the [Embeddable Meeting Widget project](https://github.com/WXSD-Sales/MeetingWidget) to embed the Webex Meetings Widget via CDN link. 


## Contacts
* ramrenne

## Solution Components
* Webex REST API
* Webex Meetings Widget
* Webex Space Widget 

## Workflow
![/IMAGES/migration_workflow.png](/IMAGES/workflow.png)

## Preparation

Webex does offer a feature to prompt a user to provide a meeting password for joining an event. We disable this feature for this demo in exchange for an easier workflow for guests based on the Webex Meetings Widget. 

In the [Webex Control Hub](https://admin.webex.com/), go to: 

Services: Meeting > Click the row of the preferred site > Configure Site > Common Settings: Security:

* unselect: Enforce meeting password when joining from video conferencing systems
* unselect: Enforce meeting password when joining by phone


## Installation

1. Make sure you have [Python 3.8.0](https://www.python.org/downloads/) and [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) installed

2.	(Optional) Create and activate a virtual environment 
    ```
    python3 -m venv [add name of virtual environment here] 
    source [add name of virtual environment here]/bin/activate
    ```
  * Access the created virtual environment folder
    ```
    cd [add name of virtual environment here] 
    ```

3. Clone this Github repository into a local folder:  
  ```git clone [add github link here]```
  * For Github link: 
      In Github, click on the **Clone or download** button in the upper part of the page > click the **copy icon**  
      ![/IMAGES/giturl.png](/IMAGES/giturl.png)
  * Or simply download the repository as zip file using 'Download ZIP' button and extract it

4. Access the downloaded folder:  
    ```cd gve_devnet_webex_virtual_museum```

5. Install all dependencies:  
  ```pip install -r requirements.txt```

Use the same login for step 6. - 8. :

6. Setup or use an existing Webex [Guest Issuer](https://developer.webex.com/docs/guest-issuer) and note the guest issuer ID and secret for a later step.

7. Set up a [Bot Token](https://developer.webex.com/docs/bots) for a later step.

8. Create a [Personal Access Token](https://developer.webex.com/docs/getting-started) for a later step, bases on a normal or admin account. Only an admin token allows to create a meeting for another user/speaker of the organization as part of the demo.
   > This token has a short lifetime (12 hours) and is meant for testing purposes. Instead of providing an static user token it is also possible to use an oAuth integration: [OAuth example](https://github.com/gve-sw/wbxteams_oauth_w_refresh_sample). 

9. Fill in your variables in the **.env** file:      
      
  ```  
    GUEST_ISSUER_SECRET="[guest issuer secret from step 6]"
    GUEST_ISSUER_ID="[guest issuer ID from step 6]"

    BOT_TOKEN="[Bot Token token from 7]"
    USER_TOKEN="[Personal Access Token token from 8]"
    HOST="https://webexapis.com/v1/"

    APP_URL="[URL under which the app is reachable. Local default: https://127.0.0.1:5000]???"
    SENDER_EMAIL="[email address from which notification emails will be send]???"
    SENDER_PW="[password of sender email account]"
  ```

  > Note: Make sure that the sender email account settings allow the sending of emails via an external app (e.g. [Instructions for gmail.com account](https://www.google.com/settings/security/lesssecureapps) - Use only for testing purposes.)
  
  > Note: Mac OS hides the .env file in the finder by default. View the demo folder for example with your preferred IDE to make the file visible.

9. Run the application   
  ```python3 app.py```


Assuming you kept the default parameters for starting the Flask application, the address to navigate to would be:
https://127.0.0.1:5000

This demo runs the code with HTTP**S** without using a real certificate. Thereby, you will need to accept the warnings generated by the browser to proceed.

In case you used a non-admin account for step 8 of these instructions: Use the same email address for the speaker field as used in the mentioned step.
If you used an admin account in step 8: It is possible to use a speaker email address that differentiates from the email address used in the mentioned step. The speaker email address has to be from a user within the same organization. 

## Additional Steps to Demonstrate Access from an External Device

To access this application from an external device it must be reachable over an internet accessible URL. Therefore, it can be deployed on different IaaS platform like Heroku, Amazon Web Services Lambda, Google Cloud Platform (GCP) and more. Alternatively, it is possible to use the tool ngrok for this reason. Please be aware that ngrok can be blocked in some corporate networks.


## Screenshots

![/IMAGES/step1.png](/IMAGES/step1.png)
![/IMAGES/step2.png](/IMAGES/step2.png)
![/IMAGES/step3.png](/IMAGES/step3.png)
![/IMAGES/email.png](/IMAGES/email.png)
![/IMAGES/step4.png](/IMAGES/step4.png)


## More Useful Resources
 - Webex REST API: https://developer.webex.com/docs/getting-started
 - Webex Widgets: https://developer.webex.com/docs/widgets
 - Webex Meetings Widget (via CDN links): https://github.com/WXSD-Sales/MeetingWidget


### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.