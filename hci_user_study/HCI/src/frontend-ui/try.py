# import streamlit as st
# import requests
# import re
# import datetime
# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# import os
# from google.oauth2.credentials import Credentials

# # Google Calendar Setup
# SCOPES = ['https://www.googleapis.com/auth/calendar']
# TOKEN_FILE = "token_calendar_v3.json"

# def create_service(client_secret_file, api_name, api_version, *scopes):
#     CLIENT_SECRET_FILE = client_secret_file
#     API_SERVICE_NAME = api_name
#     API_VERSION = api_version
#     SCOPES = [scope for scope in scopes[0]]

#     creds = None
#     working_dir = os.getcwd()
#     token_file = f"{TOKEN_FILE}"

#     if os.path.exists(os.path.join(working_dir, token_file)):
#         creds = Credentials.from_authorized_user_file(os.path.join(working_dir, token_file), SCOPES)

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
#             creds = flow.run_local_server(port=0)

#         with open(os.path.join(working_dir, token_file), "w") as token:
#             token.write(creds.to_json())

#     try:
#         service = build(API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False)
#         return service
#     except Exception as e:
#         st.error(f"Failed to create Google Calendar service. Error: {e}")
#         return None

# # Initialize Google Calendar service
# CLIENT_SECRET_FILE = 'client_secret.json'
# API_NAME = 'calendar'
# API_VERSION = 'v3'
# service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

# # Streamlit UI
# st.title("🎯 ChunkIt: Task Breakdown & Calendar Integration")

# # FastAPI endpoint URL
# API_URL = "http://localhost:9000/api/perform_rag"

# # Initialize session state
# if "query" not in st.session_state:
#     st.session_state["query"] = ""
# if "due_date" not in st.session_state:
#     st.session_state["due_date"] = None
# if "subtasks" not in st.session_state:
#     st.session_state["subtasks"] = []
# if "due_dates" not in st.session_state:
#     st.session_state["due_dates"] = []

# # Input section
# st.write("### 📝 Task Input")
# with st.container():
#     col1, col2 = st.columns((2, 1))
#     with col1:
#         query = st.text_input(
#             "Describe your task to be chunked:",
#             st.session_state["query"],
#             key="query_input"
#         )
#     with col2:
#         due_date = st.date_input(
#             "Select the due date:",
#             value=st.session_state["due_date"],
#             key="due_date_input"
#         )
# chunkify = st.button("🔧 Chunkify Task")

# # Chunkify logic
# if chunkify:
#     st.session_state["query"] = query
#     st.session_state["due_date"] = due_date

#     try:
#         # Send request to the backend
#         response = requests.post(API_URL, json={"query": query})
#         if response.status_code == 200:
#             # Parse response
#             response_data = response.json()
#             answer_text = response_data.get("answer", "")
#             subtask_pattern = r"Subtask \d+: (.*?)(?=Subtask \d+:|$)"
#             subtasks = re.findall(subtask_pattern, answer_text, re.DOTALL)
#             st.session_state["subtasks"] = subtasks

#             # Extract due dates
#             date_pattern = r"- Due Date: (.+)"
#             st.session_state["due_dates"] = [
#                 match.group(1).strip()
#                 for subtask in subtasks
#                 if (match := re.search(date_pattern, subtask))
#             ]
#         else:
#             st.error("❌ Failed to retrieve subtasks from the API. Please try again.")

#     except Exception as e:
#         st.error(f"An error occurred: {e}")

