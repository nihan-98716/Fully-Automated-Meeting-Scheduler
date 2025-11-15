import os
import json
import base64
import logging
from datetime import timedelta

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import googleapiclient.errors

from utils import (
    looks_like_meeting,
    extract_meeting_link,
    parse_datetime_from_text,
    parse_ics_attachment,
    iso_local,
)
from db import mark_processed, is_processed  

TIMEZONE = os.environ.get("TIMEZONE", "Asia/Kolkata")
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")

def get_google_creds():
    if not os.path.exists("token.json"):
        raise RuntimeError("token.json not found. Run google_auth_setup.py first.")
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return creds

def add_event_to_calendar(creds, meeting):
    try:
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)
        event = {
            "summary": meeting.get("summary", "Meeting"),
            "description": (meeting.get("description", "") or "")
            + (f"\nMeeting Link: {meeting.get('link')}" if meeting.get("link") else ""),
            "start": {"dateTime": iso_local(meeting["start"]), "timeZone": TIMEZONE},
            "end": {"dateTime": iso_local(meeting["end"]), "timeZone": TIMEZONE},
        }
        created = service.events().insert(calendarId="primary", body=event).execute()
        logging.info(
            f"✅ Added to Calendar: {created.get('summary')} at {created['start']['dateTime']}"
        )
        return True
    except googleapiclient.errors.HttpError as e:
        logging.error(f"❌ Calendar insert failed: {e}")
        return False

def fetch_gmail_messages(service):
    logging.info("📬 Fetching recent Gmail messages...")
    query = 'meeting OR invite OR schedule OR "Google Meet" OR zoom OR call'
    try:
        res = service.users().messages().list(
            userId="me", q=query, maxResults=50
        ).execute()
        messages = res.get("messages", [])
        logging.info(f"✅ Gmail API responded. Found {len(messages)} candidate messages.")
        return messages
    except googleapiclient.errors.HttpError as e:
        logging.error(f"❌ Gmail API error: {e}")
        return []

def run_sync_once():
    creds = get_google_creds()
    gmail = build("gmail", "v1", credentials=creds, cache_discovery=False)
    messages = fetch_gmail_messages(gmail)
    added = 0

    for msg in messages:
        mid = msg["id"]
        if is_processed(mid):
            continue

        try:
            m = gmail.users().messages().get(
                userId="me", id=mid, format="full"
            ).execute()

            headers = m.get("payload", {}).get("headers", [])
            subject = next(
                (h["value"] for h in headers if h["name"].lower() == "subject"),
                "",
            )

            body = ""
            payload = m.get("payload", {})
            parts = payload.get("parts", []) or []

            if payload.get("body", {}).get("data"):
                body += base64.urlsafe_b64decode(
                    payload["body"]["data"]
                ).decode("utf-8", errors="ignore")

            for part in parts:
                mime = part.get("mimeType", "")
                if mime in ["text/plain", "text/html"] and part.get("body", {}).get(
                    "data"
                ):
                    body += base64.urlsafe_b64decode(
                        part["body"]["data"]
                    ).decode("utf-8", errors="ignore")

            text = (subject or "") + "\n" + (body or "")

            if not looks_like_meeting(text):
                mark_processed(mid)
                continue

            meeting = None

            for part in parts:
                if part.get("filename", "").endswith(".ics") and part.get("body", {}).get(
                    "attachmentId"
                ):
                    att_id = part["body"]["attachmentId"]
                    att = gmail.users().messages().attachments().get(
                        userId="me", messageId=mid, id=att_id
                    ).execute()
                    val = att.get("data")
                    meeting = parse_ics_attachment(val)
                    break

            if not meeting:
                dt = parse_datetime_from_text(text)
                if not dt:
                    logging.info(
                        f"⏩ Skipping '{subject}' — no valid date/time found in email."
                    )
                    mark_processed(mid)
                    continue
                meeting = {
                    "summary": subject or "Meeting",
                    "start": dt,
                    "end": dt + timedelta(hours=1),
                    "description": body,
                    "link": extract_meeting_link(text),
                }

            if add_event_to_calendar(creds, meeting):
                added += 1

            mark_processed(mid)

        except Exception as e:
            logging.error(f"⚠️ Error processing message {mid}: {e}")
            mark_processed(mid)
            continue

    logging.info(f"✨ Sync complete. {added} meetings added to calendar.")
    return added

if __name__ == "__main__":
    print("🚀 Running Gmail → Calendar sync manually...")
    run_sync_once()
