import os
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar']

# Token storage directory
TOKEN_DIR = "token_files"
TOKEN_FILE = "token_calendar_v3.json"

# Resource: https://learndataanalysis.org/google-py-file-source-code/
def create_service(client_secret_file, api_name, api_version, *scopes, prefix=''):
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]
    
    creds = None
    working_dir = os.getcwd()
    token_dir = 'token files'
    token_file = f'token_{API_SERVICE_NAME}_{API_VERSION}{prefix}.json'

    ### Check if token dir exists first, if not, create the folder
    if not os.path.exists(os.path.join(working_dir, token_dir)):
        os.mkdir(os.path.join(working_dir, token_dir))

    if os.path.exists(os.path.join(working_dir, token_dir, token_file)):
        creds = Credentials.from_authorized_user_file(os.path.join(working_dir, token_dir, token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(os.path.join(working_dir, token_dir, token_file), 'w') as token:
            token.write(creds.to_json())

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False)
        print(API_SERVICE_NAME, API_VERSION, 'service created successfully')
        return service
    except Exception as e:
        print(e)
        print(f'Failed to create service instance for {API_SERVICE_NAME}')
        os.remove(os.path.join(working_dir, token_dir, token_file))
        return None

def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
    dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
    return dt

CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar']

service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)


# Function to list user calendar events
def list_user_events(service):
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=now,
        maxResults=10, singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    if not events:
        st.write("No upcoming events found.")
    else:
        st.write("### Upcoming Events")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            st.write(f"- **{event.get('summary')}** at {start}")

# Function to add an event to Google Calendar
def add_event_to_calendar(service, summary, start_time, duration=1):
    event = {
        'summary': summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
        'end': {'dateTime': (start_time + datetime.timedelta(hours=duration)).isoformat(), 'timeZone': 'UTC'},
    }
    service.events().insert(calendarId='primary', body=event).execute()

# Streamlit app layout
st.title("ChunkIt: Google Calendar Integration and Automation")


if service:
    # Welcome user
    user_info = service.calendarList().get(calendarId='primary').execute()
    user_name = user_info.get('summary', 'User')
    st.success(f"Welcome, {user_name}!")

    # Display calendar events
    #list_user_events(service)

    col = st.columns((9, 3, 3))

# Initialize session state for inputs and subtasks
if "query" not in st.session_state:
    st.session_state["query"] = ""
if "due_date" not in st.session_state:
    st.session_state["due_date"] = None
if "subtasks" not in st.session_state:
    st.session_state["subtasks"] = []

# Input section (only once)
st.write("### Task Input")
query = st.text_input(
    "Enter your task and let AI chunk it for you!", 
    st.session_state["query"], 
    key="query_input"
)
d = st.date_input(
    "Due Date", 
    value=st.session_state["due_date"], 
    key="due_date_input"
)

chunkify = st.button("Chunkify!", key="chunkify_button")

if chunkify:
    # Save inputs to session state
    st.session_state["query"] = query
    st.session_state["due_date"] = d

    # Simulate AI chunkify logic
    st.session_state["subtasks"] = ["Subtask 1: Research topic", "Subtask 2: Write draft", "Subtask 3: Submit report"]

# Subtasks Section
if st.session_state["subtasks"]:
    st.write("### Your Chunkified Subtasks")
    for i, subtask in enumerate(st.session_state["subtasks"], start=1):
        col = st.columns((9, 3))
        with col[0]:
            st.write(f"**Subtask #{i}:** {subtask}")
        with col[1]:
            # Button to add subtask to Google Calendar
            if st.button(f"Add Subtask #{i} to Calendar", key=f"add_subtask_{i}_button"):
                try:
                    # Calculate start and end times
                    event_date = datetime.datetime.combine(st.session_state["due_date"], datetime.datetime.min.time())
                    start_time = event_date + datetime.timedelta(days=i - 1)
                    end_time = start_time + datetime.timedelta(hours=1)

                    # Define the event
                    event = {
                        'summary': subtask,
                        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
                        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'},
                    }
                    
                    # Insert event into Google Calendar
                    service.events().insert(calendarId='primary', body=event).execute()
                    st.success(f"Subtask #{i} successfully added to your Google Calendar!")
                except Exception as e:
                    st.error(f"Failed to add Subtask #{i} to Google Calendar. Error: {e}")



# Fetch the user's primary calendar ID
try:
    calendar_list = service.calendarList().list().execute()
    primary_calendar_id = None

    # Find the primary calendar
    for calendar_entry in calendar_list.get('items', []):
        if calendar_entry.get('primary', False):
            primary_calendar_id = calendar_entry.get('id')
            break

    if primary_calendar_id:
        # Construct the iframe URL for the user's primary calendar
        calendar_embed_url = f"https://calendar.google.com/calendar/embed?src={primary_calendar_id}&ctz=UTC"

        # Add the user's calendar
        st.markdown(
            f"""
            <div style="margin: 5rem"></div>
            <div style="display: flex; align-items: center; justify-content: center"> 
                <iframe src="{calendar_embed_url}" style="border-width:0" width="600" height="450" frameborder="0" scrolling="no"></iframe>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning("Unable to retrieve your primary calendar. Please ensure you have access to it.")
except Exception as e:
    st.error(f"An error occurred while retrieving your calendar: {e}")