# # Display subtasks
# if st.session_state["subtasks"] and st.session_state["due_dates"]:
#     st.write("### 📋 Chunkified Subtasks")
#     for i, (subtask, due_date) in enumerate(zip(st.session_state["subtasks"], st.session_state["due_dates"]), start=1):
#         with st.container():
#             st.markdown(
#                 f"""
#                 <div style="background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 10px;">
#                     <h4 style="color: #333;">Subtask #{i}</h4>
#                     <p style="color: #555; font-size: 16px;">{subtask}</p>
#                     <strong>Due Date:</strong> {due_date}
#                 </div>
#                 """,
#                 unsafe_allow_html=True
#             )
#             if st.button(f"Add Subtask #{i} to Calendar", key=f"add_subtask_{i}_button"):
#                 try:
#                     # Calculate start and end times
#                     event_date = datetime.datetime.combine(st.session_state["due_date"], datetime.datetime.min.time())
#                     start_time = event_date + datetime.timedelta(days=i - 1)
#                     end_time = start_time + datetime.timedelta(hours=1)

#                     # Define the event
#                     event = {
#                         'summary': subtask,
#                         'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
#                         'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'},
#                     }

#                     # Insert event into Google Calendar
#                     service.events().insert(calendarId="primary", body=event).execute()
#                     st.success(f"✅ Subtask #{i} successfully added to your Google Calendar!")
#                 except Exception as e:
#                     st.error(f"❌ Failed to add Subtask #{i} to Google Calendar. Error: {e}")

# # Display user's primary calendar
# try:
#     calendar_list = service.calendarList().list().execute()
#     primary_calendar_id = None
#     for calendar_entry in calendar_list.get('items', []):
#         if calendar_entry.get('primary', False):
#             primary_calendar_id = calendar_entry.get('id')
#             break

#     if primary_calendar_id:
#         calendar_embed_url = f"https://calendar.google.com/calendar/embed?src={primary_calendar_id}&ctz=UTC"
#         st.write("### 📅 Your Google Calendar")
#         st.markdown(
#             f"""
#             <div style="margin: 5rem"></div>
#             <div style="display: flex; align-items: center; justify-content: center"> 
#                 <iframe src="{calendar_embed_url}" style="border-width:0" width="600" height="450" frameborder="0" scrolling="no"></iframe>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )
#     else:
#         st.warning("⚠️ Unable to retrieve your primary calendar. Please ensure you have access to it.")
# except Exception as e:
#     st.error(f"❌ An error occurred while retrieving your calendar: {e}")

# good
# import streamlit as st
# import requests
# import re
# import datetime
# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# import os
# import uuid
# from google.oauth2.credentials import Credentials

# # Google Calendar Setup
# SCOPES = ['https://www.googleapis.com/auth/calendar']
# TOKEN_FILE = "token_calendar_v3.json"

# def create_service(client_secret_file, api_name, api_version, *scopes):
#     CLIENT_SECRET_FILE = client_secret_file
#     API_SERVICE_NAME = api_name
#     API_VERSION = api_version
#     SCOPES = [scope for scope in scopes[0]]

#     creds = None
#     working_dir = os.getcwd()
#     token_file = f"{TOKEN_FILE}"

#     if os.path.exists(os.path.join(working_dir, token_file)):
#         creds = Credentials.from_authorized_user_file(os.path.join(working_dir, token_file), SCOPES)

#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
#             creds = flow.run_local_server(port=0)

#         with open(os.path.join(working_dir, token_file), "w") as token:
#             token.write(creds.to_json())

#     try:
#         service = build(API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False)
#         return service
#     except Exception as e:
#         st.error(f"Failed to create Google Calendar service. Error: {e}")
#         return None

# # Initialize Google Calendar service
# CLIENT_SECRET_FILE = 'client_secret.json'
# API_NAME = 'calendar'
# API_VERSION = 'v3'
# service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

# # Streamlit UI
# st.title("🎯 ChunkIt: Task Breakdown & Calendar Integration")

# # FastAPI endpoint URL
# API_URL = "http://localhost:9000/api/perform_rag"

# if service:
#     # Welcome user
#     user_info = service.calendarList().get(calendarId='primary').execute()
#     user_name = user_info.get('summary', 'User')
#     st.success(f"Welcome, {user_name}!")

