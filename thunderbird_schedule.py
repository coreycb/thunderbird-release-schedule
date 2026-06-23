#!/usr/bin/env python3
"""
Thunderbird schedule generator.

Usage:
    thunderbird-schedule <application> <major> <a1-start-date> [--write-calendar]

Examples:
        thunderbird-schedule desktop 146 2025-10-13
        thunderbird-schedule android 15 2025-10-16 --write-calendar

The provided date is the '<application> <major>.0a1 starts' milestone.
- For 'desktop': date MUST be a Monday
- For 'android': date MUST be a Thursday

The schedule uses application-specific templates with milestone and weekdays.

Optional flags:
  --write-calendar  Write events to Google Calendar (requires setup)
"""
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import sys
from typing import List, Tuple

@dataclass(frozen=True)
class TemplateMilestone:
    # Logical key for this milestone (used for anchoring)
    key: str
    # Days offset from GA (.0) date
    delta_days: int
    # Weekday (0=Monday..6=Sunday) to enforce
    weekday: int
    # Label formatter; receives channel and major to produce label
    label: str

# Build the template for Desktop relative to a1 starts
# Weekdays validated from the provided dates.
TEMPLATE_DESKTOP: List[TemplateMilestone] = [
    TemplateMilestone("a1-starts", 0, 0, "Thunderbird {major}.0a1 starts"),
    TemplateMilestone("a1-soft-freeze", 21, 0, "Thunderbird {major}.0a1 soft freeze starts"),
    TemplateMilestone("a1-pre-merge", 24, 3, "Thunderbird {major}.0a1 pre-merge review"),
    TemplateMilestone("a1-merge", 28, 0, "Thunderbird merge {major}.0a1 central->beta"),
    TemplateMilestone("b1", 30, 2, "Thunderbird {major}.0b1"),
    TemplateMilestone("b2", 37, 2, "Thunderbird {major}.0b2"),
    TemplateMilestone("b3", 44, 2, "Thunderbird {major}.0b3"),
    TemplateMilestone("b4-pre-merge", 45, 3, "Thunderbird {major}.0 beta pre-merge review"),
    TemplateMilestone("b4", 51, 2, "Thunderbird {major}.0b4"),
    TemplateMilestone("b4-merge", 51, 2, "Thunderbird merge {major}.0 beta->release"),
    TemplateMilestone("ga", 57, 1, "Thunderbird {major}.0"),
    TemplateMilestone("dot1", 71, 1, "Thunderbird {major}.0.1"),
]

# Build the template for Android relative to a1 starts
# Weekdays validated from the provided dates.
TEMPLATE_ANDROID: List[TemplateMilestone] = [
    TemplateMilestone("a1-starts", 0, 3, "TfA {major}.0a1 starts"),
    TemplateMilestone("a1-soft-freeze", 21, 3, "TfA {major}.0a1 soft freeze starts"),
    TemplateMilestone("a1-merge", 28, 3, "TfA merge {major}.0a1 main->beta"),
    TemplateMilestone("b1", 32, 0, "TfA {major}.0b1"),
    TemplateMilestone("b2", 39, 0, "TfA {major}.0b2"),
    TemplateMilestone("b3", 46, 0, "TfA {major}.0b3"),
    TemplateMilestone("b-merge", 53, 0, "TfA merge {major}.0 beta->release"),
    TemplateMilestone("ga", 60, 0, "TfA {major}.0"),
    TemplateMilestone("dot1", 74, 0, "TfA {major}.1"),
]

WEEKDAY_NAME = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]


@dataclass(frozen=True)
class Options:
    write_calendar: bool = False
    calendar_id: str = "c_f7b7f2cea6f65593ef05afaf2abfcfb48f87e25794468cd4a19d16495d17b6d1@group.calendar.google.com"


def parse_args(argv: List[str]) -> Tuple[str, int, date, Options]:
    # Check for help flag anywhere in arguments
    if any(arg in ("--help", "-h") for arg in argv[1:]):
        print(__doc__.strip())
        sys.exit(0)

    if len(argv) < 4:
        print(__doc__.strip())
        sys.exit(2)
    application = argv[1].lower()
    try:
        major = int(argv[2])
    except ValueError:
        print("major must be an integer, e.g. 146", file=sys.stderr)
        sys.exit(2)
    try:
        a1_date = datetime.strptime(argv[3], "%Y-%m-%d").date()
    except ValueError:
        print("date must be in YYYY-MM-DD format", file=sys.stderr)
        sys.exit(2)
    # enforce weekday constraint based on application
    if application == "desktop":
        if a1_date.weekday() != 0:
            print("error: desktop a1 start date must be a Monday (weekday=0)", file=sys.stderr)
            sys.exit(2)
    elif application == "android":
        if a1_date.weekday() != 3:
            print("error: android a1 start date must be a Thursday (weekday=3)", file=sys.stderr)
            sys.exit(2)
    else:
        print(f"error: unknown application '{application}'. Supported: desktop, android", file=sys.stderr)
        sys.exit(2)
    # parse optional flags
    write_calendar = False
    for arg in argv[4:]:
        if arg == "--write-calendar":
            write_calendar = True
        else:
            print(f"unknown option: {arg}", file=sys.stderr)
            sys.exit(2)
    return application, major, a1_date, Options(write_calendar=write_calendar)


