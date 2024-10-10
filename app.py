import streamlit as st
import requests
import time
import prompts
import config
from region_voices import REGION_VOICES

st.title(" AI Phone Interview Assistant ") 
st.markdown("# Test out Babblebots' AI Phone Interview Assistant using this page. Just enter your first name and your phone number to receive a call from our AI agent, Eric, who will conduct a short interview for you. Contact us at sales@babblebots.ai if you enjoy the experience and would like to chat with us further!")
st.sidebar.markdown("# Babblebots ")

auth_token = st.secrets["auth_token"]
phone_number_id = st.secrets["phone_number_id"]

# Create the header with Authorization token
headers = {
    'Authorization': f'Bearer {auth_token}',
    'Content-Type': 'application/json',
}

def create_payload(company, candidate_phone_number, candidate_name):
    # Create the payload for the API request
    recruiter = "Eric"        
        
    #config.stt_model["keywords"] = [company, candidate_name]
    first_bot_message = prompts.first_bot_message.format(company=company, recruiter=recruiter)
    config.llm["messages"][0]["content"] = prompts.system_prompt.format(company=company)
    config.llm["messages"][1]["content"] = prompts.user_prompt_with_probing.format(company=company, recruiter = recruiter, first_name = candidate_name)
        
    voice_settings = REGION_VOICES.get(REGION_VOICES['US'])

    data = {
        'assistant': {
            "firstMessage": first_bot_message,
            #"endCallMessage": prompts.end_call_message.format(candidate_name=candidate_name),
            "endCallPhrases": ["Have a great day."],
            "backgroundDenoisingEnabled": True,
            "responseDelaySeconds": 0.8,
            "silenceTimeoutSeconds": 30,
            "transcriber": config.stt_model,
            "model": config.llm,
            "startSpeakingPlan": {
                "waitSeconds": 1.0
            },
            "endCallFunctionEnabled": True,
            "voice": voice_settings,
            "backgroundSound": "off"
        },
        'phoneNumberId': phone_number_id,
        'customer': {
            'number': candidate_phone_number,
        },
    }

    return data


if 'call_id' not in st.session_state:
    st.session_state.call_id = None

def create_call(data):
    # Make the POST request to VAPI to create the phone call
    try: 
        response = requests.post(
            'https://api.vapi.ai/call', headers=headers, json=data
        )

        # Check if the request was successful
        if response.text:
            if response.status_code == 201:
                print('Call created successfully')
                st.session_state.call_id = response.json().get('id', None)
                print(response.json())
            else:
                print('Failed to create call')
                print(response.text)
        else:
            print("No data received to create call")
    except Exception as e:
        print('Error creating call')
        print("Error: ", e)


def get_call_id():
    return st.session_state.get('call_id', None)

company = st.text_input(
    label="Enter the name of the company that the AI assistant is calling on behalf of",
)

candidate_name = st.text_input(
    label="Enter the first name of the candidate here",
)


phone_number = st.text_input(
    label="Enter the candidate's phone number here in the given format ('+' followed by the country-code and mobile-number with no spaces in-between )",
    placeholder="+18888888888",
    
)

if st.button("Make the call", type="primary"):
    try:
        data = create_payload(company, phone_number, candidate_name)
        if(data):
            create_call(data)
            with st.empty():
                st.write("The AI assistant is calling the above number now.")
                time.sleep(5)
                st.write("")
        else:
            print("No payload recieved for creating call")
    except Exception as e:
        print("Error creating call: ", e)

    
