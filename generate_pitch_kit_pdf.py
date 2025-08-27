from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
import os

# File path (Windows style, saved to user's Documents)
pdf_path = os.path.expanduser(r"~/Documents/RainCheck_GreenBid_Pitch_Kit.pdf")

# Styles
styles = getSampleStyleSheet()
title_style = styles["Title"]
heading_style = styles["Heading2"]
body_style = styles["BodyText"]

# Content
content = []

# Title
content.append(Paragraph("RainCheck + GreenBid Bootcamp Pitch Kit", title_style))
content.append(Spacer(1, 12))

# Final 3-min Script
content.append(Paragraph("Final 3-Minute Pitch Script", heading_style))
script = """
HOOK (0:00–0:30)
Every year, over $100M in clean energy contracts in D.C. slip past small, minority-owned contractors—not because they can’t do the work, but because their bids aren’t compliant or fundable. I’m Terrance Ellerbe, founder of Actionuity, and we’re here to fix that.

PROBLEM (0:30–1:00)
Certified Business Enterprises—CBEs—are losing opportunities to transform our city. They face mountains of forms, non-compliance rejections, and no real path to financing. Without change, we’ll keep locking out the very businesses D.C. has pledged to uplift.

SOLUTION (1:00–1:30)
Our solution is twofold: GreenBid Bootcamp—a weekend accelerator that makes CBEs bid-ready with compliant cost models and capability statements. And RainCheck—a first-of-its-kind platform that turns those same businesses into fundable, stock-like assets using automation.

MODEL (1:30–2:15)
Bootcamps generate revenue through cohort fees, templates, and partnerships. RainCheck monetizes by creating liquidity—entrepreneurs and investors can buy into or trade ownership in these fundable businesses. Together, it’s a pipeline: bids won, contracts executed, capital secured.

CLOSE (2:15–3:00)
D.C.’s clean energy economy should be built by the businesses rooted here. With GreenBid and RainCheck, we’re not just fixing bids—we’re building wealth and opportunity. Together, we can turn overlooked firms into investable assets, and ensure the future is built by those who call this city home.
"""
content.append(Paragraph(script, body_style))
content.append(Spacer(1, 12))

# Objection Handling
content.append(Paragraph("Objection Handling (Top 5)", heading_style))
objections = [
    "Isn’t this just training? → The Bootcamp is just the start. RainCheck ensures each firm doesn’t just learn—they become a fundable, investable business.",
    "How do you scale? → Each Bootcamp trains 25 firms per cohort, four cohorts per year. RainCheck is fully digital and scalable across cities with procurement ecosystems.",
    "Where’s the proof? → Actionuity has already won clean energy contracts and guided CBEs through procurement compliance. We’re now packaging that playbook into a repeatable Bootcamp.",
    "Who pays for this? → Revenue comes from a mix of CBE bootcamp fees, government partnerships, and RainCheck’s transaction fees in the business marketplace.",
    "Why now? → D.C. is committing billions to clean energy upgrades. Equity mandates mean CBEs are meant to benefit. Without this, they’ll miss out again."
]
content.append(ListFlowable([ListItem(Paragraph(obj, body_style)) for obj in objections]))
content.append(Spacer(1, 12))

# Follow-Up
content.append(Paragraph("Follow-Up Sequence", heading_style))
followup = """
EMAIL 1 (Same-Day Thank You)
Subject: Thank you for your time at [Pitch Competition]
Body: Thank you for hearing our pitch today. With GreenBid Bootcamp and RainCheck, we’re closing a $100M gap for CBEs in D.C.’s clean energy economy. I’d love to schedule 20 minutes to share how you or your organization could partner with us. Are you available next week?

EMAIL 2 (48 Hours Later)
Subject: Following up on RainCheck + GreenBid
Body: I wanted to follow up on our conversation. We’re preparing our next Bootcamp cohort and building the RainCheck platform. Your support—whether as a partner, sponsor, or advisor—would help accelerate this mission. Let’s connect.

MEETING CLOSE SCRIPT
Before we wrap, I’d like to ask: how would you like to be involved—supporting our next cohort, piloting RainCheck with your network, or discussing investment opportunities?
"""
content.append(Paragraph(followup, body_style))

# Build PDF
doc = SimpleDocTemplate(pdf_path, pagesize=letter)
doc.build(content)

print(f"PDF generated at: {pdf_path}")