def find_template_by_key(template: List[TemplateMilestone], key: str) -> TemplateMilestone:
    for tm in template:
        if tm.key == key:
            return tm
    raise KeyError(f"unknown anchor key: {key}")


def get_template(application: str) -> List[TemplateMilestone]:
    """Return the appropriate template based on application."""
    if application == "desktop":
        return TEMPLATE_DESKTOP
    elif application == "android":
        return TEMPLATE_ANDROID
    else:
        raise ValueError(f"unknown application: {application}")


def generate_schedule(application: str, major: int, a1_date: date) -> List[Tuple[date, str]]:
    # Select template based on application
    template = get_template(application)
    # a1_date is the a1-starts date directly (offset is 0)
    out: List[Tuple[date, str]] = []
    for tm in template:
        # Compute target date from a1_date using template offset
        target = a1_date + timedelta(days=tm.delta_days)

        # Verify the calculated date falls on the expected weekday
        if target.weekday() != tm.weekday:
            label = tm.label.format(major=major)
            print(f"error: milestone '{label}' falls on {WEEKDAY_NAME[target.weekday()]} "
                  f"but template expects {WEEKDAY_NAME[tm.weekday]}", file=sys.stderr)
            print(f"  calculated date: {target}", file=sys.stderr)
            print(f"  template offset: {tm.delta_days} days from a1 start", file=sys.stderr)
            sys.exit(1)

        label = tm.label.format(major=major)
        out.append((target, label))
    return out


def format_date(d: date) -> str:
    return d.strftime("%B %-d, %Y") if sys.platform != "win32" else d.strftime("%B %#d, %Y")


def write_to_google_calendar(schedule: List[Tuple[date, str]], application: str, major: int, calendar_id: str):
    """Write schedule events to Google Calendar using the API."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        import os.path
        import pickle
    except ImportError:
        print("Error: Google Calendar API libraries not installed.", file=sys.stderr)
        sys.exit(1)

    SCOPES = ['https://www.googleapis.com/auth/calendar.events']
    creds = None

    # Token file stores user's access and refresh tokens
    token_file = os.path.expanduser('~/.thunderbird-schedule-token.pickle')

    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Need credentials.json from Google Cloud Console
            creds_file = os.path.expanduser('~/.thunderbird-schedule-credentials.json')
            if not os.path.exists(creds_file):
                print("Error: Google Calendar credentials file not found.", file=sys.stderr)
                print(f"Expected at: {creds_file}", file=sys.stderr)
                print("\nTo set up:", file=sys.stderr)
                print("1. Go to https://console.cloud.google.com/", file=sys.stderr)
                print("2. Create a project and enable Google Calendar API", file=sys.stderr)
                print("3. Create OAuth 2.0 credentials (Desktop app)", file=sys.stderr)
                print(f"4. Download credentials.json and save to {creds_file}", file=sys.stderr)
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Create events
    print(f"Writing {len(schedule)} events to Google Calendar...", file=sys.stderr)
    for event_date, label in schedule:
        event = {
            'summary': label,
            'start': {
                'date': event_date.isoformat(),
                'timeZone': 'America/New_York',
            },
            'end': {
                'date': event_date.isoformat(),
                'timeZone': 'America/New_York',
            },
            'description': f'{application.capitalize()} {major} milestone',
            'transparency': 'transparent',  # Show as "free" instead of "busy"
        }

        try:
            created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
            print(f"Created: {event_date} - {label}", file=sys.stderr)
        except Exception as e:
            print(f"Error creating event for {event_date}: {e}", file=sys.stderr)

    print(f"\nSuccessfully wrote schedule to calendar!", file=sys.stderr)
    print(f"View at: https://calendar.google.com/calendar/embed?src={calendar_id}", file=sys.stderr)


def main(argv: List[str]) -> int:
    application, major, a1_date, opts = parse_args(argv)
    schedule = generate_schedule(application, major, a1_date)

    # Print aligned columns: Date | Weekday | Label
    rows = [(format_date(d), WEEKDAY_NAME[d.weekday()], label) for d, label in schedule]
    date_w = max(len(r[0]) for r in rows) if rows else 0
    day_w = max(len(r[1]) for r in rows) if rows else 0
    for date_str, day_str, label in rows:
        print(f"{date_str:<{date_w}}  {day_str:<{day_w}}  {label}")

    # Write to Google Calendar if requested
    if opts.write_calendar:
        write_to_google_calendar(schedule, application, major, opts.calendar_id)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))


# Console-script entry point wrapper for packaging
def cli() -> int:
    """Entry point used by console_scripts.

    This simply forwards to main(sys.argv) so it can be invoked as
    `thunderbird-schedule` when installed from a wheel.
    """
    return main(sys.argv)
