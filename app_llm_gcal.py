# import streamlit as st
# import requests
# import re

# # Streamlit UI
# st.title("The Ultimate AI-based Planning Tool")
# st.write("Enter your task and let AI chunk it for you!")

# # FastAPI endpoint URL
# API_URL = "http://localhost:9000/api/perform_rag"

# # Input for the query
# query = st.text_input("Enter your query:")

# if st.button("Chunkify!"):
#     try:
#         # Sending request to backend
#         response = requests.post(API_URL, json={"query": query})

#         if response.status_code == 200:
#             # Parsing response
#             response_data = response.json()

#             # Display Query
#             st.write("### Query")
#             st.write(response_data['query'])

#             # Extract subtasks from the response 'answer'
#             answer_text = response_data.get('answer', "")
#             before_subtasks = re.split(r"Subtask 1:", answer_text, maxsplit=1)[0].strip()
#             subtask_pattern = r"Subtask \d+: (.*?)(?=Subtask \d+:|$)"
#             subtasks = re.findall(subtask_pattern, answer_text, re.DOTALL)

#             # st.write(before_subtasks)
#             # # Display Subtasks as bullet points
#             # st.write("### Subtasks")
#             # for i, subtask in enumerate(subtasks, start=1):
#             #     st.markdown(f"- **Subtask {i}:** {subtask.strip()}")

#             # Styled box for the introduction
#             st.markdown(
#                 f"""
#                 <div style="background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 20px;">
#                     <h4 style="color: #333; font-size: 18px;">Introduction</h4>
#                     <p style="color: #555; font-size: 16px;">{before_subtasks}</p>
#                 </div>
#                 """,
#                 unsafe_allow_html=True,
#             )

#             # Styled subtasks
#             st.markdown("<h4 style='color: #333;'>Subtasks</h4>", unsafe_allow_html=True)
#             for i, subtask in enumerate(subtasks, start=1):
#                 st.markdown(
#                     f"""
#                     <div style="background-color: #e8f4fc; border: 1px solid #b6d8e4; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
#                         <p style="color: #084c61; font-size: 16px;"><strong>Subtask {i}:</strong> {subtask.strip()}</p>
#                     </div>
#                     """,
#                     unsafe_allow_html=True,
#                 )

#         else:
#             st.error(f"Error: {response.status_code} - {response.text}")
#     except Exception as e:
#         st.error(f"An error occurred: {e}")
#         st.write("Exception details:", e)

# app.py
# import streamlit as st
# import requests
# import re
# import datetime
# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# import os
# import pickle

# # Streamlit UI
# st.title("The Ultimate AI-based Planning Tool")
# st.write("Enter your task and let AI chunk it for you!")

# # FastAPI endpoint URL
# API_URL = "http://localhost:9000/api/perform_rag"

# # Google Calendar Setup
# SCOPES = ['https://www.googleapis.com/auth/calendar']

# def get_calendar_service():
#     """Authenticate and get the Google Calendar service."""
#     creds = None
#     # Token storage
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = pickle.load(token)
#     # Authenticate if no valid credentials
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'client_secrets.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for future use
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)
#     return build('calendar', 'v3', credentials=creds)

# # Input for the query
# query = st.text_input("Enter your query:")

# if st.button("Chunkify!"):
#     try:
#         # Sending request to backend
#         response = requests.post(API_URL, json={"query": query})

#         if response.status_code == 200:
#             # Parsing response
#             response_data = response.json()

#             # Display Query
#             st.write("### Query")
#             st.write(response_data['query'])

#             # Extract subtasks from the response 'answer'
#             answer_text = response_data.get('answer', "")
#             before_subtasks = re.split(r"Subtask 1:", answer_text, maxsplit=1)[0].strip()
#             subtask_pattern = r"Subtask \d+: (.*?)(?=Subtask \d+:|$)"
#             subtasks = re.findall(subtask_pattern, answer_text, re.DOTALL)

#             # Display Introduction
#             st.markdown(
#                 f"""
#                 <div style="background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 20px;">
#                     <h4 style="color: #333; font-size: 18px;">Introduction</h4>
#                     <p style="color: #555; font-size: 16px;">{before_subtasks}</p>
#                 </div>
#                 """,
#                 unsafe_allow_html=True,
#             )

