# Actionuity Notion HQ Build Guide

This guide explains how to recreate Actionuity's HQ inside the **actual Notion app** using native pages, databases, and templates. It is written so you can stand up a reliable workspace without custom integrations.

## 1) Create the workspace shell
- Create a new page called **Actionuity HQ** in your Notion sidebar and add a simple cover + icon for quick recognition.
- Inside, add four top-level pages to keep navigation clear:
  1. **Home (Command Center)**
  2. **Projects & Delivery**
  3. **People & Operations**
  4. **Revenue & Finance**

Add a short "How to use this HQ" callout at the top with links to onboarding and support contacts.

## 2) Core databases to build
Create the following databases (as full-page tables). Use linked views in the relevant pages so teams only see what they need.

| Database | Required properties | Useful views |
| --- | --- | --- |
| **Projects** | Name (Title), Status (Select: Idea, Active, Blocked, Done), Owner (Person), Squad (Multi-select), Priority (Select), Start, Target Launch, Confidence (Number 0-1), OKR Link (Relation → OKRs), Docs (Files & media) | Board by Status, Table filtered to "Active", Timeline by Target Launch |
| **Tasks** | Name, Project (Relation → Projects), Status (Todo/In progress/Review/Done), Assignee, Sprint (Relation → Sprints), Effort (Number), Due, Tags (Multi-select), Blocked? (Checkbox) | Board by Status, My Tasks (Assignee is Me), Sprint view grouped by Status |
| **Sprints** | Name, Start, End, Goal (Text), Retrospective (Text), Velocity (Number) | Calendar, Active Sprint (date is within current) |
| **OKRs** | Objective (Title), Cycle (Select: H1, H2), Status (Select), KRs (Text), Confidence (Number), DRIs (People) | Board by Status, Table filtered by Cycle |
| **Docs** | Title, Type (Select: Spec, Decision, Retro, Meeting Notes), Related Project (Relation → Projects), Owner, Date | Table sorted by Date, Gallery by Type |
| **CRM Deals** | Company, Stage (Select), Amount, Close Date, Champion, Next Step (Text), Probability (%) | Board by Stage, Forecast (table sorted by Close Date), Won/Lost reports |
| **Vendors/Tools** | Name, Category (Select), Owner, Cost (Number), Renewal (Date), Contract (Files), Security Review (Checkbox) | Table sorted by Renewal, Renewals this Quarter |
| **People Directory** | Name, Team (Select), Role, Manager (Person), Start Date, Location, Bio, Links (URL) | Directory (table), New joiners (start date this month) |

## 3) Page layout recommendations

### Home (Command Center)
- Add a **hero** section with mission + current quarter theme.
- Insert linked views:
  - "This week" tasks filtered to current week.
  - "Active projects" board by Status.
  - "Top OKRs" filtered to in-flight cycles.
- Add a **Quick Actions** callout: "Start new project", "Log decision", "Book retro", "Submit vendor request" (each links to a template button).

### Projects & Delivery
- Place the **Projects** board (grouped by Status) at the top.
- Add a **Project intake template button** that duplicates a pre-styled project page with sections for Brief, Risks, Milestones, and Links.
- Create a **Tasks** board filtered by the current sprint and grouped by Status.
- Add a **Docs** linked database filtered to the selected project.
- Pin a **Retros & Learnings** section where retro notes are tagged and summarized.

### People & Operations
- Start with the **People Directory** table and a "New hire checklist" toggle list.
- Add a **Vendors/Tools** table with renewal reminders and a relation to security reviews.
- Create a **Policies & How-tos** list (simple toggles) linking to onboarding, PTO, security, and procurement guides.

### Revenue & Finance
- Add a **CRM Deals** board grouped by Stage with a "Forecast" table sorted by Close Date.
- Create a **Pipeline health** callout that shows next steps on deals with Probability < 0.6.
- Add a **Finance dashboard** section with quick links to burn, runway, and invoices (these can be embeds or linked databases if you store them in Notion).

## 4) Templates to wire up
Implement template buttons or database templates for repeatable work:

- **Project brief** (in Projects): Summary, Goals, Metrics, Scope, Risks, Dependencies, Timeline, Stakeholders, Links.
- **Sprint**: Goal, Capacity, Planned commits (Relation → Projects), Retro notes, Demos, Outcomes.
- **Meeting notes**: Agenda, Attendees, Decisions (Relation → Docs with Type = Decision), Actions (Relation → Tasks).
- **Retro**: What went well, What to improve, Actions (Relation → Tasks), Owner, Due.
- **Deal review**: ICP fit, Pain, Champion, Competition, Next step, Mutual close plan.
- **Security review**: Vendor, Data handled, Risk level, Owner, Renewal date, Decision.

## 5) Automation ideas (native to Notion)
- **Status rollups**: In Projects, add a rollup of linked Tasks to compute % done.
- **Overdue alerts**: Create a view that filters Tasks where Due < Today AND Status is not Done; pin it on Home.
- **Intake routing**: Add a "Submission Type" select in Docs (Spec/Decision/Retro) and default Status to "Review" to keep intake tidy.
- **Lightweight approvals**: Use a "Needs review" checkbox + person property to ping reviewers via comments.

## 6) Permissions and governance
- Keep **Actionuity HQ** open to the org, but lock the database schemas to avoid accidental edits.
- Create a **Founders & Leads** group with edit rights on OKRs, Finance, and CRM; make other teams comment-only on sensitive views.
- Add **page rules** explaining naming conventions (e.g., `2024-09-12 – Meeting – Partner Sync`).

## 7) Onboarding checklist
1. Invite teammates and group them (Product, Eng, GTM, Ops).
2. Publish the **How to use this HQ** page and pin it to Home.
3. Seed example entries: one project, five tasks, one sprint, two OKRs, two docs, one deal.
4. Test template buttons and relations; confirm rollups and default filters.
5. Record a 5-minute Loom walking through the HQ.
6. Schedule a monthly housekeeping slot to archive stale projects and close loops on tasks and retros.

## 8) Visual polish (optional)
- Use the provided icon set for databases (Projects, Tasks, Docs, CRM, Finance) to keep navigation consistent.
- Add a **dark/light-friendly** color palette for callouts: green for success, yellow for risks, red for blockers, grey for neutral info.
- Keep page widths at "Full width" for boards and calendars; use "Layout: Small text" for documentation-heavy pages.

## 9) Export/backup tips
- Enable **automated exports** (Settings → Export content) on a monthly cadence if governance requires it.
- For critical databases (Projects, Tasks, CRM), export CSV snapshots quarterly and store them in your data room.

---
With these steps, you can stand up Actionuity's Notion HQ quickly in the actual Notion app, while keeping it maintainable as the team grows.
