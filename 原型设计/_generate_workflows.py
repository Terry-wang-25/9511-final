# -*- coding: utf-8 -*-
"""Generates one HTML file per workflow topic (workflow-{slug}-{stem}.html)."""
from __future__ import annotations

import html
from pathlib import Path

BASE = Path(__file__).resolve().parent


def load_header_shell() -> str:
    lines = (BASE / "consumer-issue-faulty.html").read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[:69])


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def steps_ol(items: list[tuple[str, str]]) -> str:
    parts = ['<ol class="la-workflow-steps">']
    for title, body in items:
        parts.append(
            "<li>"
            f'<p class="la-workflow-step-title">{esc(title)}</p>'
            f'<p class="la-workflow-step-body">{esc(body)}</p>'
            "</li>"
        )
    parts.append("</ol>")
    return "\n".join(parts)


def actions(claim_slug: str) -> str:
    wizard_href = f"任务 1 的第二个页面.html?topic={claim_slug}"
    return (
        '<div class="la-workflow-actions la-workflow-actions--dual">'
        "<span>What would you like to do?</span>"
        f'<a class="la-btn-maroon" href="{esc(wizard_href)}">Submit a claim <span aria-hidden="true">›</span></a>'
        '<a class="la-btn-teal" href="Contact.html">Contact for support <span aria-hidden="true">›</span></a>'
        "</div>"
    )


def wf_stem(anchor: str) -> str:
    if not anchor.startswith("wf-"):
        raise ValueError(f"anchor must start with wf-: {anchor!r}")
    return anchor[3:]


def standalone_article(anchor: str, when: str, step_items: list[tuple[str, str]], claim_slug: str) -> str:
    """Single-topic page: title lives in banner h1; card is steps + actions only."""
    return (
        f'<article id="{esc(anchor)}" class="la-workflow-card la-workflow-card--standalone">'
        f'<p class="la-workflow-when"><strong>When to use this path:</strong> {esc(when)}</p>'
        f"{steps_ol(step_items)}"
        f"{actions(claim_slug)}"
        "</article>"
    )


def merge_shell(doc_title: str) -> str:
    shell = load_header_shell()
    shell = shell.replace(
        "<body class=\"subpage subpage-header-la\">",
        "<body class=\"subpage subpage-header-la la-workflow-page\">",
        1,
    )
    out_lines: list[str] = []
    for line in shell.splitlines():
        if line.strip().startswith("<title>"):
            out_lines.append(f"  <title>{esc(doc_title)}</title>")
        else:
            out_lines.append(line)
    return "\n".join(out_lines)


def build_single_page(
    *,
    doc_title: str,
    h1: str,
    lead: str,
    back_href: str,
    back_label: str,
    article_html: str,
) -> str:
    shell = merge_shell(doc_title)
    main = f"""  <main id="main-content">
    <section class="la-workflow-banner" aria-labelledby="wf-page-title">
      <div class="container">
        <h1 id="wf-page-title">{esc(h1)}</h1>
        <p class="la-workflow-banner-lead">{esc(lead)}</p>
      </div>
    </section>
    <div class="la-workflow-wrap">
      <p class="la-workflow-back"><a href="{esc(back_href)}">← {esc(back_label)}</a></p>
{article_html}
    </div>
  </main>

<script src="site-preferences.js"></script>
</body>
</html>
"""
    return shell + "\n" + main


# --- Page definitions: (anchor, heading, when, steps) x5 ---

