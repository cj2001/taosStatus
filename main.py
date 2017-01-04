"""
This skill was written by Clair J. Sullivan (cj2001@gmail.com). It is based on the 
favorite color example for Python.
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6
"""

import urllib2
from bs4 import BeautifulSoup
import lxml
import re


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
#    return {
#        'outputSpeech': {
#            'type': 'PlainText',
#            'text': output
#        },
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output

        },
       'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    #If we wanted to initialize the session to have some attributes we could
    #add those here
    

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Taos Ski Valley status report. " \
                    "Please inquire about the status of a lift by saying " \
                    "What is the status of lift name?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please ask what the status of a particular lift is by saying, " \
                    "What is the status of lift name?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for skiing Taos Ski Valley. " \
                    "Have fun!"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

###################################################
#
# THE MEAT
#
###################################################

def get_status_from_session(intent, session):
    
    session_attributes = {}
    reprompt_text = None
    
    if intent['slots']['LiftName']['value']:

        taosrep = "https://www.skitaos.com/lifts-trails/"
        bspage = urllib2.urlopen(taosrep).read()
        soup = BeautifulSoup(bspage)

        lifts = soup.find("div", "display-lifts")
        liftNames = lifts.find_all("span","title")
        status = lifts.find_all("svg")

        #######################
        #
        # CHAIR LIFTS
        #
        #######################
        
        # Create a list of lift names

        nameList = []
        for l in liftNames:
            y = l.text.strip()
            nameList.append(y)
        names = [n.lower() for n in nameList]
        # Create a list of lift statuses   
    
        liftStatus = []
        for stat in status:
            if re.search("OPEN", str(stat)):
                liftStatus.append("OPEN")
            elif re.search("CLOSED", str(stat)):
                liftStatus.append("CLOSED")
            elif re.search("HOLD", str(stat)):
                liftStatus.append("HOLD")
            else:
                liftStatus.append("UNKNOWN")
        
        # Combine the two as a dict

        di = dict(zip(names,liftStatus))
        
        #######################
        #
        # TRAIL STATUS
        #
        #######################
        
        trails = soup.find("div", "display-trails")
        trailNames = trails.find_all("span","title")

        tr = []
        for l in trailNames:
            y = l.text.strip()
            tr.append(y)
            
        runStatus = trails.find_all("td", "text-center")
        
        level = []
        groomed = []
        status = []
        for i in range(0,len(runStatus),3):
    
            # Get trail level
            if re.search("BEGINNER", str(runStatus[i])):
                level.append("BEGINNER")
            elif re.search("INTERMEDIATE", str(runStatus[i])):
                level.append("INTERMEDIATE")
            elif re.search("ADVANCED", str(runStatus[i])):
                level.append("ADVANCED")
            elif re.search("DIFFICULT", str(runStatus[i])):
                level.append("EXPERT")
            else:
                level.append("UNKNOWN")
        
            # Get groomed status, if it exists
            if re.search("OPEN", str(runStatus[i+1])):
                groomed.append("GROOMED")
            else:
                groomed.append("NOT GROOMED")
    
            # Get open status
            if re.search("OPEN", str(runStatus[i+2])):
                status.append("OPEN")
            else:
                status.append("CLOSED")
                
        zz = zip(level, groomed, status)
        trailDict = dict(zip(tr,zz))
    
        chosenLift = intent['slots']['LiftName']['value']
        chosenStat = di[chosenLift]

        speech_output = "<speak> " + chosenLift + " is currently listed as " + chosenStat + ".  Have fun!</speak>"
    
        should_end_session = True

    else:
        speech_output = "I need more information. " \
                        "You can say, for example, what is the status of Lift One?"
        should_end_session = False

    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    
    if intent_name == "taosStatus":
        return get_status_from_session(intent, session)
    #elif intent_name == "MyColorIsIntent":
    #    return set_color_in_session(intent, session)
    #elif intent_name == "WhatsMyColorIntent":
    #    return get_color_from_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request() 
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

