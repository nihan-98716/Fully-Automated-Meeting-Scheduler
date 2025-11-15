import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

def main():
    if not os.path.exists("credentials.json"):
        raise FileNotFoundError("credentials.json not found in current folder")

    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json", SCOPES
    )

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )

    print("Open this URL in browser to authenticate:\n")
    print(auth_url)

    creds = flow.run_local_server(
        port=8080,
        prompt='consent',
        authorization_prompt_message='',
        success_message='Authentication complete! You may close this window.',
        open_browser=True
    )

    with open("token.json", "w") as token_file:
        token_file.write(creds.to_json())

    print("\n✅ Authentication complete. token.json saved.")

if __name__ == "__main__":
    main()
