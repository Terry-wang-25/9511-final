# -*- coding: utf-8 -*-
"""Build claim-wizard-topics.js — per-topic Q1/Q2 for claim wizard step 1."""
from __future__ import annotations

import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent


def wf_title(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    m = re.search(r'<h1 id="wf-page-title">(.*?)</h1>', raw, re.DOTALL)
    if not m:
        return path.stem
    return re.sub(r"\s+", " ", m.group(1).strip())


def pair_for(slug: str, title: str) -> tuple[str, list[str], str, list[str]]:
    cat, *rest = slug.split("-")
    tail = "-".join(rest)

    def P(q1: str, o1: list[str], q2: str, o2: list[str]):
        return q1, o1, q2, o2

    if cat == "faulty":
        if "digital" in tail:
            return P(
                "Where did you purchase or subscribe?",
                ["App Store (Apple)", "Google Play", "PC/console game store", "SaaS / website direct", "Other"],
                "What best describes the problem?",
                ["Software crashes or errors", "Not as described / missing features", "Charged after cancellation", "Account or licence locked", "Other"],
            )
        if "unsafe" in tail or "recall" in tail:
            return P(
                "Product safety situation",
                ["Official recall announced", "Unsafe but no recall yet", "Injury or near miss", "Reporting only / concerned"],
                "Do you still have the product?",
                ["Yes — can provide photos/serial", "Stopped using and disposed", "Returned to store", "Other"],
            )
        if "major" in tail:
            return P(
                "Type of goods or service",
                ["Physical product", "In-home or personal service", "Online-delivered service", "Mixed"],
                "Why do you believe the failure is “major”?",
                ["Unsafe or risk of harm", "Would not have bought if known", "Cannot use for normal purpose", "Other serious failure"],
            )
        if "statutory" in tail or "guarantee" in tail:
            return P(
                "Which guarantee area applies most?",
                ["Acceptable quality", "Fit for purpose", "Matches description", "Repairs / spare parts", "Other"],
                "Purchase or hire timeframe",
                ["Under 6 months", "6–12 months", "12–24 months", "More than 24 months / unsure"],
            )
        if "repair" in tail:
            return P(
                "Repair status with the business",
                ["Waiting for repair", "Repair took too long", "Repair refused", "Recurring fault after repair", "Other"],
                "Documentation you hold",
                ["Written repair quote", "Emails only", "Photos/video", "No written record yet"],
            )
        return P(
            "Goods or service category",
            ["Electronics / appliances", "Vehicle-related", "Clothing / household", "Service contract", "Other"],
            "Main statutory issue",
            ["Defective quality", "Not as described", "Not fit for purpose", "Other"],
        )

    if cat == "refunds":
        return P(
            "What outcome are you seeking?",
            ["Full refund", "Partial refund", "Replacement", "Repair first then refund if fails", "Unsure"],
            "Where are you in the dispute?",
            ["Business has not responded", "Offered repair only — you want refund", "Refund offered but delayed", "Other"],
        )

    if cat == "misleading":
        return P(
            "What kind of pricing or advertising issue?",
            ["Drip / hidden fees", "“Was/now” or discount claims", "Bait advertising / stock excuse", "Fake reviews / endorsements", "Fine print / buried terms"],
            "Where did you see the representation?",
            ["Website / app", "In-store shelf or poster", "Email or SMS", "Phone sale", "Other"],
        )

    if cat == "contracts":
        return P(
            "Contract context",
            ["Door-to-door or unsolicited sale", "Online subscription", "Utilities / telco", "Bundled add-ons", "Early exit fee"],
            "What do you want to challenge?",
            ["Unfair term wording", "Cooling-off cancellation", "Auto-renewal disclosure", "Exit fee amount", "Other"],
        )

    if cat == "tenancy":
        return P(
            "Tenancy issue type",
            ["Bond refund / deductions", "Condition report / photos", "Repairs", "Rent increase notice", "Breaking lease"],
            "Your role",
            ["Tenant", "Co-tenant", "Representing someone else", "Other"],
        )

    if cat == "scams":
        return P(
            "Scam or harm type",
            ["Online shopping / fake seller", "Phishing / impersonation", "Pyramid / investment scheme", "Recovery scam", "Unsafe product + fraud"],
            "Money or data lost?",
            ["Money sent — some or all", "Personal details disclosed", "No loss yet — suspicious contact", "Other"],
        )

    if cat == "doorstep":
        return P(
            "Sales channel involved",
            ["Door-to-door visit", "Telemarketing call", "Energy / telco switch offer", "Cooling-off cancellation proof", "Permits / ID concern"],
            "Contract signed?",
            ["Signed — within cooling-off", "Signed — cooling-off passed", "Did not sign", "Unsure"],
        )

    if cat == "billing":
        return P(
            "Billing dispute type",
            ["Wrong line items / tariff", "Utilities / telco complaint path", "Backbilling / catch-up bill", "Hardship / payment plan", "Exit or early termination fee"],
            "Largest concern",
            ["Amount is wrong", "Notice was inadequate", "Harassment or disconnection threat", "Other"],
        )

    if cat == "complaints":
        return P(
            "Stage of your complaint",
            ["Drafting first complaint", "Gathering evidence / timeline", "Internal escalation", "External scheme / ombudsman", "Tribunal or court consideration"],
            "Desired next step from us",
            ["Template or checklist help", "Referral information", "Case triage only", "Other"],
        )

    return P(
        "How does this relate to your issue?",
        ["Matches this topic closely", "Related but broader", "Multiple issues", "Unsure"],
        "Urgency",
        ["Need response within days", "Within a few weeks", "No fixed deadline"],
    )


def main() -> None:
    topics: dict[str, dict] = {}
    for wf in sorted(BASE.glob("workflow-*.html")):
        slug = wf.name.removeprefix("workflow-").removesuffix(".html")
        title = wf_title(wf)
        q1, o1, q2, o2 = pair_for(slug, title)
        topics[slug] = {
            "title": title,
            "q1": {"legend": q1, "options": o1},
            "q2": {"legend": q2, "options": o2},
        }

    topics["general"] = {
        "title": "General complaint",
        "q1": {
            "legend": "What type of case are you filing?",
            "options": [
                "Real estate (e.g. rental, purchase)",
                "Consumer protection (goods, services, advertising)",
                "Employment (e.g. wages, dismissal)",
                "Other",
            ],
        },
        "q2": {
            "legend": "Which area is closest?",
            "options": ["Faulty or unsafe goods/services", "Refunds or contracts", "Scams or pressure sales", "Billing or complaints process", "Not sure"],
        },
    }

    out_path = BASE / "claim-wizard-topics.js"
    payload = json.dumps(topics, ensure_ascii=False, indent=2)
    out_path.write_text(
        "/* Auto-generated by _build_claim_wizard_topics.py — do not edit by hand; re-run script. */\n"
        "window.CLAIM_WIZARD_TOPICS = "
        + payload
        + ";\n",
        encoding="utf-8",
        newline="\n",
    )
    print("Wrote", out_path.name, "keys:", len(topics))


if __name__ == "__main__":
    main()
