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

import streamlit as st
import requests
import re
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# Streamlit UI
st.title("The Ultimate AI-based Planning Tool")
st.write("Enter your task and let AI chunk it for you!")

# FastAPI endpoint URL
API_URL = "http://localhost:9000/api/perform_rag"

# Google Calendar Setup
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Authenticate and get the Google Calendar service."""
    creds = None
    # Token storage
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # Authenticate if no valid credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('calendar', 'v3', credentials=creds)

# Input for the query
query = st.text_input("Enter your query:")

if st.button("Chunkify!"):
    try:
        # Sending request to backend
        response = requests.post(API_URL, json={"query": query})

        if response.status_code == 200:
            # Parsing response
            response_data = response.json()

            # Display Query
            st.write("### Query")
            st.write(response_data['query'])

            # Extract subtasks from the response 'answer'
            answer_text = response_data.get('answer', "")
            before_subtasks = re.split(r"Subtask 1:", answer_text, maxsplit=1)[0].strip()
            subtask_pattern = r"Subtask \d+: (.*?)(?=Subtask \d+:|$)"
            subtasks = re.findall(subtask_pattern, answer_text, re.DOTALL)

            # Display Introduction
            st.markdown(
                f"""
                <div style="background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 10px; padding: 15px; margin-bottom: 20px;">
                    <h4 style="color: #333; font-size: 18px;">Introduction</h4>
                    <p style="color: #555; font-size: 16px;">{before_subtasks}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Display Subtasks and Add to Calendar
            st.markdown("<h4 style='color: #333;'>Subtasks</h4>", unsafe_allow_html=True)
            calendar_service = None

            for i, subtask in enumerate(subtasks, start=1):
                st.markdown(
                    f"""
                    <div style="background-color: #e8f4fc; border: 1px solid #b6d8e4; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
                        <p style="color: #084c61; font-size: 16px;"><strong>Subtask {i}:</strong> {subtask.strip()}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Button to add subtask to Google Calendar
                if st.button(f"Add Subtask {i} to Google Calendar"):
                    if not calendar_service:
                        calendar_service = get_calendar_service()

                    event = {
                        'summary': f"Subtask {i}: {subtask.strip()}",
                        'description': subtask.strip(),
                        'start': {
                            'dateTime': (datetime.datetime.now() + datetime.timedelta(days=i)).isoformat(),
                            'timeZone': 'UTC',
                        },
                        'end': {
                            'dateTime': (datetime.datetime.now() + datetime.timedelta(days=i, hours=1)).isoformat(),
                            'timeZone': 'UTC',
                        },
                    }
                    calendar_service.events().insert(calendarId='primary', body=event).execute()
                    st.success(f"Subtask {i} added to Google Calendar!")

        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.write("Exception details:", e)