PAGES: list[dict] = [
    {
        "slug": "faulty",
        "back_href": "consumer-issue-faulty.html",
        "back_label": "Back to faulty goods overview",
        "from_key": "faulty",
        "blocks": [
            (
                "wf-statutory-guarantees",
                "Statutory guarantees and consumer guarantees",
                "You bought goods or paid for a service and want to know if the law already promises a minimum standard (quality, match with description, fitness for purpose).",
                [
                    ("Confirm what you paid for", "Write down the product or service, date, price, and what the ad, label or contract said it would do."),
                    ("Separate “change of mind” from a fault", "If the item is unsafe, broken, does not work as described or is not fit for what you told the seller you needed, note that as a consumer-law issue—not a store policy preference."),
                    ("Gather quick proof", "Photos or video of the fault, packaging, model numbers, and any messages where you described your needs to the business."),
                    ("Contact the seller in one channel", "Email or the official complaints form: state what you bought, what went wrong, what outcome you want (repair, replacement or refund), and a clear deadline for reply."),
                    ("Keep a dated record", "Save a copy of your message and any reply. You will need this if you escalate or use the checker."),
                ],
            ),
            (
                "wf-major-failures",
                "Major failures and remedies",
                "The problem is serious (unsafe, cannot be fixed, or very different from what you agreed) and you want to know if you can refuse a repair-only offer.",
                [
                    ("Describe severity in plain words", "Ask: Would a reasonable person have bought it knowing this? Is it unsafe? Can it be made acceptable within a reasonable time?"),
                    ("List failed repair attempts", "If they already tried to fix it more than once or the fix took too long, note dates and what was done."),
                    ("State your preferred remedy", "In writing, say whether you want a refund, replacement or compensation—and quote that your issue may be a major failure under consumer guarantees."),
                    ("Set a response deadline", "Give at least a few business days for a written answer before you escalate to a dispute body or regulator."),
                    ("Do not dispose of the item yet", "Unless it is unsafe to keep, retain the goods and packaging until the dispute is resolved or you are told otherwise."),
                ],
            ),
            (
                "wf-repairs-timelines",
                "Repairs, timelines and spare parts",
                "The business agreed to repair but is delaying, gave no date, or you need spare parts for something still under consumer guarantees.",
                [
                    ("Ask for a written repair plan", "Request an estimated start date, finish date, and whether parts are on order."),
                    ("Define “reasonable” for your case", "Consider product type, how you use it, and whether you are without essential use (for example a fridge or phone needed for work)."),
                    ("Follow up in writing", "If the date passes, send a short follow-up that repeats your request and sets a new deadline."),
                    ("Escalate inside the company", "Ask for the complaints or escalations team and include prior reference numbers."),
                    ("Prepare next-tier options", "Identify your industry ombudsman or fair trading line while you wait—so you can act immediately if the deadline is missed again."),
                ],
            ),
            (
                "wf-unsafe-recalls",
                "Unsafe products and recalls",
                "You suspect the product is dangerous, injured someone, or you heard about a recall.",
                [
                    ("Stop using it if there is injury risk", "Unplug, isolate or store safely; do not attempt DIY repairs on electrical or gas items."),
                    ("Search official recall lists", "Look up the brand, model and batch on government recall or product-safety pages and the manufacturer site."),
                    ("Notify the seller and manufacturer", "Report the hazard with photos, serial numbers and where you bought it; ask for safe disposal or remedy instructions."),
                    ("Report to regulators", "Use the official injury or unsafe-goods reporting channels with the same evidence."),
                    ("Preserve evidence", "Keep the item (if safe), packaging, receipts and medical records if someone was hurt."),
                ],
            ),
            (
                "wf-digital-goods",
                "Digital goods, apps and downloads",
                "Paid software, app, game, subscription or download is defective, locked, not as described or keeps billing after cancel.",
                [
                    ("List accounts and charges", "Screenshots of app store or bank charges, subscription ID, email on the account, and the advertised features."),
                    ("Try the official refund or dispute path first", "Use the platform’s purchase history and report a problem within their stated window."),
                    ("Cancel auto-renew correctly", "Turn off renewal in account settings and keep a screenshot showing the cancellation time."),
                    ("Email the trader with facts", "State version, device, error messages, and what you expected versus what you received."),
                    ("Chargeback only after documented attempts", "If payment was card-based and the seller refuses, ask your bank about chargeback rules with your paper trail ready."),
                ],
            ),
        ],
    },
    {
        "slug": "refunds",
        "back_href": "consumer-issue-refunds.html",
        "back_label": "Back to refunds overview",
        "from_key": "refunds",
        "blocks": [
            (
                "wf-refund-entitlement",
                "When you are entitled to a refund",
                "You want money back and need to know if it is a voluntary store policy or something you can insist on.",
                [
                    ("Clarify your reason", "Label it: change of mind, faulty, not as described, service not delivered, or cooling-off/cancellation right."),
                    ("Read the receipt and signage", "Note posted refund signs and any “no refund” wording—consumer guarantees may still apply for faults."),
                    ("Collect proof of payment", "Receipt, tax invoice, bank or card statement showing merchant name and amount."),
                    ("Write one clear request", "State facts, dates, what you want (refund amount), and a reply deadline."),
                    ("If refused, escalate with evidence", "Reply referencing your prior message and attach the same proof packet."),
                ],
            ),
            (
                "wf-repair-or-replace",
                "Repair or replace first?",
                "The business insists on repair first; you believe replacement or refund is fair.",
                [
                    ("Ask why repair is offered", "Get the reason in writing (cost, parts availability, minor fault claim)."),
                    ("Check proportionality", "If repair means long downtime, repeat failures, or cannot fix the core problem, say so plainly."),
                    ("Request a timetable", "Ask for start date, completion date, and loan or substitute if it is essential goods."),
                    ("Reply if repair fails or drags", "State the repair failed or missed the deadline and restate the remedy you want now."),
                    ("Log every interaction", "Dates, names, reference numbers."),
                ],
            ),
            (
                "wf-proof-purchase",
                "Proof of purchase and evidence",
                "The trader says they have no record of your purchase or disputes the amount.",
                [
                    ("Pull all payment trails", "Bank/card export, PayPal or wallet receipt, BNPL confirmation, gift card redemption."),
                    ("Gather indirect proof", "Warranty registration, serial number photos, delivery tracking, loyalty app history."),
                    ("Order a timeline", "One page: date of purchase, date fault noticed, each contact with the business."),
                    ("Send a single indexed bundle", "Numbered attachments (Photo 1, Statement 2) in your email."),
                    ("Ask them to identify what they dispute", "Request specifically which facts or amounts they reject."),
                ],
            ),
            (
                "wf-layby-deposits",
                "Lay-bys and deposits",
                "Lay-by was cancelled, or a deposit was kept, and you disagree with the amount retained or the reason.",
                [
                    ("Locate the lay-by agreement", "Terms on receipt, contract, or docket showing deposit, schedule and cancellation rules."),
                    ("Calculate what you paid vs what was deducted", "Write the arithmetic the business should be able to verify."),
                    ("Request a written breakdown", "Ask for itemised fees and how they comply with the agreement and law."),
                    ("Dispute in writing", "If the deduction looks unfair, state why and the refund you expect."),
                    ("Keep goods or documents until resolved", "Do not sign releases you do not understand."),
                ],
            ),
            (
                "wf-extended-warranties",
                "Extended warranties and store policies",
                "You are offered an extra paid warranty and want to compare it to free consumer protections.",
                [
                    ("List what the paid plan adds", "Copy coverage, exclusions, claim caps, and who underwrites it."),
                    ("Compare to consumer guarantees", "Ask which problems are already covered without paying extra."),
                    ("Check overlap with home insurance", "Some risks may already be covered elsewhere."),
                    ("Sleep on it", "Do not buy under pressure at checkout; request the brochure and a copy to read at home."),
                    ("If you already bought, read cooling-off", "See if you can cancel the add-on within any statutory cooling-off for unsolicited or linked sales."),
                ],
            ),
        ],
    },
    {
        "slug": "misleading",
        "back_href": "consumer-issue-misleading.html",
        "back_label": "Back to misleading conduct overview",
        "from_key": "misleading",
        "blocks": [
            (
                "wf-drip-pricing",
                "Drip pricing and hidden fees",
                "Advertised price was low but mandatory fees appeared late or at checkout.",
                [
                    ("Screenshot the journey", "Capture each step from ad to cart to payment page with timestamps if possible."),
                    ("Highlight mandatory vs optional fees", "Circle fees you could not avoid to get the advertised good or service."),
                    ("Compare to what was stated upfront", "Note any “from” price that did not include unavoidable charges."),
                    ("Complain to the trader first", "Ask for the total price you should have been shown and any adjustment."),
                    ("Report patterns", "If widespread, note other examples for a regulator report."),
                ],
            ),
            (
                "wf-was-now",
                "“Was/now” pricing and discounts",
                "You doubt the “was” price or the urgency of a limited-time sale.",
                [
                    ("Save the ad", "Photo, URL, catalogue page, or email with date."),
                    ("Check prior prices", "Search archived pages or older catalogues if available."),
                    ("Ask the business for evidence", "Request how long the higher price applied before the sale."),
                    ("Compare competitors", "Note similar items elsewhere for context."),
                    ("Write a concise allegation", "Two sentences: what was claimed, why you believe it was misleading."),
                ],
            ),
            (
                "wf-bait-advertising",
                "Bait advertising and stock excuses",
                "A special was advertised but staff pushed a dearer model or said “out of stock”.",
                [
                    ("Record what was advertised", "Store flyer, online banner, or audio if from radio/TV."),
                    ("Record what happened in store", "Time, location, staff name if known, what you were told."),
                    ("Ask for rain-check or equivalent", "Request honouring the deal, comparable substitute at same terms, or written refusal reason."),
                    ("Escalate to head office", "Send your evidence packet with a clear remedy."),
                    ("Note systemic baiting", "If many consumers report the same, that strengthens a regulator referral."),
                ],
            ),
            (
                "wf-fake-reviews",
                "Comparisons and fake reviews",
                "Star ratings, testimonials or comparisons look manipulated or untrue.",
                [
                    ("Capture the claim", "Screenshots of reviews, influencer posts, or comparison tables."),
                    ("Check disclosure", "See if paid partnerships or gifts are labelled as required."),
                    ("Search review patterns", "Sudden spikes, duplicate wording, or only five-star clusters."),
                    ("Report platform abuse", "Use the platform’s reporting tool for fake reviews."),
                    ("Complain to the advertiser", "Ask them to substantiate or remove misleading endorsements."),
                ],
            ),
            (
                "wf-fine-print",
                "Fine print and important terms",
                "A critical condition was buried while marketing highlighted only benefits.",
                [
                    ("Mark what was prominent in marketing", "Headlines, pop-ups, or sales pitch notes."),
                    ("Locate the buried term", "Page, clause number, or checkbox text."),
                    ("Explain why it matters", "Fees, auto-renewal, non-refundable deposits, or limits that change the deal."),
                    ("Request plain-language confirmation", "Ask the business to confirm in email how the term applies to you."),
                    ("Seek cancellation or variation", "If the term was not fairly drawn to your attention, say you dispute fairness and want a fair outcome."),
                ],
            ),
        ],
    },
    {
        "slug": "contracts",
        "back_href": "consumer-issue-contracts.html",
        "back_label": "Back to contracts overview",
        "from_key": "contracts",
        "blocks": [
            (
                "wf-unfair-terms",
                "Unfair contract terms",
                "A clause feels one-sided (penalties, unilateral changes, broad liability exclusions).",
                [
                    ("Extract the clause", "Quote it exactly with section number."),
                    ("Identify the imbalance", "Who bears risk, cost, or decision power?"),
                    ("Check standard-form context", "Was it take-it-or-leave-it with no negotiation?"),
                    ("Write a challenge letter", "State why the term may be unfair or void and what outcome you want."),
                    ("Send to the right address", "Legal or complaints team; keep proof of delivery."),
                ],
            ),
            (
                "wf-cooling-doorstep",
                "Cooling-off and door-to-door contracts",
                "Someone sold you something at home or unsolicited and you want to cancel within a cooling-off period.",
                [
                    ("Confirm sale type", "Door-to-door, telemarketing linked sale, or unsolicited visit rules may differ."),
                    ("Find the cooling-off end date", "From contract date or delivery—write it in your calendar."),
                    ("Use written notice", "Email or letter stating you cancel under cooling-off; keep a copy."),
                    ("Return goods if instructed", "Use tracked post and photograph condition."),
                    ("Watch for refunds", "Follow up if money is not returned within stated timelines."),
                ],
            ),
            (
                "wf-subscriptions-auto",
                "Subscriptions and auto-renewal",
                "Free trial converted, renewal was unclear, or cancellation is blocked.",
                [
                    ("Screenshot signup page", "What it said about price after trial and renewal date."),
                    ("Cancel through every channel", "App settings, web account, and email notice—keep confirmations."),
                    ("Request refund of wrongful charge", "List charge dates and why disclosure was inadequate."),
                    ("Dispute with payment provider", "If ignored, ask bank/card scheme about chargeback eligibility."),
                    ("Block future debits", "If needed, revoke direct debit authority after documented cancellation."),
                ],
            ),
            (
                "wf-bundled-addons",
                "Bundled products and add-ons",
                "You were sold extras you did not want or could not opt out fairly.",
                [
                    ("List each line item on the contract", "Separate core service from add-ons."),
                    ("State what you agreed to verbally", "Compare to what was signed."),
                    ("Request itemisation and removal", "Ask to drop unwanted components with adjusted price."),
                    ("Reject pressure bundling", "If told core service requires add-on, ask for that policy in writing."),
                    ("Escalate as misleading if misrepresented", "Attach ads and contract."),
                ],
            ),
            (
                "wf-early-exit",
                "Early termination and exit fees",
                "You want out early and the exit fee looks excessive or was not clear at signup.",
                [
                    ("Retrieve signup disclosure", "Quote what you were told about exit fees."),
                    ("Calculate fee vs remaining contract value", "Note if fee bears no relation to loss."),
                    ("Request hardship or transfer options", "Replacement customer, transfer, or payment plan."),
                    ("Negotiate in writing", "Propose a lower fee with reasons."),
                    ("Prepare external dispute", "Identify ombudsman or tribunal threshold before you pay under protest."),
                ],
            ),
        ],
    },
    {
        "slug": "tenancy",
        "back_href": "consumer-issue-tenancy.html",
        "back_label": "Back to renting overview",
        "from_key": "tenancy",
        "blocks": [
            (
                "wf-bond-refunds",
                "Bonds and bond refunds",
                "You moved out or are about to and need your bond returned or dispute a deduction.",
                [
                    ("Confirm bond authority record", "Check online bond scheme for lodged amount and parties."),
                    ("Complete exit condition process", "Final inspection request, keys handover date."),
                    ("Keep copies of rent ledger", "Show no arrears or agreed payment plan."),
                    ("Challenge unfair deductions", "Itemise each deduction against evidence (fair wear and tear)."),
                    ("Use formal bond dispute steps", "Follow your bond authority’s evidence and mediation process."),
                ],
            ),
            (
                "wf-condition-reports",
                "Condition reports and photos",
                "Start or end of lease—you need a defensible record of property condition.",
                [
                    ("Use the official form if required", "Match fields to each room and fixture."),
                    ("Photo everything dated", "Wide shots plus close-ups of existing damage."),
                    ("Send copies on time", "Return one signed copy within the deadline stated on the form."),
                    ("At exit, repeat the same angles", "Show new damage vs pre-existing."),
                    ("Store files safely", "Cloud backup plus USB."),
                ],
            ),
            (
                "wf-repairs-tenancy",
                "Urgent and non-urgent repairs",
                "Something needs fixing and the landlord or agent is slow or refuses.",
                [
                    ("Classify urgency", "Safety, security, essential services vs cosmetic."),
                    ("Notify in writing with photos", "Describe fault, risk, and access windows."),
                    ("Set reasonable follow-up dates", "Use local guides for typical response times."),
                    ("Escalate using tenancy forms", "Official notice to repair if available in your jurisdiction."),
                    ("Document health impacts", "Medical certificates if mould or heating affects health."),
                ],
            ),
            (
                "wf-rent-increases",
                "Rent increases and notices",
                "You received a rent increase and want to check notice period and grounds.",
                [
                    ("Check tenancy type and term", "Fixed vs periodic affects increases."),
                    ("Measure notice length", "Count from date received to effective date."),
                    ("Verify form of notice", "Signed, dated, required wording."),
                    ("Research local caps or freezes", "If any apply to your area or property type."),
                    ("Respond in writing", "Accept, negotiate, or dispute within the allowed window."),
                ],
            ),
            (
                "wf-breaking-lease",
                "Breaking a lease",
                "You need to leave before the end date and want to limit costs.",
                [
                    ("Read break clause and fees", "Note advertised reletting fees."),
                    ("Propose replacement tenant", "Qualified applicant ready to sign may reduce loss."),
                    ("Request hardship consideration", "Job loss, violence, or health—with evidence."),
                    ("Mitigate loss in writing", "Show steps you took to find replacement."),
                    ("Get settlement in writing", "Any agreed amount to end the lease."),
                ],
            ),
        ],
    },
    {
        "slug": "scams",
        "back_href": "consumer-issue-scams.html",
        "back_label": "Back to scams overview",
        "from_key": "scams",
        "blocks": [
            (
                "wf-online-shopping-scams",
                "Online shopping scams",
                "You paid an online seller and goods never arrived or the site vanished.",
                [
                    ("Stop further payments", "Cancel card if details were shared; revoke pending transfers if possible."),
                    ("Collect every receipt", "Order confirmation, chat logs, ads, URL screenshots."),
                    ("Contact bank or platform", "Ask chargeback, dispute, or buyer protection immediately."),
                    ("Report to cybercrime/scam agencies", "Use national reporting portals with the same evidence."),
                    ("Secure accounts", "Change passwords and enable two-factor authentication on email and shopping accounts."),
                ],
            ),
            (
                "wf-phishing",
                "Phishing and impersonation",
                "You clicked a link or gave details to someone impersonating a bank, agency or courier.",
                [
                    ("Disconnect the bait", "Do not reply; hang up if live call."),
                    ("Call official numbers only", "From the back of your card or official website—not from the message."),
                    ("Reset passwords starting with email", "Then banking, then other linked sites."),
                    ("Monitor statements", "Set alerts for 60–90 days."),
                    ("Report identity theft", "Follow government ID theft checklists if documents were taken."),
                ],
            ),
            (
                "wf-unsafe-injuries",
                "Unsafe goods and injuries",
                "Someone was hurt or nearly hurt by a product.",
                [
                    ("Seek medical help first", "Document injuries professionally."),
                    ("Preserve the product", "Do not alter it; photograph scene."),
                    ("Report to manufacturer and seller", "Demand incident reference numbers."),
                    ("Notify regulators", "Product safety and work health authorities as applicable."),
                    ("Keep a single incident file", "Medical reports, photos, receipts, communications."),
                ],
            ),
            (
                "wf-pyramid-schemes",
                "Pyramid and “investment” schemes",
                "Returns depend on recruiting or “guaranteed” high yield with pressure to recruit.",
                [
                    ("Stop recruiting or investing further", "Do not bring in friends or family."),
                    ("Map money in and promised returns", "Dates, amounts, wallets, and names used."),
                    ("Report to consumer and corporate regulators", "Use scam and misconduct reporting lines."),
                    ("Warn your bank", "If accounts were used for transfers."),
                    ("Seek independent financial advice", "From a licensed adviser not linked to the scheme."),
                ],
            ),
            (
                "wf-recovery-scams",
                "Recovery scams",
                "After a loss, someone offers to recover funds for an upfront fee.",
                [
                    ("Do not pay upfront recovery fees", "Legitimate agencies do not ask for gift cards or crypto to “unlock” money."),
                    ("Verify identity independently", "Call agencies using numbers you look up yourself."),
                    ("Block repeat contact", "Scammers share “sucker lists”."),
                    ("Report the recovery approach", "Attach messages and payment requests."),
                    ("Use only official victim support", "Government and bank fraud teams."),
                ],
            ),
        ],
    },
    {
        "slug": "doorstep",
        "back_href": "consumer-issue-doorstep.html",
        "back_label": "Back to doorstep and calls overview",
        "from_key": "doorstep",
        "blocks": [
            (
                "wf-cooling-unsolicited",
                "Cooling-off for unsolicited sales",
                "A salesperson approached you without invitation or called out of the blue selling a good or service.",
                [
                    ("Ask if the sale is unsolicited", "If yes, cooling-off rights may apply—get it in writing."),
                    ("Do not sign on the spot", "Request ID, licence numbers, and paperwork to read alone."),
                    ("Write down the exact start time of any visit", "Cooling-off clocks often run from contract date or delivery."),
                    ("Deliver cancellation in writing", "Email and letter; keep proof."),
                    ("Return any goods delivered", "Follow instructions and keep tracking."),
                ],
            ),
            (
                "wf-permits-id",
                "Permits and identification",
                "Someone at the door claims to be a tradesperson, inspector or charity.",
                [
                    ("Ask for photo ID and licence", "Note licence number and issuer."),
                    ("Verify independently", "Call the company or regulator using a number you find yourself."),
                    ("Do not allow entry without appointment", "Legitimate utilities book visits."),
                    ("Refuse high-pressure payment", "Cash, gift cards, or immediate bank transfer are red flags."),
                    ("Report impersonation", "If verification fails, contact police non-emergency and the impersonated organisation."),
                ],
            ),
            (
                "wf-telemarketing",
                "Telemarketing and call lists",
                "You get repeated sales calls or calls outside allowed hours.",
                [
                    ("Register do-not-call lists", "Use official national lists for your numbers."),
                    ("Answer once: request stop", "Note date, time, company name."),
                    ("Block and log repeat callers", "Screenshots of call logs."),
                    ("Complain to the business", "Send written cease request referencing prior calls."),
                    ("Escalate to communications regulator", "If pattern continues."),
                ],
            ),
            (
                "wf-energy-telco-marketers",
                "Energy and telco marketers",
                "Someone wants you to switch power or phone on the spot with a “today only” deal.",
                [
                    ("Never share your bill or account number first", "They can misuse it to slam-switch you."),
                    ("Compare on neutral comparison sites", "Away from the salesperson."),
                    ("Read exit fees on your current plan", "Before agreeing to switch."),
                    ("Get the offer in writing", "Rates, contract length, bundle inclusions."),
                    ("Cooling-off if signed under pressure", "Cancel within the allowed window if applicable."),
                ],
            ),
            (
                "wf-cooling-forms-proof",
                "Cooling-off forms and proof",
                "You cancelled within cooling-off and the business denies receiving notice.",
                [
                    ("Use email with read receipt or registered post", "Keep PDF of letter and postal receipt."),
                    ("Quote contract clause used", "Cooling-off section and statutory right if applicable."),
                    ("State effective cancellation date", "Clear sentence: “I cancel as of [date].”"),
                    ("Request refund timeline", "Ask when card or deposit will be credited."),
                    ("Follow up once with same attachments", "If no reply by their deadline."),
                ],
            ),
        ],
    },
    {
        "slug": "billing",
        "back_href": "consumer-issue-billing.html",
        "back_label": "Back to bills and utilities overview",
        "from_key": "billing",
        "blocks": [
            (
                "wf-bill-line-by-line",
                "Checking a bill line by line",
                "Your bill looks higher than expected or has unfamiliar charges.",
                [
                    ("Export last 12 months of bills", "PDF or CSV from your online account."),
                    ("Mark plan name, tariff and discounts", "Check they match your contract."),
                    ("Highlight duplicates or unknown codes", "Google each charge code."),
                    ("Compare meter or usage data", "If usage spiked, check for leaks or faulty appliances."),
                    ("Open a billing enquiry", "Reference each disputed line with a numbered list."),
                ],
            ),
            (
                "wf-utilities-complaints",
                "Utilities and telco complaints",
                "The provider’s response is slow or you want an external body.",
                [
                    ("Use internal complaints process", "Ask for the complaints reference number."),
                    ("Set their deadline", "Note required industry response times if known."),
                    ("Summarise in two pages max", "Facts, dates, desired outcome."),
                    ("Ask for deadlock or escalation letter", "Needed before some ombudsman schemes."),
                    ("Lodge with ombudsman if eligible", "Attach correspondence pack."),
                ],
            ),
            (
                "wf-backbilling",
                "Mistakes and backbilling",
                "The company wants a large catch-up after long undercharging or meter errors.",
                [
                    ("Request full calculation", "Meter reads, estimates, and dates of each revision."),
                    ("Check notice rules", "Note how far back they can bill in your jurisdiction or contract."),
                    ("Challenge unreasonable delay", "If you could not have known, say so with dates."),
                    ("Negotiate instalments", "Propose affordable amounts with a schedule."),
                    ("Get outcome in writing", "Before paying large sums."),
                ],
            ),
            (
                "wf-hardship-payment-plans",
                "Payment plans and hardship",
                "You cannot pay on time and want to avoid disconnection or default.",
                [
                    ("Calculate affordable weekly amount", "Based on income and essentials."),
                    ("Call hardship line in writing and phone", "Send budget summary."),
                    ("Ask for hold on enforcement", "While plan is assessed."),
                    ("Request rebates or grants", "Government energy or water relief if available."),
                    ("Keep confirmation of plan", "Payment dates and waived fees."),
                ],
            ),
            (
                "wf-exit-fees-billing",
                "Exit fees and early termination",
                "Final bill includes an exit or early termination fee you do not recognise.",
                [
                    ("Locate contract fee table", "What was disclosed at sale for early exit."),
                    ("Compare fee to disclosure", "Screenshot signup page if still online."),
                    ("Query proportionality", "Ask how fee relates to remaining months or handset subsidy."),
                    ("Dispute line on bill", "Do not pay under protest until answered if rules allow."),
                    ("Escalate to ombudsman", "If deadlock reached."),
                ],
            ),
        ],
    },
    {
        "slug": "complaints",
        "back_href": "consumer-issue-complaints.html",
        "back_label": "Back to complaints overview",
        "from_key": "complaints",
        "blocks": [
            (
                "wf-effective-complaint",
                "Writing an effective complaint",
                "You need the business to understand and fix the issue quickly.",
                [
                    ("One issue per letter", "If several problems, number them A, B, C."),
                    ("Chronology table", "Date | What happened | Who said what | Evidence ref."),
                    ("Clear ask", "Refund $X, repair by date, apology, or other measurable outcome."),
                    ("Attach index of evidence", "Annexure list matching your chronology."),
                    ("Professional tone", "No abuse—it speeds legal review if needed later."),
                ],
            ),
            (
                "wf-evidence-timelines",
                "Evidence and timelines",
                "You want your folder ready if this goes further.",
                [
                    ("Create a master folder", "Email exports PDF, photos, contracts."),
                    ("Label files YYYY-MM-DD_topic", "So anyone can sort them."),
                    ("Screenshot web pages", "Include URL bar and date visible."),
                    ("Keep a contact log", "Who you spoke to, time, reference numbers."),
                    ("Back up off-phone", "Cloud or desktop copy."),
                ],
            ),
            (
                "wf-internal-dispute",
                "Internal dispute resolution",
                "You are moving up inside the company after first-line support failed.",
                [
                    ("Ask for complaints or escalations team", "Do not repeat the whole story—add 'see prior ref #'."),
                    ("Set review deadline", "Reasonable business days based on complexity."),
                    ("Request senior written response", "Not only phone promises."),
                    ("Cite prior broken promises", "Quote dates."),
                    ("State next step", "Ombudsman, regulator, or tribunal if unresolved."),
                ],
            ),
            (
                "wf-external-schemes",
                "External dispute schemes",
                "Internal process finished or timed out; you want a free external scheme.",
                [
                    ("Check scheme eligibility", "Industry, dollar caps, and membership."),
                    ("Gather pack", "Complaint letter, replies, key evidence under 10 MB if uploading."),
                    ("Complete scheme form accurately", "Match dates to your chronology."),
                    ("Cooperate with requests", "Extra documents on time."),
                    ("Note limitation periods", "Do not miss tribunal time limits while waiting."),
                ],
            ),
            (
                "wf-tribunal-court",
                "Going to a tribunal or court",
                "You consider small claims or tribunal for a consumer dispute.",
                [
                    ("Check monetary limits", "Tribunal vs court thresholds."),
                    ("Cost-benefit", "Filing fees, time off work, and enforceability."),
                    ("Self-help legal information only", "Use official court information services—not unverified forums."),
                    ("Draft originating application", "Facts, law you rely on (general), relief sought."),
                    ("Serve correctly", "Follow rules so the case is not dismissed on technicality."),
                ],
            ),
        ],
    },
]


