import streamlit as st
import requests
import re
import datetime
# from googleapiclient.discovery import build
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
import os
import pickle
from streamlit_calendar import calendar

# Streamlit UI
st.title("ChunkIt")

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

#  Add columns for input
col = st.columns((9, 3, 3))

with col[0]:
    # Input for the query
    query = st.text_input("Enter your task and let AI chunk it for you!")
with col[1]:
    # Due Date input
    d = st.date_input("Due Date", value=None)
with col[2]:
    st.markdown(f"""<div style='margin: 27px;'></div>""", unsafe_allow_html=True)
    chunkify = st.button("Chunkify!")

# Chunkify
if chunkify:
    try:
        # Sending request to backend
        # response = requests.post(API_URL, json={"query": query})

        #     if response.status_code == 200:
        #         # Parsing response
        #         response_data = response.json()

        #         # Display Query
        #         st.write("### Query")
        #         st.write(response_data['query'])

        # Extract subtasks from the response 'answer'
        answer_text = "ANSWER"
        # answer_text = response_data.get('answer', "")
        before_subtasks = "SUMMARY TEXT"
        # before_subtasks = re.split(r"Subtask 1:", answer_text, maxsplit=1)[0].strip()
        # subtask_pattern = r"Subtask \d+: (.*?)(?=Subtask \d+:|$)"
        subtasks = ["Title of Subtask #1", "Title of Subtask #2", "Title of Subtask #3"]
        # subtasks = re.findall(subtask_pattern, answer_text, re.DOTALL)

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

        for i, subtask in enumerate(subtasks, start=1):
            col = st.columns((9, 5))
            with col[0]:
                # Each Subtask 
                date = d.strftime("%m") + "/" + d.strftime("%d")
                checkbox = st.checkbox(f"**Subtask #{i}: {date}**") 
            with col[1]:
                # Button to add subtask to Google Calendar
                if st.button(f"Add Subtask #{i} to Calendar"):
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
                        st.success(f"Subtask {i} added to calendar!")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
            
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

# Add calendar
st.markdown (
    f"""
    <div style="margin: 5rem"></div>
    <div style="display: flex; align-items: center; justify-content: center"> 
        <iframe src="https://calendar.google.com/calendar/embed?height=450&wkst=1&ctz=America%2FNew_York&bgcolor=%23ffffff&showPrint=0&showTitle=0&showTz=0&src=Y18xYmJmOWM2YzM2YTFhZDBlYTRhZTIxM2U1YWYwMWY3YjJhMmIzYzU0ZWJjMWRjYTcwZGNkMDQ2NDM1NDc2ZjcxQGdyb3VwLmNhbGVuZGFyLmdvb2dsZS5jb20&color=%23009688" style="border-width:0" width="600" height="450" frameborder="0" scrolling="no"></iframe>
    </div>
    """,
    unsafe_allow_html=True,
)  