# # Initialize session state
# if "query" not in st.session_state:
#     st.session_state["query"] = ""
# if "due_date" not in st.session_state:
#     st.session_state["due_date"] = None
# if "subtasks" not in st.session_state:
#     st.session_state["subtasks"] = []
# if "due_dates" not in st.session_state:
#     st.session_state["due_dates"] = []
# if "calendar_refresh" not in st.session_state:
#     st.session_state["calendar_refresh"] = False

# # Function to generate a unique query parameter for the iframe URL
# def generate_calendar_src(primary_calendar_id):
#     unique_param = uuid.uuid4().hex  # Generate a unique identifier
#     return f"https://calendar.google.com/calendar/embed?src={primary_calendar_id}&ctz=UTC&refresh={unique_param}"

# # Input section
# st.write("### 📝 Task Input")
# with st.container():
#     col1, col2 = st.columns((2, 1))
#     with col1:
#         query = st.text_input(
#             "Describe your task to be chunked:",
#             st.session_state["query"],
#             key="query_input"
#         )
#     with col2:
#         due_date = st.date_input(
#             "Select the due date:",
#             value=st.session_state["due_date"],
#             key="due_date_input"
#         )
# chunkify = st.button("🔧 Chunkify Task")

# # Chunkify logic
# if chunkify:
#     st.session_state["query"] = query
#     st.session_state["due_date"] = due_date

#     try:
#         # Send request to the backend
#         response = requests.post(API_URL, json={"query": query})
#         if response.status_code == 200:
#             # Parse response
#             response_data = response.json()
#             answer_text = response_data.get("answer", "")
#             subtask_pattern = r"Subtask \d+: (.*?)(?=Subtask \d+:|$)"
#             subtasks = re.findall(subtask_pattern, answer_text, re.DOTALL)
#             st.session_state["subtasks"] = subtasks

#             # Extract due dates
#             date_pattern = r"- Due Date: (.+)"
#             st.session_state["due_dates"] = [
#                 match.group(1).strip()
#                 for subtask in subtasks
#                 if (match := re.search(date_pattern, subtask))
#             ]
#         else:
#             st.error("❌ Failed to retrieve subtasks from the API. Please try again.")

#     except Exception as e:
#         st.error(f"An error occurred: {e}")

# # Display subtasks
# if st.session_state["subtasks"] and st.session_state["due_dates"]:
#     st.write("### 📋 Chunkified Subtasks")
#     for i, (subtask, due_date) in enumerate(zip(st.session_state["subtasks"], st.session_state["due_dates"]), start=1):
#         with st.container():
#             st.markdown(
#                 f"""
#                 <div style="background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 10px;">
#                     <h4 style="color: #333;">Subtask #{i}</h4>
#                     <p style="color: #555; font-size: 16px;">{subtask}</p>
#                     <strong>Due Date:</strong> {due_date}
#                 </div>
#                 """,
#                 unsafe_allow_html=True
#             )
#             if st.button(f"Add Subtask #{i} to Calendar", key=f"add_subtask_{i}_button"):
#                 try:
#                     # Calculate start and end times
#                     event_date = datetime.datetime.combine(st.session_state["due_date"], datetime.datetime.min.time())
#                     start_time = event_date + datetime.timedelta(days=i - 1)
#                     end_time = start_time + datetime.timedelta(hours=1)

#                     # Define the event
#                     event = {
#                         'summary': subtask,
#                         'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
#                         'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'},
#                     }

#                     # Insert event into Google Calendar
#                     service.events().insert(calendarId="primary", body=event).execute()
#                     st.success(f"✅ Subtask #{i} successfully added to your Google Calendar!")

#                     # Set refresh flag
#                     st.session_state["calendar_refresh"] = True

#                 except Exception as e:
#                     st.error(f"❌ Failed to add Subtask #{i} to Google Calendar. Error: {e}")

# # Refresh button
# if st.button("🔄 Refresh Calendar"):
#     st.session_state["calendar_refresh"] = True

