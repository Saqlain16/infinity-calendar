# infinity-calendar
It shows the employee's birthdates in a calendar view of an org
# Team Calendar — Employee Birthdays & Anniversaries

`employees.csv` is the single source of truth. `index.html` reads it directly
in the browser every time the page loads (or you hit **Refresh data**) —
there's no conversion step, no JSON to regenerate, no cache to bust by hand.

**Add a new joiner or remove someone who's left → edit the CSV → refresh the
page.** That's it.

## Files

| File               | Purpose                                                             |
|--------------------|----------------------------------------------------------------------|
| `employees.csv`    | The one file you maintain. Add/remove/edit rows as staff changes.   |
| `index.html`       | The dashboard — reads `employees.csv` live via PapaParse + FullCalendar |
| `csv_to_json.py`   | Optional. A standalone batch export to JSON, useful if you want a static snapshot for reporting elsewhere. Not required for the dashboard to work. |
| `validate_csv.py`  | Optional. Run this before deploying to catch bad date formats (e.g. the Excel DD-MM-YYYY issue) or missing fields, without opening a browser. |
| `employees.json`   | Optional pre-generated snapshot (only relevant if you use the script above). |

## 1. CSV format

`employees.csv` needs exactly these five column headers, spelled and
capitalized exactly as shown, in any order:

| Column          | Type / format         | Required? | Example         |
|-----------------|------------------------|-----------|------------------|
| `Name`          | Text                   | Yes       | `Diptesh Shukla` |
| `Date of Birth` | `YYYY-MM-DD`           | No*       | `1990-08-14`     |
| `Designation`   | Text                   | No        | `FE`             |
| `Date of Joining` | `YYYY-MM-DD`         | No*       | `2026-01-07`     |
| `Branch Name`   | Text                   | No        | `Raipur`         |

\* A row needs *at least one* of Date of Birth or Date of Joining, or it's
skipped entirely (nothing to put on the calendar). Designation and Branch
Name can be blank — the hover card just shows "—" for that field.

Example file:

```csv
Name,Date of Birth,Designation,Date of Joining,Branch Name
Varsha Vani,1987-06-26,Operation Head,2015-03-01,Head Office
Diptesh Shukla,1990-08-14,FE,2026-01-07,Raipur
```

A few things that will silently break it:
- Dates in `DD-MM-YYYY` or `MM/DD/YYYY` format — must be `YYYY-MM-DD`.
- Renamed or misspelled headers (e.g. `DOB` instead of `Date of Birth`) —
  the column is simply ignored.
- Saving as `.xlsx` instead of `.csv` — export back to CSV before deploying.

**To onboard someone:** add a row.
**To offboard someone:** delete their row. Their birthday/anniversary events
disappear from the calendar (and from notifications) on the next refresh —
nothing else to clean up.

## 2. Run it locally

Browsers block `fetch()` of local files opened directly as `file://`, so serve
the folder instead of double-clicking `index.html`:

```bash
cd rcap-birthday-calendar
python3 -m http.server 8000
```

Then open `http://localhost:8000/index.html`.

## 3. What the dashboard does

- **Live CSV sync** — re-reads and re-parses `employees.csv` on load and on
  demand via the "Refresh data" button. The status line under the title
  shows how many records were found and when it last checked.
- **Month view + list view** — toggle between a calendar grid and a flat
  chronological list (handy on mobile, or for printing a month's list).
- **Coming up panel** — the next 60 days of birthdays/anniversaries across
  the whole company, closest first, with a "Today" / "Tomorrow" / "N days"
  badge.
- **Search & filter** — search by name, filter by branch, or toggle
  birthdays/anniversaries on and off with the chips. All three affect the
  calendar, the stats, and the "Coming up" panel together.
- **Hover card** — Name, Date of Birth, Designation, Branch, Date of
  Joining, plus age turning (birthdays) or years of service (anniversaries).
- **Avatars** — each employee gets a consistent colored initials badge
  (derived from their name), shown on calendar chips and in the sidebar, so
  repeat names are easy to spot at a glance across the month.
- **Stats bar** — birthdays this month, anniversaries this month, total
  employees on record, and number of branches — all recompute as you filter.
- **Notification bell** — birthdays only (anniversaries are deliberately
  excluded, as requested), sorted into three fixed buckets:
  - **Today** — birthday is today
  - **This week** — 1–7 days from now
  - **This month** — later in the current calendar month, after this week
  Each person appears once, in their nearest upcoming bucket, so there's no
  double-counting. The badge on the bell shows today's count (or this
  week's, if nobody's birthday is today).
  - **Desktop alerts**: click "Enable desktop alerts" in the panel to opt in
    to a native OS/browser notification when there's a birthday today. This
    only fires while the tab is open — see the limitation below.

## 4. Deploy

Any static host works, since there's still no backend:

- **GitHub Pages**: push the folder to a repo, enable Pages.
- **Netlify**: drag-and-drop the folder into Netlify's deploy UI.
- **Intranet server**: drop the folder into any web server's static root.

To update staff, edit `employees.csv` directly in the deployed folder (or via
your normal deploy process) and reload the page — no build step, no redeploy
of a second file.

## 5. Troubleshooting

**"Excel keeps changing my dates back to DD-MM-YYYY"**
Excel auto-detects date-looking text and redisplays it using your regional
settings every time you reopen the file — it's not actually ignoring your
edit, it's re-converting on open. Fixes, pick one:
- Edit the CSV in Notepad, VS Code, or Google Sheets instead of Excel.
- In Excel: select the date columns → *Format Cells* → **Text**, before
  typing/pasting `YYYY-MM-DD` values, so Excel stores them literally.
- Run `python validate_csv.py employees.csv` after saving — it'll flag any
  row where a date isn't in `YYYY-MM-DD` and tell you which one.

**"index.html shows 0 records"**
This is almost always because the file was opened directly by double-click
(`file://...`). Browsers block reading local files that way. Serve the
folder instead:
```bash
cd rcap-birthday-calendar
python3 -m http.server 8000
```
Then open `http://localhost:8000/index.html`. Once deployed to GitHub
Pages/Netlify/an intranet server (served over `http://` or `https://`
rather than `file://`), this isn't an issue at all.

If it's still 0 after serving properly, open the browser console (F12) —
the sync status line and the amber warning banner (if it appears) will show
exactly which rows/fields failed to parse.

## 6. When to deploy

Once `python validate_csv.py employees.csv` reports no issues, and
`http://localhost:8000/index.html` shows the correct record count with no
warning banner, it's ready. There's nothing else to prepare — deploy
whenever convenient.

## Notes / limitations

- Still backend-free by design: no database, auth, or write path. If you
  want employees to self-update, or want this wired into a CRM/HRMS, that's
  a separate build.
- **Notifications only fire while someone has the page open in a tab.**
  There's no server here to push a real notification to your phone or
  desktop at 9am even if nobody has the browser open — that needs a backend
  (a scheduled job + a push service, e.g. via service workers and VAPID
  keys, or simpler: a daily Slack/email digest triggered by a cron job that
  reads the same CSV). If that's something you want, it's a natural next
  step but a separate piece of infrastructure from this static page.
- Feb 29 birthdays/anniversaries are rolled forward to Mar 1 in non-leap
  years.
- Events are generated for last year through 5 years ahead from *today's*
  date, recalculated on every load — so the window itself never goes stale.
- If two employees share an exact name, they'll get the same avatar color;
  add a unique ID column and tweak `hashColor()` in `index.html` if that
  matters for your org.
