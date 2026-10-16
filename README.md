# Thunderbird Release Schedule Generator

Generate a Thunderbird Desktop or Android release schedule from the major version and the `<major>.0a1` start date. Optionally write it to Google Calendar and/or Notion.

## Installation

Requires Python 3.12 or later. From the repo root, install with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install --force --python 3.12 ".[notion,calendar]"
```

`--python 3.12` makes uv use (or download) Python 3.12 even if your default Python is older. The extras are optional: `calendar` enables `--write-calendar` and `notion` enables `--write-notion`. Leave out any you don't need, e.g. `".[notion]"`.

To pick up local changes, re-run the command with `--reinstall` so uv rebuilds the package instead of reusing a cached build.

## Usage

```bash
thunderbird-schedule <application> <major> <a1-start-date> [options]
```

- `application` is `desktop` or `android`.
- `a1-start-date` is the date of the "`<major>`.0a1 starts" milestone, in `YYYY-MM-DD` format. It must be a **Thursday**.

```bash
thunderbird-schedule desktop 146 2025-10-16
thunderbird-schedule android 15 2025-10-16
```

Each milestone date is a fixed offset from the a1 start date. The script prints the date, weekday, and milestone name for each. It exits with an error if a milestone would land on the wrong weekday.

## Google Calendar (`--write-calendar`)

```bash
thunderbird-schedule desktop 146 2025-10-16 --write-calendar
```

Creates an all-day event for each milestone in the **Thunderbird Releases & Events** Google Calendar. Your Google account needs "Make changes to events" access to that calendar. To use a different calendar, change `calendar_id` in `thunderbird_schedule.py`.

### Setup

1. In the [Google Cloud Console](https://console.cloud.google.com/), create or select a project and enable the **Google Calendar API**.
2. Under **APIs & Services → Credentials**, create an **OAuth client ID** with application type **Desktop app**. If asked, set up the OAuth consent screen first. Choose Internal for a Google Workspace account; for External, add yourself as a test user.
3. Download the client JSON, save it as `~/.thunderbird-schedule-credentials.json`, and restrict it so only you can read it:
   ```bash
   chmod 600 ~/.thunderbird-schedule-credentials.json
   ```
4. Run with `--write-calendar`. A browser opens for you to sign in and allow access. If it doesn't, open the URL printed in the terminal. The login is saved to `~/.thunderbird-schedule-token.pickle`, which the script creates readable only by you.

## Notion (`--write-notion`)

```bash
thunderbird-schedule desktop 160 2026-10-08 --write-notion --assignee "Jane Doe"
```

Creates a **task** in the Notion tasks database for each schedule date except "0a1 starts". Task titles drop the "Thunderbird " or "TfA " prefix (e.g. `160.0b1`, `merge 160.0a1 main->beta`). Each task gets:

- **Original Due Date:** the schedule date
- **Team:** Build & Release
- **Assignee:** `--assignee`, given as a Notion display name or email
- **Milestones:** linked to the monthly release milestone for the task's date. A task on 2026-10-26 goes to **2026 October Releases**, and one on 2026-11-02 to **2026 November Releases**. Those milestones must already exist in Notion; the script never creates or edits milestones.
- **Estimate:** 2 for b1, 1 for all other tasks

`--assignee` is required. The script checks the assignee, every month's milestone, the team, and the database fields before writing anything; if any check fails (for example, next month's milestone hasn't been created yet), it exits without creating tasks. Tasks whose title already exists are skipped, so re-running is safe.

### Setup

1. **Get a token.** Use either:
   - a **personal access token**: in Notion, **Settings → Developer**, create one for the Thunderbird workspace; or
   - a **connection**: at https://app.notion.com/developers/connections, create one of type **API Token** (not OAuth). Enable the *Read content*, *Insert content*, and *Read user information* capabilities. Choose "including email addresses" for the last one if you want to pass emails to `--assignee`.

   Copy the token right away and treat it like a password.
2. **Give the token access** to all three databases (the same ones [notion-scripts](https://github.com/thunderbird/notion-scripts) syncs to):

   | database | ID |
   |---|---|
   | tasks | `2332df5d45ae8072aa7aededaf161252` |
   | milestones | `2332df5d45ae80909305fe2278a14629` |
   | teams | `2332df5d45ae80bc8839d089f5c7f608` |

   On each database, open `•••` → **Connections** and add your connection. Sharing their parent page covers all three. You only do this once; milestones added later are covered automatically. If you can't add it, ask a workspace admin.

   All three are needed. A **404 "Could not find database"** means the tasks database isn't shared with the token. An error that **`Milestones`** or **`Team`** is missing, even though you see it in Notion, usually means the milestones or teams database isn't shared with the token.
3. **Create `~/.thunderbird-schedule-notion.toml`** and run `chmod 600` on it:
   ```toml
   token = "ntn_..."
   database_id = "2332df5d45ae8072aa7aededaf161252"   # tasks database

   # Optional; defaults shown
   team = "Build & Release"
   milestone_format = "{year} {month} Releases"   # milestone title for each task's month

   [properties]                     # only needed if your field names differ
   title = "Name"
   date = "Original Due Date"
   assignee = "Assignee"
   estimate = "Estimate"            # select or number
   team = "Team"                    # relation to the teams DB, select, or multi-select
   milestone = "Milestones"         # relation to the milestones DB
   milestone_title = "Name"         # title field in the milestones DB
   ```
   The script finds the milestones and teams databases through the tasks database, so they don't go in the config. To use a different file, set `THUNDERBIRD_SCHEDULE_NOTION_CONFIG=/path/to/file.toml`.

   For a trial run, notion-scripts' dev tasks database is `3372df5d45ae808f83dcce2c88580ffa` (if your token can access it).

## Development

`uv run` creates a `.venv` in the repo from `uv.lock` and runs a command in it:

```bash
# run the tests
uv run python -m unittest discover -s tests -v

# run the script from source, with both extras
uv run --all-extras thunderbird-schedule desktop 160 2026-10-08
```

The tests don't call Google or Notion, so the extras aren't needed. CI runs them on Python 3.12 and 3.13 for every push and pull request.

### Dependencies and `uv.lock`

`uv.lock` pins the exact version of every dependency, including indirect ones, so every development environment gets the same packages. Commit it whenever it changes. It only affects `uv run` and `uv sync`; `uv tool install` ignores it and installs the newest versions allowed by `pyproject.toml`.

- **Add or change a dependency:** edit `pyproject.toml`, then run `uv lock` (or just `uv run …`, which updates the lock automatically).
- **Upgrade all dependencies:** `uv lock --upgrade`, then run the tests and commit `uv.lock`. Do this now and then so development environments don't fall behind fresh installs.
- **Upgrade one dependency:** `uv lock --upgrade-package notion-client`.
- **Check the lock matches `pyproject.toml`:** `uv lock --check`.
