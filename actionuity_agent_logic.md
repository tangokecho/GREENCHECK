# ⚡ Actionuity Agent Logic – Procurement-to-Performance System

## Overview
The Actionuity agent turns contractor readiness into a repeatable execution workflow for clean energy and public-sector opportunities. It helps users qualify, prepare, submit, and track compliant bids while preserving evidence for financing and growth.

---

## 🎯 Core Functions

### 1. `intake_contractor_profile(input_data)`
- Captures company profile, certifications, NAICS, labor capacity, and service geography.
- Generates a readiness baseline and missing-doc checklist.

### 2. `compliance_readiness_audit(profile)`
- Validates procurement requirements (CBE/DBE status, OSHA, COI, First Source, Disclosure 33, licensing).
- Returns pass/fail by requirement with remediation actions and due dates.

### 3. `opportunity_match_engine(profile, opportunity_feed)`
- Scores opportunities by fit (scope alignment, margin potential, timeline feasibility, compliance burden).
- Prioritizes high-probability targets and flags red-risk opportunities.

### 4. `build_bid_packet(profile, target_rfp)`
- Produces submission-ready packet components:
  - capability statement variants
  - technical response draft
  - cost narrative + pricing assumptions
  - compliance attachment index
- Enforces LPTA/compliance formatting rules for target agency templates.

### 5. `execution_tracker(contract_award)`
- Tracks milestones from notice-to-proceed through closeout.
- Logs deliverables, change orders, invoices, and proof-of-performance artifacts.
- Maintains an audit trail that can be reused for future bids and underwriting.

### 6. `performance_to_fundability_loop(history)`
- Converts completed work history into improved fundability signals.
- Recalculates internal score based on win rate, cycle time, gross margin, and compliance quality.

---

## 🛠 Supported Inputs
```json
{
  "user": {
    "name": "Terrance Ellerbe",
    "organization": "Actionuity",
    "entity_type": "LLC",
    "location": "Washington, DC",
    "sector": "Clean Energy Contracting",
    "certifications": ["CBE", "MBE"]
  },
  "documents": {
    "capability_statement": "capability_statement.pdf",
    "insurance": "certificate_of_insurance.pdf",
    "past_performance": ["contract_001.pdf", "contract_002.pdf"],
    "pricing_model": "cost_model.xlsx"
  },
  "targets": {
    "agencies": ["DCSEU", "DOEE", "GSA"],
    "contract_types": ["Energy retrofit", "Weatherization", "Compliance support"]
  }
}
```

---

## ✅ Expected Outputs
- Readiness score + remediation plan
- Ranked opportunity list with rationale
- Submission-ready bid packet components
- Post-award execution log and performance summary
- Updated fundability profile for next-cycle growth