def main() -> None:
    combined = [
        "workflow-faulty.html",
        "workflow-refunds.html",
        "workflow-misleading.html",
        "workflow-contracts.html",
        "workflow-tenancy.html",
        "workflow-scams.html",
        "workflow-doorstep.html",
        "workflow-billing.html",
        "workflow-complaints.html",
    ]
    for name in combined:
        p = BASE / name
        if p.is_file():
            p.unlink()
            print("Removed old", name)

    for page in PAGES:
        slug = page["slug"]
        fk = page["from_key"]
        for anchor, h2, when, steps in page["blocks"]:
            stem = wf_stem(anchor)
            filename = f"workflow-{slug}-{stem}.html"
            doc_title = f"{h2} — Consumer Rights"
            lead = "Follow the numbered steps in order, then choose whether to submit a claim or contact support."
            claim_slug = f"{slug}-{stem}"
            art = standalone_article(anchor, when, steps, claim_slug)
            html_out = build_single_page(
                doc_title=doc_title,
                h1=h2,
                lead=lead,
                back_href=page["back_href"],
                back_label=page["back_label"],
                article_html=f"      {art}\n",
            )
            (BASE / filename).write_text(html_out, encoding="utf-8", newline="\n")
            print("Wrote", filename)


if __name__ == "__main__":
    main()
