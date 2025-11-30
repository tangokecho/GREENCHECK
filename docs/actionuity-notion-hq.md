# Actionuity Notion HQ Build Guide

This guide explains how to recreate Actionuity's HQ inside the **actual Notion app** using native pages, databases, and templates. It is written so you can stand up a reliable workspace without custom integrations. Follow the numbered steps in order; everything can be done with built‑in Notion blocks, relations, and formulas.

## 1) Create the workspace shell
1) Create a new page called **Actionuity HQ** in your Notion sidebar and add a simple cover + icon for quick recognition.
2) Add four child pages to keep navigation clear:
   - **Home (Command Center)**
   - **Projects & Delivery**
   - **People & Operations**
   - **Revenue & Finance**
3) Add a short "How to use this HQ" callout at the top with links to onboarding and support contacts.
4) Pin a **Changelog** toggle list that records edits to databases, views, and templates so teammates know what changed.

## 2) Core databases to build
Create the following databases as **full-page tables** under Actionuity HQ. Use the property types exactly as listed so templates and rollups work. After each database is created, add a **Board** view grouped by the most important property to make the layout useful by default.

| Database | Required properties | Helpful extras |
| --- | --- | --- |
| **Projects** | Name (Title), Status (Select: Idea, Active, Blocked, Done), Owner (Person), Squad (Multi-select), Priority (Select: P0–P3), Start (Date), Target Launch (Date), Confidence (Number, 0–1), OKR Link (Relation → OKRs), Docs (Files & media) | Formula: `if(prop("Status")="Done", 1, empty())` to use in rollups; Relation: Tasks (Relation → Tasks, show only status + due) |
| **Tasks** | Name (Title), Project (Relation → Projects), Status (Select: Todo/In progress/Review/Done), Assignee (Person), Sprint (Relation → Sprints), Effort (Number), Due (Date), Tags (Multi-select), Blocked? (Checkbox) | Formula: `if(prop("Blocked?"), "🚧", "")` to flag cards; Rollup: Project Target Launch; Checkbox: Needs QA |
| **Sprints** | Name (Title), Start (Date), End (Date), Goal (Text), Retrospective (Text), Velocity (Number) | Formula: `dateBetween(now(), prop("Start"), prop("End"))` to show Active?; Relation: Tasks |
| **OKRs** | Objective (Title), Cycle (Select: H1, H2), Status (Select), KRs (Text), Confidence (Number), DRIs (People) | Relation: Projects, so every project can roll up to its objective |
| **Docs** | Title (Title), Type (Select: Spec, Decision, Retro, Meeting Notes), Related Project (Relation → Projects), Owner (Person), Date (Date) | Files: Attachments; Status (Select: Draft/Review/Final) |
| **CRM Deals** | Company (Title), Stage (Select), Amount (Number, currency), Close Date (Date), Champion (Person), Next Step (Text), Probability (%) | Checkbox: Renewals; Relation: Docs for meeting notes |
| **Vendors/Tools** | Name (Title), Category (Select), Owner (Person), Cost (Number, currency), Renewal (Date), Contract (Files), Security Review (Checkbox) | Formula to flag upcoming renewals: `dateBetween(prop("Renewal"), now(), dateAdd(now(), 30, "days"))` |
| **People Directory** | Name (Title), Team (Select), Role (Text), Manager (Person), Start Date (Date), Location (Text), Bio (Text), Links (URL) | Relation: Projects for DRIs; Checkbox: Onboarding complete |

## 3) Page layout recommendations

### Home (Command Center)
- Add a **hero** section with mission + current quarter theme.
- Insert linked views:
  - "This week" tasks filtered to current week.
  - "Active projects" board by Status.
  - "Top OKRs" filtered to in-flight cycles.
- Add a **Quick Actions** callout: "Start new project", "Log decision", "Book retro", "Submit vendor request" (each links to a template button).
- Include a **Now / Next / Later** 3-column list for leadership priorities.

### Projects & Delivery
- Place the **Projects** board (grouped by Status) at the top.
- Add a **Project intake template button** that duplicates a pre-styled project page with sections for Brief, Risks, Milestones, and Links.
- Create a **Tasks** board filtered by the current sprint and grouped by Status.
- Add a **Docs** linked database filtered to the selected project.
- Pin a **Retros & Learnings** section where retro notes are tagged and summarized.
- Add a **Risks heatmap** callout summarizing top 3 risks with owners; link to the relevant Task cards for mitigations.

### People & Operations
- Start with the **People Directory** table and a "New hire checklist" toggle list.
- Add a **Vendors/Tools** table with renewal reminders and a relation to security reviews.
- Create a **Policies & How-tos** list (simple toggles) linking to onboarding, PTO, security, and procurement guides.
- Add a **Request tracker** (simple inline database) for access, procurement, and IT tickets; relate it to Vendors when relevant.

