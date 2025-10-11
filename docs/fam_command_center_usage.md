# FAM Command Center Setup Guide

This guide explains how to run `create_fam_command_center.py` to provision the Actionuity FAM Command Center structure inside your Notion workspace.

## Prerequisites

1. **Python 3.9+** installed locally.
2. **Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Notion integration token:**
   - Go to [Notion My Integrations](https://www.notion.so/my-integrations) and create a new internal integration in the target workspace.
   - Copy the generated *Internal Integration Token*; this becomes your `NOTION_TOKEN`.
4. **Parent page access:**
   - Open the page in Notion where the Command Center should live.
   - Share the page with the integration (Share → Invite → select your integration).
5. **Parent page ID:**
   - With the page open, copy the URL and remove any trailing query parameters.
   - The 32-character string after the final `/` is the ID. Remove any hyphens and export it as `NOTION_PARENT_PAGE_ID`.

## Environment variables

Export the credentials in your shell session (or source them from a `.env` file):

```bash
export NOTION_TOKEN="secret_xxx"
export NOTION_PARENT_PAGE_ID="0123456789abcdef0123456789abcdef"
```

## Running the script

Provision the Command Center by running:

```bash
python create_fam_command_center.py
```

The script will:

- Create a **FAM Command Center** parent page under the provided parent.
- Add the five supporting databases (Projects, Tri-Core Loops, Automation Tasks, Performance Logs, Intelligence Reports).
- Configure relations, rollups, and formulas tying everything together.
- Seed example rows so you can see how information flows across the workspace.
- Append quick-start instructions to the Command Center landing page.

When the run completes, the terminal prints the IDs of the newly created resources for reference.

## Need a refresher?

Print the embedded setup walkthrough without provisioning anything:

```bash
python create_fam_command_center.py --instructions
```

## After running the script

1. Visit the new Command Center page in Notion.
2. Add your preferred database views (Board, List, Calendar, etc.).
3. Update sharing settings and permissions for your team.
4. Replace the seeded example content with your own projects, loops, tasks, and reports.

## Troubleshooting tips

- **401 Unauthorized:** Verify the `NOTION_TOKEN` has access to the parent page and that the integration is invited to the page.
- **404 Not Found:** Double-check the `NOTION_PARENT_PAGE_ID` for typos or missing characters.
- **429 Rate Limited:** Wait a few seconds and rerun; the script makes sequential API calls, so reruns are safe.
- **Idempotency:** Running the script multiple times will create duplicate structures. Delete any unwanted pages in Notion before rerunning.

For more details on the API calls, read through [`create_fam_command_center.py`](../create_fam_command_center.py), which is thoroughly commented and structured for clarity.
