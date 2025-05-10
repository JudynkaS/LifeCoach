import os
from django.conf import settings
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from accounts.models import Profile

GOOGLE_CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, 'config', 'credentials.json')
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/calendar.events']


def create_coach_calendar_event(coach_profile, summary, description, start_dt, end_dt, timezone_str='UTC'):
    """
    Vytvoří událost v Google kalendáři kouče.
    coach_profile: Profile instance kouče (musí mít google_refresh_token)
    summary: Název události
    description: Popis události
    start_dt, end_dt: datetime (aware)
    timezone_str: např. 'Europe/Prague'
    """
    if not coach_profile.google_refresh_token:
        raise Exception('Coach does not have a Google refresh token.')

    # Načti client_id a client_secret z credentials.json
    import json
    with open(GOOGLE_CLIENT_SECRETS_FILE, 'r') as f:
        secrets = json.load(f)
        client_id = secrets['web']['client_id']
        client_secret = secrets['web']['client_secret']

    # Vytvoř credentials objekt
    creds = Credentials(
        None,
        refresh_token=coach_profile.google_refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=client_id,
        client_secret=client_secret,
        scopes=GOOGLE_SCOPES
    )

    # Vytvoř service objekt
    service = build('calendar', 'v3', credentials=creds)

    # Vytvoř událost
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': timezone_str,
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': timezone_str,
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},  # Email 24 hodin předem
                {'method': 'popup', 'minutes': 30},       # Popup 30 minut předem
            ],
        },
        'guestsCanModify': False,
        'guestsCanSeeOtherGuests': False,
    }

    # Vlož událost do kalendáře
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event

def delete_coach_calendar_event(coach_profile, event_id):
    """
    Smaže událost z Google kalendáře kouče.
    coach_profile: Profile instance kouče (musí mít google_refresh_token)
    event_id: ID události v Google kalendáři
    """
    if not coach_profile.google_refresh_token:
        raise Exception('Coach does not have a Google refresh token.')

    # Načti client_id a client_secret z credentials.json
    import json
    with open(GOOGLE_CLIENT_SECRETS_FILE, 'r') as f:
        secrets = json.load(f)
        client_id = secrets['web']['client_id']
        client_secret = secrets['web']['client_secret']

    # Vytvoř credentials objekt
    creds = Credentials(
        None,
        refresh_token=coach_profile.google_refresh_token,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=client_id,
        client_secret=client_secret,
        scopes=GOOGLE_SCOPES
    )

    # Vytvoř service objekt
    service = build('calendar', 'v3', credentials=creds)

    # Smaž událost
    service.events().delete(calendarId='primary', eventId=event_id).execute() 