// Set Google API credentials
const CLIENT_ID = '224206916412-b4itu1s9r8tvvr33qcrjv43ej954e9ia.apps.googleusercontent.com';
const API_KEY = 'AIzaSyBw69o6jMDInBa07SFQ2tGxAUstocC3XTc';
const DISCOVERY_DOC = 'https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest';
const SCOPES = 'https://www.googleapis.com/auth/calendar';

// Initialize variables
let tokenClient;
let gapiInited = false;
let gisInited = false;

// Hide buttons until ready
document.getElementById('authorize_button').style.visibility = 'hidden';
document.getElementById('signout_button').style.visibility = 'hidden';

// Load Google API
function gapiLoaded() {
  gapi.load('client', initializeGapiClient);
}

async function initializeGapiClient() {
  await gapi.client.init({
    apiKey: API_KEY,
    discoveryDocs: [DISCOVERY_DOC],
  });
  gapiInited = true;
  maybeEnableButtons();
}

// Load Google Identity Services
function gisLoaded() {
  tokenClient = google.accounts.oauth2.initTokenClient({
    client_id: CLIENT_ID,
    scope: SCOPES,
    callback: '', // Will be set later
  });
  gisInited = true;
  maybeEnableButtons();
}

// Enable buttons if API and GIS are loaded
function maybeEnableButtons() {
  if (gapiInited && gisInited) {
    document.getElementById('authorize_button').style.visibility = 'visible';
  }
}

// Handle authorization
function handleAuthClick() {
    tokenClient.callback = async (resp) => {
      if (resp.error !== undefined) {
        throw (resp);
      }
      document.getElementById('signout_button').style.visibility = 'visible';
      document.getElementById('authorize_button').innerText = 'Refresh';
      await listUpcomingEvents();
    };

    if (gapi.client.getToken() === null) {
      tokenClient.requestAccessToken({ prompt: 'consent' });
    } else {
      tokenClient.requestAccessToken({ prompt: '' });
    }
  }

// Handle sign-out
function handleSignoutClick() {
    const token = gapi.client.getToken();
    if (token !== null) {
      google.accounts.oauth2.revoke(token.access_token);
      gapi.client.setToken('');
  
      // Restore placeholder and hide content
      document.getElementById('placeholder_calendar').style.display = 'block';
      document.getElementById('content').style.display = 'none';
      document.getElementById('content').innerHTML = '';
  
      // Update buttons
      document.getElementById('authorize_button').style.visibility = 'visible';
      document.getElementById('signout_button').style.display = 'none';
    }
  }
  

// List upcoming events
async function listUpcomingEvents() {
    const placeholder = document.getElementById('placeholder_calendar');
    const content = document.getElementById('content');
  
    let response;
    try {
      const request = {
        'calendarId': 'primary',
        'timeMin': (new Date()).toISOString(),
        'showDeleted': false,
        'singleEvents': true,
        'maxResults': 10,
        'orderBy': 'startTime',
      };
      response = await gapi.client.calendar.events.list(request);
  
      // Hide placeholder and show content
      placeholder.style.display = 'none';
      content.style.display = 'block';
    } catch (err) {
      content.innerText = `Error fetching events: ${err.message}`;
      return;
    }
  
    const events = response.result.items;
    content.innerHTML = ''; // Clear previous events
    if (!events || events.length === 0) {
      content.innerHTML = '<p>No events found in your calendar.</p>';
      return;
    }
  
    // Display events
    events.forEach(event => {
      const eventElement = document.createElement('div');
      eventElement.className = 'event-item';
      eventElement.innerHTML = `
        <strong>${event.summary || 'No Title'}</strong><br>
        ${event.start.dateTime || event.start.date}
      `;
      content.appendChild(eventElement);
    });
  }
  

// Add a new calendar event
async function addCalendarEvent(task, dueDate) {
  const event = {
    summary: task,
    start: {
      dateTime: dueDate.toISOString(),
      timeZone: 'America/New_York',
    },
    end: {
      dateTime: new Date(dueDate.getTime() + 60 * 60 * 1000).toISOString(), // +1 hour
      timeZone: 'America/New_York',
    },
  };

  try {
    const response = await gapi.client.calendar.events.insert({
      calendarId: 'primary',
      resource: event,
    });
    alert(`Event created: ${response.result.htmlLink}`);
    listUpcomingEvents(); // Refresh events
  } catch (err) {
    alert('Error creating event: ' + err.message);
  }
}

// Handle "Chunkify" button click
document.getElementById('chunkify').addEventListener('click', () => {
  const taskInput = document.querySelector('input[placeholder="Add a task..."]');
  const task = taskInput.value.trim();

  // Prompt for due date (replace this with a date picker in the future)
  const dueDateString = prompt('Enter due date (YYYY-MM-DD):');
  const dueDate = new Date(dueDateString);

  if (task && !isNaN(dueDate)) {
    addCalendarEvent(task, dueDate);
    taskInput.value = ''; // Clear input
  } else {
    alert('Please enter a valid task and due date.');
  }
});