#             # Display Subtasks and Add to Calendar
#             st.markdown("<h4 style='color: #333;'>Subtasks</h4>", unsafe_allow_html=True)
#             calendar_service = None

#             for i, subtask in enumerate(subtasks, start=1):
#                 st.markdown(
#                     f"""
#                     <div style="background-color: #e8f4fc; border: 1px solid #b6d8e4; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
#                         <p style="color: #084c61; font-size: 16px;"><strong>Subtask {i}:</strong> {subtask.strip()}</p>
#                     </div>
#                     """,
#                     unsafe_allow_html=True,
#                 )

#                 # Button to add subtask to Google Calendar
#                 if st.button(f"Add Subtask {i} to Google Calendar"):
#                     if not calendar_service:
#                         calendar_service = get_calendar_service()

#                     event = {
#                         'summary': f"Subtask {i}: {subtask.strip()}",
#                         'description': subtask.strip(),
#                         'start': {
#                             'dateTime': (datetime.datetime.now() + datetime.timedelta(days=i)).isoformat(),
#                             'timeZone': 'UTC',
#                         },
#                         'end': {
#                             'dateTime': (datetime.datetime.now() + datetime.timedelta(days=i, hours=1)).isoformat(),
#                             'timeZone': 'UTC',
#                         },
#                     }
#                     calendar_service.events().insert(calendarId='primary', body=event).execute()
#                     st.success(f"Subtask {i} added to Google Calendar!")

#         else:
#             st.error(f"Error: {response.status_code} - {response.text}")
#     except Exception as e:
#         st.error(f"An error occurred: {e}")
#         st.write("Exception details:", e)

# app-frontend.py

# import streamlit as st
# import requests
# import re
# import datetime
# # from googleapiclient.discovery import build
# # from google_auth_oauthlib.flow import InstalledAppFlow
# # from google.auth.transport.requests import Request
# import os
# import pickle

# # Streamlit UI
# st.title("ChunkIt")

# # FastAPI endpoint URL
# API_URL = "http://localhost:9000/api/perform_rag"

# # Google Calendar Setup
# SCOPES = ['https://www.googleapis.com/auth/calendar']

# def get_calendar_service():
#     """Authenticate and get the Google Calendar service."""
#     creds = None
#     # Token storage
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = pickle.load(token)
#     # Authenticate if no valid credentials
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'client_secrets.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for future use
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)
#     return build('calendar', 'v3', credentials=creds)   

# #  Add columns for input
# col = st.columns((9, 3, 3))

# with col[0]:
#     # Input for the query
#     query = st.text_input("Enter your task and let AI chunk it for you!")
# with col[1]:
#     # Due Date input
#     d = st.date_input("Due Date", value=None)
# with col[2]:
#     st.markdown(f"""<div style='margin: 27px;'></div>""", unsafe_allow_html=True)
#     chunkify = st.button("Chunkify!")

# # Chunkify
# if chunkify:
#     try:
#         # Sending request to backend
#         # response = requests.post(API_URL, json={"query": query})

#         #     if response.status_code == 200:
#         #         # Parsing response
#         #         response_data = response.json()

#         #         # Display Query
#         #         st.write("### Query")
#         #         st.write(response_data['query'])

#         # Extract subtasks from the response 'answer'
#         answer_text = "ANSWER"
#         # answer_text = response_data.get('answer', "")
#         before_subtasks = "SUMMARY TEXT"
#         # before_subtasks = re.split(r"Subtask 1:", answer_text, maxsplit=1)[0].strip()
#         # subtask_pattern = r"Subtask \d+: (.*?)(?=Subtask \d+:|$)"
#         subtasks = ["Title of Subtask #1", "Title of Subtask #2", "Title of Subtask #3"]
#         # subtasks = re.findall(subtask_pattern, answer_text, re.DOTALL)

#         # Display query, due date, subtasks, and button to add to calendar
#         col = st.columns((9, 3))
#         with col[0]:
#             # query
#             st.markdown(f"""<h4 style='color: #333;'>{query}</h4>""", unsafe_allow_html=True)
#             calendar_service = None
#         with col[1]:
#             # Due Date 
#             st.markdown(f"""<div style='margin: 5px'></div>""", unsafe_allow_html=True)
#             st.write("Due Date:", d.strftime("%m"), "/", d.strftime("%d"))