# # Display or refresh user's primary calendar
# try:
#     calendar_list = service.calendarList().list().execute()
#     primary_calendar_id = None
#     for calendar_entry in calendar_list.get('items', []):
#         if calendar_entry.get('primary', False):
#             primary_calendar_id = calendar_entry.get('id')
#             break

#     if primary_calendar_id:
#         # Generate a unique iframe URL if the refresh flag is set
#         calendar_src = generate_calendar_src(primary_calendar_id) if st.session_state.get("calendar_refresh") else f"https://calendar.google.com/calendar/embed?src={primary_calendar_id}&ctz=UTC"

#         st.write("### 📅 Your Google Calendar")
#         st.markdown(
#             f"""
#             <div style="margin: 5rem"></div>
#             <div style="display: flex; align-items: center; justify-content: center"> 
#                 <iframe src="{calendar_src}" 
#                         style="border-width:0" 
#                         width="600" 
#                         height="450" 
#                         frameborder="0" 
#                         scrolling="no"></iframe>
#             </div>
#             """,
#             unsafe_allow_html=True,
#         )
#         st.session_state["calendar_refresh"] = False  # Reset the refresh flag
#     else:
#         st.warning("⚠️ Unable to retrieve your primary calendar. Please ensure you have access to it.")
# except Exception as e:
#     st.error(f"❌ An error occurred while retrieving your calendar: {e}")

# date fix

import streamlit as st
import requests
import re
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import uuid
from google.oauth2.credentials import Credentials

# Google Calendar Setup
SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_FILE = "token_calendar_v3.json"

