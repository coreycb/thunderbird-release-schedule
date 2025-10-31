# Google Calendar Setup Guide

This guide explains how to set up Google Calendar API access for the `--write-calendar` feature.

## Prerequisites

- Python 3.10 or later
- A Google account with access to the target calendar

## Installation Steps

### 1. Install the Package with Calendar Extras

**Using pip (editable install for development):**

```bash
pip install -e .[calendar]
```

**Using pipx (isolated install):**

```bash
pipx install .
pipx inject thunderbird-release-schedule google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

**Or install dependencies manually:**

```bash
pip install -r requirements.txt
```

This installs:
- `google-api-python-client` - Google Calendar API client
- `google-auth-httplib2` - HTTP library for auth
- `google-auth-oauthlib` - OAuth 2.0 library

### 2. Set Up Google Cloud Project

1. **Go to Google Cloud Console:**
   - Navigate to https://console.cloud.google.com/

2. **Create or Select a Project:**
   - Click the project dropdown at the top
   - Click "New Project" or select an existing one
   - Give it a name like "Thunderbird Schedule"

3. **Enable Google Calendar API:**
   - In the left sidebar, go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click on it and press "Enable"

4. **Create OAuth 2.0 Credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "+ CREATE CREDENTIALS" > "OAuth client ID"
   - If prompted, configure the OAuth consent screen:
     - User Type: External (or Internal if using Google Workspace)
     - App name: "Thunderbird Schedule Writer"
     - User support email: your email
     - Developer contact: your email
     - Scopes: Add `.../auth/calendar.events` (or leave default)
     - Test users: Add your email if using External
     - Click "Save and Continue" through the steps
   - Back in Credentials, create OAuth client ID:
     - Application type: "Desktop app"
     - Name: "Thunderbird Schedule App"
     - Click "Create"

5. **Download Credentials:**
   - Click the download icon (⬇) next to your newly created OAuth 2.0 Client ID
   - Save the downloaded JSON file as:
     ```
     ~/.thunderbird-schedule-credentials.json
     ```
   - On Linux/Mac: `~/.thunderbird-schedule-credentials.json`
   - On Windows: `C:\Users\YourUsername\.thunderbird-schedule-credentials.json`

### 3. Ensure Calendar Access

The script writes to this calendar by default:
```
c_f7b7f2cea6f65593ef05afaf2abfcfb48f87e25794468cd4a19d16495d17b6d1@group.calendar.google.com
```

Make sure:
- Your Google account has write access to this calendar
- The calendar is shared with your account with "Make changes to events" permission

## First Run

The first time you use `--write-calendar`:

```bash
thunderbird-schedule desktop 144 2025-08-18 --write-calendar
```

1. Your default browser will open automatically
2. Sign in to your Google account
3. Review the permissions request
4. Click "Allow" to grant calendar access
5. The browser will show "The authentication flow has completed"
6. Close the browser and return to the terminal

The authentication token will be saved to `~/.thunderbird-schedule-token.pickle` for future runs.

## Usage

After setup, simply add `--write-calendar` to any command:

```bash
# Desktop schedule
thunderbird-schedule desktop 144 2025-08-18 --write-calendar

# Android schedule
thunderbird-schedule android 15 2025-10-16 --write-calendar
```

The script will:
- Print the schedule to stdout (as usual)
- Create all-day events in the Google Calendar
- Print progress messages to stderr

## Troubleshooting

**"credentials file not found" error:**
- Verify the file is saved as `~/.thunderbird-schedule-credentials.json`
- Check that it's the OAuth 2.0 client credentials, not API key or service account

**"Access denied" error:**
- Make sure your Google account has write access to the target calendar
- Check that the calendar is shared with your account

**"Invalid credentials" error:**
- Delete `~/.thunderbird-schedule-token.pickle`
- Run the command again to re-authenticate

**Browser doesn't open:**
- The script will print a URL to the terminal
- Copy and paste it into your browser manually

## Security Notes

- The credentials file (`~/.thunderbird-schedule-credentials.json`) contains your OAuth client ID and secret
- The token file (`~/.thunderbird-schedule-token.pickle`) contains your access token
- Keep both files secure and don't commit them to version control
- These files give access to create/modify calendar events in the specified calendar

## Uninstalling

To remove Google Calendar integration:

```bash
# Remove credentials
rm ~/.thunderbird-schedule-credentials.json
rm ~/.thunderbird-schedule-token.pickle

# Uninstall package (pipx)
pipx uninstall thunderbird-release-schedule

# Or uninstall packages (pip)
pip uninstall google-api-python-client google-auth-httplib2 google-auth-oauthlib
```