#         for i, subtask in enumerate(subtasks, start=1):
#             col = st.columns((9, 5))
#             with col[0]:
#                 # Each Subtask 
#                 date = d.strftime("%m") + "/" + d.strftime("%d")
#                 checkbox = st.checkbox(f"**Subtask #{i}: {date}**") 
#             with col[1]:
#                 # Button to add subtask to Google Calendar
#                 if st.button(f"Add Subtask #{i} to Calendar"):
#                     if not calendar_service:
#                         calendar_service = get_calendar_service()

#                         event = {
#                                 'summary': f"Subtask {i}: {subtask.strip()}",
#                                 'description': subtask.strip(),
#                                 'start': {
#                                     'dateTime': (datetime.datetime.now() + datetime.timedelta(days=i)).isoformat(),
#                                     'timeZone': 'UTC',
#                                 },
#                                 'end': {
#                                     'dateTime': (datetime.datetime.now() + datetime.timedelta(days=i, hours=1)).isoformat(),
#                                     'timeZone': 'UTC',
#                                 },
#                         }
#                         calendar_service.events().insert(calendarId='primary', body=event).execute()
#                         st.success(f"Subtask {i} added to calendar!")
#                     else:
#                         st.error(f"Error: {response.status_code} - {response.text}")
            
#             # Text of Subtask
#             st.markdown(f"""<div style='margin-left: 25px; margin-bottom: 25px'>{subtask}</div>""", unsafe_allow_html=True)
#             # st.markdown(
#                 #     f"""
#                 #     <div style="background-color: #e8f4fc; border: 1px solid #b6d8e4; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
#                 #     <p style="color: #084c61; font-size: 16px;"><strong>Subtask {i}:</strong> {subtask.strip()}</p>
#                 #     </div>
#                 #     """,
#                 #     unsafe_allow_html=True,
#             # )
                
#     except Exception as e:
#         st.error(f"An error occurred: {e}")
#         st.write("Exception details:", e)

# # Add calendar
# st.markdown (
#     f"""
#     <div style="margin: 5rem"></div>
#     <div style="display: flex; align-items: center; justify-content: center"> 
#         <iframe src="https://calendar.google.com/calendar/embed?height=450&wkst=1&ctz=America%2FNew_York&bgcolor=%23ffffff&showPrint=0&showTitle=0&showTz=0&src=Y18xYmJmOWM2YzM2YTFhZDBlYTRhZTIxM2U1YWYwMWY3YjJhMmIzYzU0ZWJjMWRjYTcwZGNkMDQ2NDM1NDc2ZjcxQGdyb3VwLmNhbGVuZGFyLmdvb2dsZS5jb20&color=%23009688" style="border-width:0" width="600" height="450" frameborder="0" scrolling="no"></iframe>
#     </div>
#     """,
#     unsafe_allow_html=True,
# )  

# combo

import streamlit as st
import requests
import re
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from google.oauth2.credentials import Credentials

# Streamlit UI
st.title("ChunkIt")

# FastAPI endpoint URL
API_URL = "http://localhost:9000/api/perform_rag"

# Google Calendar Setup
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Token storage directory
TOKEN_DIR = "token_files"
TOKEN_FILE = "token_calendar_v3.json"

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
        # with open(os.path.join(working_dir, token_dir, token_file), 'rb') as token:
        #   cred = pickle.load(token)

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

CLIENT_SECRET_FILE = 'client_secret.json'
API_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar']

service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

# def get_calendar_service():
#     """Authenticate and get the Google Calendar service."""
#     creds = None
#     # Token storage
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = pickle.load(token)
#     # Authenticate if no valid credentials
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'client_secrets.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for future use
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)
#     return build('calendar', 'v3', credentials=creds)   

#  Add columns for input
# col = st.columns((9, 3, 3))

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

with col[0]:
    # Input for the query
    query = st.text_input("Enter your task and let AI chunk it for you!",
    st.session_state["query"], 
    key="query_input"
    )
with col[1]:
    # Due Date input
    d = st.date_input("Due Date",
    value=st.session_state["due_date"], 
    key="due_date_input"
    )
with col[2]:
    st.markdown(f"""<div style='margin: 27px;'></div>""", unsafe_allow_html=True)
    chunkify = st.button("Chunkify!", key="chunkify_button")

