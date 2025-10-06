#!/usr/bin/env python3
"""create_fam_command_center

Utility to scaffold an Actionuity "FAM Command Center" workspace in Notion.

The script expects two environment variables to be set:
- NOTION_TOKEN: The Notion integration token with permissions to create
  pages and databases in the target workspace.
- NOTION_PARENT_PAGE_ID: The identifier for the parent page where the
  Command Center page should be created.

Running the script will create:
1. A new page titled "FAM Command Center" under the provided parent page.
2. Five child databases for projects, loops, tasks, logs, and intelligence.
3. Relations, rollups, and formulas connecting the databases.
4. Sample entries in each database to demonstrate usage.
5. Basic instructional content on the Command Center page.

Example usage:
    export NOTION_TOKEN="secret_xxx"
    export NOTION_PARENT_PAGE_ID="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    python create_fam_command_center.py
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import requests

API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _headers() -> Dict[str, str]:
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise RuntimeError("Missing NOTION_TOKEN environment variable.")
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _post(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(
        f"{API_BASE}{path}",
        headers=_headers(),
        data=json.dumps(payload),
        timeout=30,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"POST {path} failed: {response.status_code} {response.text}")
    return response.json()


def _patch(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.patch(
        f"{API_BASE}{path}",
        headers=_headers(),
        data=json.dumps(payload),
        timeout=30,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"PATCH {path} failed: {response.status_code} {response.text}")
    return response.json()


def _append_blocks(block_id: str, children: List[Dict[str, Any]]) -> Dict[str, Any]:
    response = requests.patch(
        f"{API_BASE}/blocks/{block_id}/children",
        headers=_headers(),
        data=json.dumps({"children": children}),
        timeout=30,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Append blocks failed: {response.status_code} {response.text}")
    return response.json()


def create_page(parent_page_id: str, title: str, icon: Optional[str] = None, emoji: Optional[str] = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "properties": {
            "title": [{"type": "text", "text": {"content": title}}]
        },
    }
    if emoji:
        payload["icon"] = {"type": "emoji", "emoji": emoji}
    elif icon:
        payload["icon"] = {"type": "external", "external": {"url": icon}}
    return _post("/pages", payload)


def create_database(parent_page_id: str, title: str, properties: Dict[str, Any], icon_emoji: Optional[str] = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": properties,
    }
    if icon_emoji:
        payload["icon"] = {"type": "emoji", "emoji": icon_emoji}
    return _post("/databases", payload)


def create_page_item_in_db(db_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    payload = {"parent": {"database_id": db_id}, "properties": properties}
    return _post("/pages", payload)


def build_databases(parent_id: str) -> Dict[str, Any]:
    projects_props: Dict[str, Any] = {
        "Name": {"title": {}},
        "Status": {
            "select": {
                "options": [
                    {"name": "Active", "color": "green"},
                    {"name": "Planning", "color": "yellow"},
                    {"name": "Paused", "color": "red"},
                ]
            }
        },
        "Owner": {"people": {}},
        "FAM Mode": {"checkbox": {}},
        "Priority": {
            "select": {
                "options": [
                    {"name": "P0", "color": "red"},
                    {"name": "P1", "color": "orange"},
                    {"name": "P2", "color": "yellow"},
                    {"name": "P3", "color": "gray"},
                ]
            }
        },
        "OKRs": {"rich_text": {}},
        "Notes": {"rich_text": {}},
    }
    db_projects = create_database(parent_id, "🚀 Projects", projects_props, "🚀")

    tricores_props: Dict[str, Any] = {
        "Title": {"title": {}},
        "Project": {"relation": {"database_id": db_projects["id"], "single_property": True}},
        "Core": {
            "select": {
                "options": [
                    {"name": "GPT-5 Strategist", "color": "blue"},
                    {"name": "Codex Executor", "color": "purple"},
                    {"name": "Agent Deployer", "color": "green"},
                ]
            }
        },
        "Stage": {
            "select": {
                "options": [
                    {"name": "Strategize", "color": "blue"},
                    {"name": "Execute", "color": "purple"},
                    {"name": "Deploy", "color": "green"},
                    {"name": "Verify", "color": "gray"},
                ]
            }
        },
        "Auto": {"checkbox": {}},
        "Summary": {"rich_text": {}},
        "Last Run": {"date": {}},
    }
    db_tricores = create_database(parent_id, "🔁 Tri-Core Loops", tricores_props, "🔁")

    tasks_props: Dict[str, Any] = {
        "Task": {"title": {}},
        "Project": {"relation": {"database_id": db_projects["id"], "single_property": True}},
        "Tri-Core Loop": {"relation": {"database_id": db_tricores["id"], "single_property": True}},
        "State": {
            "select": {
                "options": [
                    {"name": "Queued", "color": "yellow"},
                    {"name": "In Progress", "color": "blue"},
                    {"name": "Blocked", "color": "red"},
                    {"name": "Done", "color": "green"},
                ]
            }
        },
        "Assignee": {"people": {}},
        "Due": {"date": {}},
        "Impact": {
            "select": {
                "options": [
                    {"name": "High", "color": "red"},
                    {"name": "Medium", "color": "orange"},
                    {"name": "Low", "color": "gray"},
                ]
            }
        },
        "Notes": {"rich_text": {}},
    }
    db_tasks = create_database(parent_id, "⚙️ Automation Tasks", tasks_props, "⚙️")

    logs_props: Dict[str, Any] = {
        "Title": {"title": {}},
        "Project": {"relation": {"database_id": db_projects["id"], "single_property": True}},
        "Tri-Core Loop": {"relation": {"database_id": db_tricores["id"], "single_property": True}},
        "Task": {"relation": {"database_id": db_tasks["id"], "single_property": True}},
        "Type": {
            "select": {
                "options": [
                    {"name": "Info", "color": "blue"},
                    {"name": "Warning", "color": "yellow"},
                    {"name": "Error", "color": "red"},
                    {"name": "Success", "color": "green"},
                ]
            }
        },
        "Timestamp": {"date": {}},
        "Message": {"rich_text": {}},
        "Tags": {
            "multi_select": {
                "options": [
                    {"name": "FAM", "color": "purple"},
                    {"name": "Sync", "color": "blue"},
                    {"name": "QA", "color": "green"},
                    {"name": "Ops", "color": "gray"},
                ]
            }
        },
    }
    db_logs = create_database(parent_id, "📈 Performance Logs", logs_props, "📈")

    intel_props: Dict[str, Any] = {
        "Title": {"title": {}},
        "Project": {"relation": {"database_id": db_projects["id"], "single_property": True}},
        "Summary": {"rich_text": {}},
        "Confidence": {"number": {"format": "percent"}},
        "Created": {"date": {}},
        "Source": {
            "multi_select": {
                "options": [
                    {"name": "GPT-5 Strategist", "color": "blue"},
                    {"name": "Codex Executor", "color": "purple"},
                    {"name": "Agent Deployer", "color": "green"},
                    {"name": "External", "color": "gray"},
                ]
            }
        },
    }
    db_intel = create_database(parent_id, "🧠 Intelligence Reports", intel_props, "🧠")

    return {
        "projects": db_projects,
        "tricores": db_tricores,
        "tasks": db_tasks,
        "logs": db_logs,
        "intel": db_intel,
    }


def add_rollups_and_formulas(db_ids: Dict[str, Any]) -> None:
    project_db_id = db_ids["projects"]["id"]

    project_properties = {
        "properties": {
            "Active Tasks": {
                "rollup": {
                    "relation_property_name": "Project",
                    "rollup_property_name": "State",
                    "function": "show_original",
                }
            },
            "Health": {
                "formula": {
                    "expression": 'if(prop("FAM Mode") == true, "ACTIVE", "HOLD")'
                }
            },
        }
    }
    _patch(f"/databases/{project_db_id}", project_properties)

    tricores_db_id = db_ids["tricores"]["id"]
    tricores_properties = {
        "properties": {
            "Status Light": {
                "formula": {
                    "expression": 'if(prop("Auto") == true, "AUTO", "MANUAL")'
                }
            }
        }
    }
    _patch(f"/databases/{tricores_db_id}", tricores_properties)


def seed_samples(db_ids: Dict[str, Any]) -> None:
    project = create_page_item_in_db(
        db_ids["projects"]["id"],
        {
            "Name": {
                "title": [
                    {"text": {"content": "Home Quest: Journey to Ownership"}},
                ]
            },
            "Status": {"select": {"name": "Active"}},
            "FAM Mode": {"checkbox": True},
            "Priority": {"select": {"name": "P0"}},
            "OKRs": {
                "rich_text": [
                    {
                        "text": {
                            "content": "Ship Cycle 3 assets; 95% curation complete; 3 pilot families onboarded"
                        }
                    }
                ]
            },
            "Notes": {
                "rich_text": [
                    {"text": {"content": "Command Center seed record."}},
                ]
            },
        },
    )
    project_ref = [{"id": project["id"]}]

    tri_core_configs = [
        ("GPT-5 Strategist", "Strategize"),
        ("Codex Executor", "Execute"),
        ("Agent Deployer", "Deploy"),
    ]

    for core, stage in tri_core_configs:
        loop = create_page_item_in_db(
            db_ids["tricores"]["id"],
            {
                "Title": {"title": [{"text": {"content": f"{core} — Initial Loop"}}]},
                "Project": {"relation": project_ref},
                "Core": {"select": {"name": core}},
                "Stage": {"select": {"name": stage}},
                "Auto": {"checkbox": True},
                "Summary": {
                    "rich_text": [
                        {"text": {"content": "Boot sequence seeded by script."}},
                    ]
                },
                "Last Run": {"date": {"start": "2025-10-06"}},
            },
        )

        create_page_item_in_db(
            db_ids["tasks"]["id"],
            {
                "Task": {
                    "title": [
                        {
                            "text": {
                                "content": f"[{core}] Initialize FAM pipeline",
                            }
                        }
                    ]
                },
                "Project": {"relation": project_ref},
                "Tri-Core Loop": {"relation": [{"id": loop["id"]}]},
                "State": {"select": {"name": "Queued"}},
                "Impact": {"select": {"name": "High"}},
                "Notes": {
                    "rich_text": [
                        {"text": {"content": "Auto-created task for demonstration."}},
                    ]
                },
            },
        )

    create_page_item_in_db(
        db_ids["logs"]["id"],
        {
            "Title": {"title": [{"text": {"content": "FAM Boot Log"}}]},
            "Project": {"relation": project_ref},
            "Type": {"select": {"name": "Info"}},
            "Timestamp": {"date": {"start": "2025-10-06T09:00:00"}},
            "Message": {
                "rich_text": [
                    {"text": {"content": "FAM Command Center initialized."}},
                ]
            },
            "Tags": {
                "multi_select": [
                    {"name": "FAM"},
                    {"name": "Ops"},
                ]
            },
        },
    )

    create_page_item_in_db(
        db_ids["intel"]["id"],
        {
            "Title": {"title": [{"text": {"content": "Cycle 3 Readiness Brief"}}]},
            "Project": {"relation": project_ref},
            "Summary": {
                "rich_text": [
                    {
                        "text": {
                            "content": "Home Quest Cycle 3 is ≥90% content-complete; curation & QA next.",
                        }
                    }
                ]
            },
            "Confidence": {"number": 0.85},
            "Created": {"date": {"start": "2025-10-06"}},
            "Source": {
                "multi_select": [
                    {"name": "GPT-5 Strategist"},
                ]
            },
        },
    )


def decorate_command_center(command_center_page_id: str) -> None:
    blocks: List[Dict[str, Any]] = [
        {
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [
                    {"type": "text", "text": {"content": "FAM Command Center"}},
                ]
            },
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Your Full Autonomous Mode cockpit. Use the databases below for Tri-Core loops, tasks, logs, and intelligence.",
                        },
                    }
                ]
            },
        },
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {"type": "text", "text": {"content": "How to Use"}},
                ]
            },
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Add board views in each database for quick status control (Stage, State, Status).",
                        },
                    }
                ]
            },
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Toggle FAM Mode (checkbox) on Projects to mark automation-ready initiatives.",
                        },
                    }
                ]
            },
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Use Tri-Core Loops to track Strategize → Execute → Deploy → Verify cycles.",
                        },
                    }
                ]
            },
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Log outcomes in Performance Logs; publish syntheses in Intelligence Reports.",
                        },
                    }
                ]
            },
        },
    ]
    _append_blocks(command_center_page_id, blocks)


def main() -> None:
    parent_page_id = os.environ.get("NOTION_PARENT_PAGE_ID")
    if not parent_page_id:
        raise RuntimeError("Missing NOTION_PARENT_PAGE_ID environment variable.")

    page = create_page(parent_page_id, "FAM Command Center", emoji="🛰️")
    command_center_page_id = page["id"]

    db_ids = build_databases(command_center_page_id)

    add_rollups_and_formulas(db_ids)

    seed_samples(db_ids)

    decorate_command_center(command_center_page_id)

    print("\n✅ FAM Command Center created.")
    print(f"- Command Center Page ID: {command_center_page_id}")
    print(f"- Projects DB ID:        {db_ids['projects']['id']}")
    print(f"- Tri-Core Loops DB ID:  {db_ids['tricores']['id']}")
    print(f"- Automation Tasks DB ID:{db_ids['tasks']['id']}")
    print(f"- Performance Logs DB ID:{db_ids['logs']['id']}")
    print(f"- Intelligence Reports DB:{db_ids['intel']['id']}")
    print("\nOpen Notion and add your preferred views (Board, Timeline, List) for each database.")
    print("Tip: Create a Board view grouped by Stage in Tri-Core Loops, and by State in Automation Tasks.")


if __name__ == "__main__":
    main()
