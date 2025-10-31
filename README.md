# Thunderbird Release Schedule Generator

Generate a Thunderbird Desktop or Android release schedule based on the application, major version, and <version>.0a1 start date.

## Installation

Install the package to get the `thunderbird-schedule` console command:

**Isolated install with pipx:**

```bash
pipx install .
# to add calendar extras later
pipx inject thunderbird-release-schedule google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

**Editable install (development):**

```bash
pip install -e .
# with optional Google Calendar extras
pip install -e .[calendar]
```

## Usage

```bash
thunderbird-schedule <application> <major> <a1-start-date>
```

Or run directly without installation:

```bash
python3 thunderbird_schedule.py <application> <major> <a1-start-date>
```

Supported applications: `desktop`, `android`

**Examples:**

```bash
thunderbird-schedule desktop 146 2025-10-13
thunderbird-schedule android 15 2025-10-16
```

The provided date is the day of the "<major>.0a1 starts" milestone:
- For `desktop` (Thunderbird): date **must be a Monday**
- For `android` (Thunderbird for Android / TfA): date **must be a Thursday**

The script uses application-specific templates with milestone and weekday constraints. For each milestone, the script:

- Shifts by the template offset from the a1 start date
- Adjusts to match the template's required weekday (previous-or-same occurrence)
- Ensures milestones remain in chronological order (pushing forward by 7 days if needed)

Dates print in the format `Month D, YYYY` with columns for Date, Weekday, and Milestone label.

## Google Calendar Integration

You can optionally write the schedule directly to Google Calendar using the `--write-calendar` flag:

```bash
thunderbird-schedule desktop 146 2025-10-13 --write-calendar
thunderbird-schedule android 15 2025-10-16 --write-calendar
```

### Setup for Google Calendar

For detailed setup instructions including Google Cloud Console configuration and authentication, see [GOOGLE_CALENDAR_SETUP.md](GOOGLE_CALENDAR_SETUP.md).

## Development and Testing

**Requirements:** Python 3.12 or later

Run the test suite using unittest:

```bash
python -m unittest discover -s tests -v
```

Tests run automatically in GitHub Actions CI across Python 3.12 and 3.13 on every push and pull request.