# Chunkify
if chunkify:
    # Save inputs to session state
    st.session_state["query"] = query
    st.session_state["due_date"] = d
    try:
        # Sending request to backend
        response = requests.post(API_URL, json={"query": query})

        if response.status_code == 200:
            # Parsing response
            response_data = response.json()

                # Display Query
                # st.write("### Query")
                # st.write(response_data['query'])

        # Extract subtasks from the response 'answer'
        # answer_text = "ANSWER"
        answer_text = response_data.get('answer', "")
        # before_subtasks = "SUMMARY TEXT"
        before_subtasks = re.split(r"Subtask 1:", answer_text, maxsplit=1)[0].strip()
        subtask_pattern = r"Subtask \d+: (.*?)(?=Subtask \d+:|$)"
        # subtasks = ["Title of Subtask #1", "Title of Subtask #2", "Title of Subtask #3"]
        subtasks = re.findall(subtask_pattern, answer_text, re.DOTALL)
        st.session_state["subtasks"] = subtasks

        # Regex pattern to extract the date after "Due Date:"
        date_pattern = r"- Due Date: (.+)"

        # Extract due dates using list comprehension
        due_dates = [re.search(date_pattern, subtask).group(1).strip() for subtask in subtasks if re.search(date_pattern, subtask)]


        # Display query, due date, subtasks, and button to add to calendar
        col = st.columns((9, 3))
        with col[0]:
            # query
            st.markdown(f"""<h4 style='color: #333;'>{query}</h4>""", unsafe_allow_html=True)
            calendar_service = None
        with col[1]:
            # Due Date 
            st.markdown(f"""<div style='margin: 5px'></div>""", unsafe_allow_html=True)
            st.write("Due Date:", d.strftime("%m"), "/", d.strftime("%d"))

        if st.session_state["subtasks"]:
            # for i, subtask in enumerate(subtasks, start=1):
            for i, (subtask, due_date) in enumerate(zip(st.session_state["subtasks"], due_dates), start=1):
                col = st.columns((9, 5))
                with col[0]:
                    # Each Subtask 
                    # date = d.strftime("%m") + "/" + d.strftime("%d")
                    # date_pattern = r"Due Date: (.+)$"
                    # match = re.search(date_pattern, subtask)
                    # extracted_date = match.group(1).strip()
                    checkbox = st.checkbox(f"**Subtask #{i}: {due_date}**") 
                with col[1]:
                    # Button to add subtask to Google Calendar
                    if st.button(f"Add Subtask #{i} to Calendar", key=f"add_subtask_{i}_button"):
                        try:
                            # Calculate start and end times
                            # parsed_date = datetime.datetime.strptime(due_date, "%m/%d").date().replace(year=datetime.datetime.now().year)
                            # st.session_state["due_date"] = parsed_date
                            # event_date = datetime.datetime.combine(st.session_state["due_date"], datetime.datetime.min.time())
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

                        # if not calendar_service:
                        #     calendar_service = get_calendar_service()

                        #     event = {
                        #             'summary': f"Subtask {i}: {subtask.strip()}",
                        #             'description': subtask.strip(),
                        #             'start': {
                        #                 'dateTime': (datetime.datetime.now() + datetime.timedelta(days=i)).isoformat(),
                        #                 'timeZone': 'UTC',
                        #             },
                        #             'end': {
                        #                 'dateTime': (datetime.datetime.now() + datetime.timedelta(days=i, hours=1)).isoformat(),
                        #                 'timeZone': 'UTC',
                        #             },
                        #     }
                        #     calendar_service.events().insert(calendarId='primary', body=event).execute()
                        #     st.success(f"Subtask {i} added to calendar!")
                        # else:
                        #     st.error(f"Error: {response.status_code} - {response.text}")

                # Text of Subtask
                st.markdown(f"""<div style='margin-left: 25px; margin-bottom: 25px'>{subtask}</div>""", unsafe_allow_html=True)
                # st.markdown(
                    #     f"""
                    #     <div style="background-color: #e8f4fc; border: 1px solid #b6d8e4; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
                    #     <p style="color: #084c61; font-size: 16px;"><strong>Subtask {i}:</strong> {subtask.strip()}</p>
                    #     </div>
                    #     """,
                    #     unsafe_allow_html=True,
                # )
                
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.write("Exception details:", e)

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
