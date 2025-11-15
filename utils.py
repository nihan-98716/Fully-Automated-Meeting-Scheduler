import re
from datetime import timedelta
import dateparser
from datetime import datetime
from icalendar import Calendar
import base64
from dateutil import tz

MEETING_KEYWORDS = [
    'meeting', 'invite', 'schedule', 'call', 'zoom', 'google meet', 'webex', 'teams'
]

MEETING_LINKS = [
    r'https?://[\w./?=&%-]*zoom.us[\w./?=&%-]*',
    r'https?://meet\.google\.com[\w./?=&%-]*',
    r'https?://teams\.microsoft\.com[\w./?=&%-]*',
    r'https?://[\w./?=&%-]*webex.com[\w./?=&%-]*'
]

def looks_like_meeting(text):
    text = (text or "").lower()
    if any(k in text for k in MEETING_KEYWORDS):
        return True
    if re.search('|'.join(MEETING_LINKS), text):
        return True
    return False

def extract_meeting_link(text):
    match = re.search(r'(https?://[^\s)]+)', text)
    return match.group(1) if match else None

def parse_datetime_from_text(text):
    """
    Improved date parser that handles natural language like:
    'tomorrow at 6pm', 'next Tuesday 4:30 PM', '13 Nov 2025 10 AM'
    Returns a timezone-aware datetime or None.
    """
    if not text:
        return None

    text = text.lower().replace('\n', ' ').replace(',', ' ')
    
    patterns = [
        r'\b(?:tomorrow|today|tonight|next\s+\w+)\b.*?(?:\d{1,2}\s?(?:am|pm))?',
        r'\b\d{1,2}\s*(?:am|pm)\b',
        r'\b\d{1,2}\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s*\d{2,4}?\b',
        r'\b(?:on\s+)?\d{1,2}/\d{1,2}(?:/\d{2,4})?\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            candidate = match.group(0)
            dt = dateparser.parse(candidate, settings={
                'PREFER_DATES_FROM': 'future',
                'PREFER_DAY_OF_MONTH': 'first',
                'RELATIVE_BASE': datetime.now(),
                'RETURN_AS_TIMEZONE_AWARE': True,
                'TIMEZONE': 'Asia/Kolkata'
            })
            if dt:
                return dt

    dt = dateparser.parse(text, settings={
        'PREFER_DATES_FROM': 'future',
        'RETURN_AS_TIMEZONE_AWARE': True,
        'TIMEZONE': 'Asia/Kolkata'
    })
    return dt

def parse_ics_attachment(b64data):
    try:
        raw = base64.b64decode(b64data)
        cal = Calendar.from_ical(raw)
        for c in cal.walk():
            if c.name == "VEVENT":
                return {
                    'summary': str(c.get('summary')),
                    'start': c.get('dtstart').dt,
                    'end': c.get('dtend').dt,
                    'description': str(c.get('description'))
                }
    except Exception:
        return None
    return None

def iso_local(dt):
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz.tzlocal())
    return dt.isoformat()
