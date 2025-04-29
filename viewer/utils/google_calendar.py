import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

# Scopes for Google Calendar access
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_calendar_service():
    """
    Get Google Calendar service instance.
    Uses client_secret.json from the config directory.
    """
    # Get the path to client_secret.json
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config')
    client_secrets_file = os.path.join(config_dir, 'client_secret.json')
    
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('calendar', 'v3', credentials=creds)
    return service

def create_event(summary, location, description, start_time, end_time, timezone='Europe/Prague'):
    """
    Create a calendar event.
    
    Args:
        summary (str): Event title
        location (str): Event location
        description (str): Event description
        start_time (datetime): Event start time
        end_time (datetime): Event end time
        timezone (str): Timezone for the event (default: Europe/Prague)
    
    Returns:
        dict: Created event details
    """
    service = get_calendar_service()
    
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': timezone,
        },
    }
    
    event = service.events().insert(calendarId='primary', body=event).execute()
    return event

def create_psychology_session(client_email, start_time, duration_minutes=60):
    """
    Create a psychology session event.
    
    Args:
        client_email (str): Client's email address
        start_time (datetime): Session start time
        duration_minutes (int): Session duration in minutes (default: 60)
    
    Returns:
        dict: Created event details
    """
    from datetime import timedelta
    
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    event = create_event(
        summary='Psychologické sezení',
        location='Online (Google Meet)',
        description=f'Sezení s klientem: {client_email}',
        start_time=start_time,
        end_time=end_time
    )
    
    return event 