### Revenue & Finance
- Add a **CRM Deals** board grouped by Stage with a "Forecast" table sorted by Close Date.
- Create a **Pipeline health** callout that shows next steps on deals with Probability < 0.6.
- Add a **Finance dashboard** section with quick links to burn, runway, and invoices (these can be embeds or linked databases if you store them in Notion).
- Include a **Renewals radar** linked view of Vendors filtered to renewals in the next 60 days; sort by Renewal date.

## 4) Templates to wire up
Implement template buttons or database templates for repeatable work. Configure these inside the database **Templates** tab so every new entry inherits structure.

- **Project brief** (Projects): Summary, Goals, Metrics, Scope, Risks, Dependencies, Timeline, Stakeholders, Links, Decision log (linked Docs filtered to Type = Decision), RAID table toggle.
- **Sprint** (Sprints): Goal, Capacity, Planned commits (Relation → Projects), Retro notes, Demo links, Outcomes, Velocity capture, Action items (Relation → Tasks, filtered by Sprint).
- **Meeting notes** (Docs): Agenda, Attendees, Decisions (Relation → Docs with Type = Decision), Actions (Relation → Tasks). Pre-create tags for recurring meetings.
- **Retro** (Docs, Type = Retro): What went well, What to improve, Actions (Relation → Tasks), Owner, Due, Emojis for sentiment.
- **Deal review** (CRM Deals): ICP fit, Pain, Champion, Competition, Next step, Mutual close plan, Mutual action plan checklist.
- **Security review** (Vendors/Tools): Vendor, Data handled, Risk level, Owner, Renewal date, Decision, Compliance artifacts (files), Security reviewer.

## 5) Automation ideas (native to Notion)
- **Status rollups**: In Projects, add a rollup of linked Tasks to compute % done. Set `Calculate` → `% checked` on Task status checkboxes or `Average` on the formula field noted above.
- **Overdue alerts**: Create a view that filters Tasks where Due < Today AND Status is not Done; pin it on Home. Subscribe the team to this view so Notion sends reminders.
- **Intake routing**: Add a "Submission Type" select in Docs (Spec/Decision/Retro) and default Status to "Review" to keep intake tidy.
- **Lightweight approvals**: Use a "Needs review" checkbox + person property to ping reviewers via comments. Add a filtered view that only shows items with Needs review = ✅.
- **Auto-assign templates**: For Tasks, set the default template to the Sprint task template so every new Task includes estimation fields.

## 6) Permissions and governance
- Keep **Actionuity HQ** open to the org, but lock the database schemas to avoid accidental edits.
- Create a **Founders & Leads** group with edit rights on OKRs, Finance, and CRM; make other teams comment-only on sensitive views.
- Add **page rules** explaining naming conventions (e.g., `2024-09-12 – Meeting – Partner Sync`).
- Turn on **Database locking** (••• → Lock database) after property creation to prevent accidental schema edits; unlock only when changing templates.
- For Docs, restrict **Decision** and **Security review** templates to editors; allow view/comment to everyone else.
- Document the SLA for intake items (e.g., vendor requests responded to within 2 business days) in the Policies section.

## 7) Onboarding checklist
1. Invite teammates and group them (Product, Eng, GTM, Ops).
2. Publish the **How to use this HQ** page and pin it to Home.
3. Seed example entries: one project, five tasks, one sprint, two OKRs, two docs, one deal, one vendor.
4. Test template buttons and relations; confirm rollups and default filters.
5. Record a 5-minute Loom walking through the HQ.
6. Schedule a monthly housekeeping slot to archive stale projects and close loops on tasks and retros.
7. Add a **Workspace status** toggle (Green/Amber/Red) with a brief note; review it weekly in leadership syncs.

## 8) Visual polish (optional)
- Use the provided icon set for databases (Projects, Tasks, Docs, CRM, Finance) to keep navigation consistent.
- Add a **dark/light-friendly** color palette for callouts: green for success, yellow for risks, red for blockers, grey for neutral info.
- Keep page widths at "Full width" for boards and calendars; use "Layout: Small text" for documentation-heavy pages.
- Create a **Template gallery** page with screenshots/gifs of the main templates so newcomers know what to expect when they click "New".

## 9) Export/backup tips
- Enable **automated exports** (Settings → Export content) on a monthly cadence if governance requires it.
- For critical databases (Projects, Tasks, CRM), export CSV snapshots quarterly and store them in your data room.

---
With these steps, you can stand up Actionuity's Notion HQ quickly in the actual Notion app, while keeping it maintainable as the team grows.