def create_service(client_secret_file, api_name, api_version, *scopes):
    CLIENT_SECRET_FILE = client_secret_file
    API_SERVICE_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes[0]]

    creds = None
    working_dir = os.getcwd()
    token_file = f"{TOKEN_FILE}"

    if os.path.exists(os.path.join(working_dir, token_file)):
        creds = Credentials.from_authorized_user_file(os.path.join(working_dir, token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(os.path.join(working_dir, token_file), "w") as token:
            token.write(creds.to_json())

    try:
        service = build(API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False)
        return service
    except Exception as e:
        st.error(f"Failed to create Google Calendar service. Error: {e}")
        return None

# Initialize Google Calendar service
CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'calendar'
API_VERSION = 'v3'
service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

# Streamlit UI
st.title("🎯 ChunkIt: make life easy!")

# FastAPI endpoint URL
API_URL = "http://localhost:9000/api/perform_rag"

if service:
    # Welcome user
    user_info = service.calendarList().get(calendarId='primary').execute()
    user_name = user_info.get('summary', 'User')
    st.success(f"Welcome, {user_name}!")

# Initialize session state
if "query" not in st.session_state:
    st.session_state["query"] = ""
if "due_date" not in st.session_state:
    st.session_state["due_date"] = None
if "subtasks" not in st.session_state:
    st.session_state["subtasks"] = []
if "due_dates" not in st.session_state:
    st.session_state["due_dates"] = []
if "calendar_refresh" not in st.session_state:
    st.session_state["calendar_refresh"] = False

# Function to generate a unique query parameter for the iframe URL
def generate_calendar_src(primary_calendar_id):
    unique_param = uuid.uuid4().hex  # Generate a unique identifier
    return f"https://calendar.google.com/calendar/embed?src={primary_calendar_id}&ctz=UTC&refresh={unique_param}"

# Input section
st.write("### 📝 Task Input")
with st.container():
    col1, col2 = st.columns((2, 1))
    with col1:
        query = st.text_input(
            "Describe your task to be chunked:",
            st.session_state["query"],
            key="query_input"
        )
    with col2:
        due_date = st.date_input(
            "Select the due date:",
            value=st.session_state["due_date"],
            key="due_date_input"
        )
chunkify = st.button("🔧 Chunkify Task")

# Chunkify logic
if chunkify:
    st.session_state["query"] = query
    st.session_state["due_date"] = due_date

    try:
        # Send request to the backend
        response = requests.post(API_URL, json={"query": query})
        if response.status_code == 200:
            # Parse response
            response_data = response.json()
            answer_text = response_data.get("answer", "")

            # Updated Parsing Logic
            subtask_pattern = r"(.+?)\s-\sDue Date:\s(\d{1,2}/\d{1,2})"
            subtasks_with_dates = re.findall(subtask_pattern, answer_text)

            # Separate subtasks and due dates
            st.session_state["subtasks"] = [desc.strip() for desc, _ in subtasks_with_dates]
            st.session_state["due_dates"] = [date.strip() for _, date in subtasks_with_dates]
        else:
            st.error("❌ Failed to retrieve subtasks from the API. Please try again.")

    except Exception as e:
        st.error(f"An error occurred: {e}")

# Display subtasks
if st.session_state["subtasks"] and st.session_state["due_dates"]:
    st.write("### 📋 Chunkified Subtasks")
    for i, (subtask, due_date) in enumerate(zip(st.session_state["subtasks"], st.session_state["due_dates"]), start=1):
        with st.container():
            st.markdown(
                f"""
                <div style="background-color: #f9f9f9; border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 10px;">
                    <h4 style="color: #333;">Subtask #{i}</h4>
                    <p style="color: #555; font-size: 16px;">{subtask}</p>
                    <strong>Due Date:</strong> {due_date}
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"Add Subtask #{i} to Calendar", key=f"add_subtask_{i}_button"):
                try:
                    # Parse the due date
                    parsed_date = datetime.datetime.strptime(due_date, "%m/%d").date()

                    # Set the year explicitly (2024)
                    parsed_date = parsed_date.replace(year=2024)

                    # Define start and end times
                    start_time = datetime.datetime.combine(parsed_date, datetime.time(9, 0))  # Start at 9 AM
                    end_time = start_time + datetime.timedelta(hours=1)  # Event lasts 1 hour

                    # Define the event
                    event = {
                        'summary': subtask,
                        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
                        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'},
                    }

                    # Insert event into Google Calendar
                    service.events().insert(calendarId="primary", body=event).execute()
                    st.success(f"✅ Subtask #{i} successfully added to your Google Calendar!")

                    # Set refresh flag
                    st.session_state["calendar_refresh"] = True

                except Exception as e:
                    st.error(f"❌ Failed to add Subtask #{i} to Google Calendar. Error: {e}")

# Refresh button
if st.button("🔄 Refresh Calendar"):
    st.session_state["calendar_refresh"] = True

# Display or refresh user's primary calendar
try:
    calendar_list = service.calendarList().list().execute()
    primary_calendar_id = None
    for calendar_entry in calendar_list.get('items', []):
        if calendar_entry.get('primary', False):
            primary_calendar_id = calendar_entry.get('id')
            break

    if primary_calendar_id:
        # Generate a unique iframe URL if the refresh flag is set
        calendar_src = generate_calendar_src(primary_calendar_id) if st.session_state.get("calendar_refresh") else f"https://calendar.google.com/calendar/embed?src={primary_calendar_id}&ctz=UTC"

        st.write("### 📅 Your Google Calendar")
        st.markdown(
            f"""
            <div style="margin: 5rem"></div>
            <div style="display: flex; align-items: center; justify-content: center"> 
                <iframe src="{calendar_src}" 
                        style="border-width:0" 
                        width="600" 
                        height="450" 
                        frameborder="0" 
                        scrolling="no"></iframe>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.session_state["calendar_refresh"] = False  # Reset the refresh flag
    else:
        st.warning("⚠️ Unable to retrieve your primary calendar. Please ensure you have access to it.")
except Exception as e:
    st.error(f"❌ An error occurred while retrieving your calendar: {e}")
