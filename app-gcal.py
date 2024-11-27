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


def get_calendar_service():
    """Authenticate and return the Google Calendar service."""
    creds = None

    # Ensure token directory exists
    if not os.path.exists(TOKEN_DIR):
        os.makedirs(TOKEN_DIR)

    token_path = os.path.join(TOKEN_DIR, TOKEN_FILE)

    # Load existing credentials if available
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Refresh or reauthorize if credentials are invalid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Initiate OAuth2 flow
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", SCOPES
            )
            auth_url, state = flow.authorization_url(prompt='consent')

            # Save state in session
            if "oauth_state" not in st.session_state:
                st.session_state.oauth_state = state

            # Provide login link
            st.write(f'<a target="_self" href="{auth_url}">Log in to Google</a>', unsafe_allow_html=True)

            # Wait for redirect response
            query_params = st.query_params
            if "code" in query_params and "state" in query_params:
                if query_params["state"][0] == st.session_state.oauth_state:
                    flow.fetch_token(authorization_response=f"http://localhost:8501?code={query_params['code'][0]}")
                    creds = flow.credentials

                    # Save new token
                    with open(token_path, "w") as token_file:
                        token_file.write(creds.to_json())
                else:
                    st.error("State mismatch. Please try logging in again.")
                    return None

    # Create Google Calendar service
    if creds:
        return build("calendar", "v3", credentials=creds)
    return None


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

# Authenticate Google Calendar
service = get_calendar_service()

if service:
    # Welcome user
    user_info = service.calendarList().get(calendarId='primary').execute()
    user_name = user_info.get('summary', 'User')
    st.success(f"Welcome, {user_name}!")

    # Display calendar events
    list_user_events(service)

    # Input for task and subtasks
    st.write("### Chunkify Your Task")
    query = st.text_input("Enter your task:")
    task_due_date = st.date_input("Due Date", value=datetime.date.today())
    chunkify_button = st.button("Chunkify")

    if chunkify_button and query:
        # Simulate API call to chunkify task
        API_URL = "http://localhost:9000/api/perform_rag"  # Example API
        # Uncomment to send a real API request
        # response = requests.post(API_URL, json={"query": query})
        # subtasks = response.json().get("subtasks", [])
        # Simulated subtasks for testing
        subtasks = ["Research", "Draft Outline", "Write First Draft", "Edit and Submit"]

        st.write(f"### Subtasks for: {query}")
        for i, subtask in enumerate(subtasks):
            st.write(f"{i + 1}. {subtask}")

        # Add subtasks to calendar
        add_subtasks_button = st.button("Add Subtasks to Google Calendar")
        if add_subtasks_button:
            for i, subtask in enumerate(subtasks):
                start_datetime = datetime.datetime.combine(task_due_date, datetime.time(9, 0)) + datetime.timedelta(hours=i * 2)
                add_event_to_calendar(service, subtask, start_datetime)
            st.success("Subtasks added to Google Calendar!")

    # Add a custom event
    st.write("### Add a Custom Event")
    task_name = st.text_input("Task Name")
    custom_due_date = st.date_input("Task Due Date", value=datetime.date.today())
    task_start_time = st.time_input("Start Time", datetime.time(9, 0))
    add_task_button = st.button("Add Task to Google Calendar")

    if add_task_button and task_name:
        try:
            start_datetime = datetime.datetime.combine(custom_due_date, task_start_time)
            add_event_to_calendar(service, task_name, start_datetime)
            st.success(f"Task '{task_name}' added to your Google Calendar!")
        except Exception as e:
            st.error(f"Failed to add task: {e}")
    else:
        if not task_name:
            st.warning("Please enter a task name.")
        elif not service:
            st.warning("Please log in to Google Calendar to access this feature.")
