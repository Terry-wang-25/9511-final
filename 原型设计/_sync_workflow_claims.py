# -*- coding: utf-8 -*-
"""Replace workflow 'Next steps' (checker/track/contact) with Submit a claim + Contact;
   generate one tailored claim-*.html per workflow topic."""
from __future__ import annotations

import html
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent

OLD_ACTIONS = re.compile(
    r'<div class="la-workflow-actions"><span>Next steps</span>'
    r'<a class="la-btn-maroon" href="Check My Rights - Page 1\.html\?from=[^"]+">Continue in step-by-step checker <span aria-hidden="true">›</span></a>'
    r'<a class="la-btn-teal" href="Case Tracker\.html">Track your case <span aria-hidden="true">›</span></a>'
    r'<a class="la-btn-maroon" href="Contact\.html">Contact for support <span aria-hidden="true">›</span></a>'
    r"</div>",
    re.DOTALL,
)

LEAD_OLD = "Follow the numbered steps in order, then use Next steps when you are ready."
LEAD_NEW = "Follow the numbered steps in order, then choose whether to submit a claim or contact support."


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def load_header_shell() -> str:
    lines = (BASE / "consumer-issue-faulty.html").read_text(encoding="utf-8").splitlines()
    return "\n".join(lines[:69])


def topic_pack(suffix: str) -> dict[str, str | list[str]]:
    """Tailored copy per workflow stem (e.g. faulty-digital-goods)."""
    parts = suffix.split("-")
    cat = parts[0]

    # Shared bullets by broad category
    cat_bullets: dict[str, list[str]] = {
        "faulty": [
            "What you bought or booked, and the date of purchase or service",
            "How the item or service failed (quality, description, fitness for purpose)",
            "Repairs, refunds or responses already offered by the business",
        ],
        "refunds": [
            "What you paid and how (card, transfer, cash, BNPL)",
            "The remedy you want (refund, repair, replacement or compensation)",
            "Written replies from the trader so far",
        ],
        "misleading": [
            "The advertisement, shelf label, website screen or email you relied on",
            "The price you were quoted versus what you were charged",
            "Screenshots, receipts and dates of each interaction",
        ],
        "contracts": [
            "Contract type (subscription, door sale, utilities, etc.) and start date",
            "The clause or fee you dispute, with page or section reference if known",
            "Cooling-off or cancellation notices you sent or received",
        ],
        "tenancy": [
            "Property address and lease dates",
            "Bond authority references and condition report dates",
            "Notices received (rent increase, breach, termination) with dates",
        ],
        "scams": [
            "How you were contacted and what you were asked to pay or share",
            "Payment channels, amounts and times",
            "Other agencies you already reported to (bank, police, Scamwatch)",
        ],
        "doorstep": [
            "Date and place of visit or call; trader name if known",
            "What you signed or paid and any cooling-off notice you gave",
            "IDs or permits you were shown (or not shown)",
        ],
        "billing": [
            "Account or customer number and billing period in dispute",
            "Line items you challenge, with expected vs charged amounts",
            "Prior complaints or reference numbers with the provider",
        ],
        "complaints": [
            "Chronology of who you contacted and key dates",
            "Your desired outcome in one clear sentence",
            "Deadlines from internal policy or industry rules if known",
        ],
    }
    bullets = list(cat_bullets.get(cat, cat_bullets["complaints"]))

    # Fourth bullet: topic-specific (one line each)
    specific_fourth: dict[str, str] = {
        "faulty-statutory-guarantees": "Which guarantee you rely on (acceptable quality, fitness, description, etc.)",
        "faulty-major-failures": "Why you believe the failure is “major” and the remedy you prefer",
        "faulty-repairs-timelines": "Repair deadlines promised or missed, and spare-part delays",
        "faulty-unsafe-recalls": "Product model, batch or recall notice; injuries or whether you stopped using it",
        "faulty-digital-goods": "Platform (e.g. App Store), app name, version, subscription ID and error messages",
        "refunds-refund-entitlement": "Whether the issue is change-of-mind vs a legal entitlement to refund",
        "refunds-repair-or-replace": "What the business offered and why you reject repair-only",
        "refunds-proof-purchase": "Every proof you hold (receipt, bank feed, warranty card)",
        "refunds-layby-deposits": "Lay-by terms, cancellation letter and any deposit retained",
        "refunds-extended-warranties": "Store warranty wording vs ACL statutory rights you assert",
        "misleading-drip-pricing": "Mandatory fees omitted at display or checkout",
        "misleading-was-now": "Comparative pricing evidence (was price, sale dates)",
        "misleading-bait-advertising": "Advertised special vs what staff offered instead",
        "misleading-fake-reviews": "Reviews or endorsements you believe are misleading",
        "misleading-fine-print": "Terms you say were hidden or unfairly prominent",
        "contracts-unfair-terms": "Exact clause text and why it is one-sided or unclear",
        "contracts-cooling-doorstep": "Cooling-off dates and how you delivered cancellation",
        "contracts-subscriptions-auto": "Trial end date, renewal charges and cancellation proof",
        "contracts-bundled-addons": "Extras bundled without clear consent",
        "contracts-early-exit": "Exit fee quoted at sale vs on final bill",
        "tenancy-bond-refunds": "Bond amount lodged, proposed deductions and evidence",
        "tenancy-condition-reports": "Entry/exit photos or report disagreements",
        "tenancy-repairs-tenancy": "Repair requests sent and landlord or agent replies",
        "tenancy-rent-increases": "Notice period, new amount and comparison to market if disputed",
        "tenancy-breaking-lease": "Reason for leaving, advertising for replacement tenant, costs",
        "scams-online-shopping-scams": "Seller URL, marketplace messages and tracking info",
        "scams-phishing": "Channels impersonated and information you may have disclosed",
        "scams-unsafe-injuries": "Injury date, medical attention and product still in your possession",
        "scams-pyramid-schemes": "Recruitment messages and money paid to join or buy inventory",
        "scams-recovery-scams": "Prior loss and the “recovery” offer or fee requested",
        "doorstep-cooling-unsolicited": "Whether sale was unsolicited and your cancellation notice",
        "doorstep-permits-id": "Permit numbers shown (or refused) and trader description",
        "doorstep-telemarketing": "Call times, numbers and Do Not Call preferences",
        "doorstep-energy-telco-marketers": "Offer compared to your current plan and cooling-off",
        "doorstep-cooling-forms-proof": "Written cancellation and proof of delivery",
        "billing-bill-line-by-line": "Tariff codes or duplicate lines you dispute",
        "billing-utilities-complaints": "Internal complaint reference and ombudsman eligibility",
        "billing-backbilling": "Period of back-bill and calculation the provider sent",
        "billing-hardship-payment-plans": "Income summary and instalment you can afford",
        "billing-exit-fees-billing": "Contract fee table vs exit fee charged",
        "complaints-effective-complaint": "Single-page summary and numbered asks",
        "complaints-evidence-timelines": "Folder structure or index of your evidence files",
        "complaints-internal-dispute": "Escalation references and senior response deadlines",
        "complaints-external-schemes": "Scheme name, eligibility and pack upload limits",
        "complaints-tribunal-court": "Tribunal/court limit, filing fee and relief sought",
    }
    bullets.append(specific_fourth.get(suffix, "Anything else that helps us match your case to this topic"))

    extra = {
        "faulty-digital-goods": (
            "Digital product details",
            "Platform, product name, version, subscription or order ID, screenshots of errors or locked content.",
        ),
        "faulty-unsafe-recalls": (
            "Safety and recall information",
            "Model, batch or serial, recall notice reference, whether you stopped using the product, injuries or near misses.",
        ),
        "faulty-major-failures": (
            "Major failure explanation",
            "Why the problem is serious or unsafe, and whether you still want refund, replacement or compensation.",
        ),
        "faulty-statutory-guarantees": (
            "Guarantee you rely on",
            "Which consumer guarantee applies and how the product or service fell short.",
        ),
        "faulty-repairs-timelines": (
            "Repair timeline",
            "Dates of drop-off/pick-up, promised return dates and any written repair quotes.",
        ),
        "refunds-refund-entitlement": (
            "Refund basis",
            "ACL or contract basis for refund; amount and date you paid.",
        ),
        "scams-online-shopping-scams": (
            "Seller and payment trail",
            "Storefront link, payment app, tracking numbers and messages with the seller.",
        ),
        "tenancy-bond-refunds": (
            "Bond and deductions",
            "Bond number, amount claimed by landlord and your dispute point-by-point.",
        ),
    }.get(
        suffix,
        (
            "Details for this topic",
            "Add any dates, reference numbers or names unique to your situation.",
        ),
    )

    focus = {
        "faulty": "This claim form is for problems with faulty or mis-described goods and services.",
        "refunds": "This claim form is for refund, repair and replacement disputes.",
        "misleading": "This claim form is for misleading prices, advertising or fine print.",
        "contracts": "This claim form is for unfair terms, subscriptions and contract exits.",
        "tenancy": "This claim form is for rental bonds, repairs and tenancy notices.",
        "scams": "This claim form is for scams, unsafe products linked to fraud, and recovery fraud.",
        "doorstep": "This claim form is for door-to-door sales, telemarketing and cooling-off.",
        "billing": "This claim form is for incorrect bills, utilities and exit fees.",
        "complaints": "This claim form is for complaint handling, evidence and escalation paths.",
    }.get(cat, "This claim form captures your issue for assessment.")

    focus_fine_tune = {
        "faulty-digital-goods": "This claim form is for paid digital products—software, apps, games, subscriptions or downloads—that are defective, not as described, or keep charging after cancellation.",
        "faulty-unsafe-recalls": "This claim form is for unsafe goods, injuries or near misses, and for responding to or disputing recall notices.",
        "faulty-major-failures": "This claim form is when you believe the failure is serious (“major”) and you want refund, replacement or compensation—not only a repair.",
        "faulty-statutory-guarantees": "This claim form is when you rely on statutory or consumer guarantees about acceptable quality, fitness for purpose or matching description.",
        "faulty-repairs-timelines": "This claim form is for unreasonably delayed repairs, refused repairs, or spare-part issues under consumer law.",
        "scams-online-shopping-scams": "This claim form is for fake stores, non-delivery, or marketplace fraud after you paid online.",
        "scams-phishing": "This claim form is after impersonation or phishing led to loss of money or personal data.",
        "tenancy-bond-refunds": "This claim form is for bond lodgement, return delays, or disputed bond deductions.",
    }
    focus = focus_fine_tune.get(suffix, focus)

    return {
        "focus": focus,
        "bullets": bullets,
        "extra_label": extra[0],
        "extra_placeholder": extra[1],
    }


def parse_workflow(path: Path) -> tuple[str, str, str]:
    raw = path.read_text(encoding="utf-8")
    m_h = re.search(r'<h1 id="wf-page-title">(.*?)</h1>', raw, re.DOTALL)
    h1 = re.sub(r"\s+", " ", m_h.group(1).strip()) if m_h else path.stem
    m_b = re.search(
        r'<p class="la-workflow-back"><a href="([^"]+)">←\s*([^<]+)</a></p>',
        raw,
    )
    back_href = m_b.group(1) if m_b else "主页面.html"
    back_label = m_b.group(2).strip() if m_b else "Back"
    return h1, back_href, back_label


def merge_shell_title(doc_title: str) -> str:
    shell = load_header_shell()
    out: list[str] = []
    for line in shell.splitlines():
        if line.strip().startswith("<title>"):
            out.append(f"  <title>{esc(doc_title)}</title>")
        else:
            out.append(line)
    return "\n".join(out)


def build_claim_page(
    *,
    suffix: str,
    h1_topic: str,
    wf_file: str,
    back_href: str,
    back_label: str,
) -> str:
    pack = topic_pack(suffix)
    doc_title = f"Submit a claim — {h1_topic} — Consumer Rights"
    shell = merge_shell_title(doc_title)
    bullets_html = "\n          ".join(f"<li>{esc(b)}</li>" for b in pack["bullets"])
    extra_label = str(pack["extra_label"])
    extra_ph = str(pack["extra_placeholder"])
    focus = str(pack["focus"])
    main = f"""
  <nav class="breadcrumbs" aria-label="Breadcrumb">
    <div class="container">
      <a href="主页面.html">Home</a><span>/</span><a href="{esc(back_href)}">{esc(back_label)}</a><span>/</span><a href="{esc(wf_file)}">{esc(h1_topic)}</a><span>/</span>Submit a claim
    </div>
  </nav>

  <main id="main-content" class="page-content claim-topic-page">
    <div class="container claim-topic-inner">
      <p class="la-workflow-back"><a href="{esc(wf_file)}">← Back to guide: {esc(h1_topic)}</a></p>
      <h1 class="claim-topic-h1">Submit a claim</h1>
      <p class="claim-topic-topicline"><strong>Topic:</strong> {esc(h1_topic)}</p>
      <p class="claim-topic-lead">{esc(focus)} The fields below are tailored to this topic so we can triage your file correctly.</p>

      <section class="claim-topic-panel" aria-labelledby="checklist-h">
        <h2 id="checklist-h">Before you start — have this ready</h2>
        <ul class="claim-topic-checklist">
          {bullets_html}
        </ul>
      </section>

      <form class="claim-topic-form" action="#" method="get" aria-label="Submit a claim">
        <div class="form-group">
          <label for="ct-name">Your full name</label>
          <input id="ct-name" name="name" type="text" autocomplete="name" required class="form-control">
        </div>
        <div class="form-group">
          <label for="ct-email">Email</label>
          <input id="ct-email" name="email" type="email" autocomplete="email" required class="form-control">
        </div>
        <div class="form-group">
          <label for="ct-phone">Phone <span class="hint">(optional)</span></label>
          <input id="ct-phone" name="phone" type="tel" autocomplete="tel" class="form-control">
        </div>
        <div class="form-group">
          <label for="ct-trader">Business, landlord or agent name</label>
          <input id="ct-trader" name="trader" type="text" required class="form-control">
        </div>
        <div class="form-group">
          <label for="ct-summary">What happened (short summary)</label>
          <textarea id="ct-summary" name="summary" rows="5" required class="form-control" placeholder="Dates, amounts, and what you want the business to do."></textarea>
        </div>
        <div class="form-group">
          <label for="ct-extra">{esc(extra_label)}</label>
          <span class="hint">{esc(extra_ph)}</span>
          <textarea id="ct-extra" name="topic_extra" rows="4" required class="form-control"></textarea>
        </div>
        <div class="form-group">
          <label for="ct-evidence">Links or references to evidence <span class="hint">(optional)</span></label>
          <textarea id="ct-evidence" name="evidence" rows="3" class="form-control" placeholder="e.g. cloud folder link, email thread IDs, or attachment filenames you will upload later."></textarea>
        </div>
        <div class="form-group form-check">
          <input id="ct-accurate" name="accurate" type="checkbox" required value="1">
          <label for="ct-accurate">I confirm this information is accurate to the best of my knowledge.</label>
        </div>
        <div class="claim-topic-actions">
          <a href="{esc(f"任务 1 的第二个页面.html?topic={suffix}")}" class="btn btn-primary btn-lg">Continue to 3-step claim</a>
          <a class="btn btn-secondary btn-lg" href="Contact.html">Contact for support instead</a>
        </div>
        <p class="claim-topic-note">This prototype does not send data. In a live site this form would POST to your case system with topic code <code>{esc(suffix)}</code>.</p>
      </form>
    </div>
  </main>

<script src="site-preferences.js"></script>
</body>
</html>
"""
    return shell + "\n" + main


def patch_workflow(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    if "la-workflow-actions--dual" in raw:
        return False
    m = OLD_ACTIONS.search(raw)
    if not m:
        return False
    suffix = path.name.removeprefix("workflow-").removesuffix(".html")
    wizard_href = f"任务 1 的第二个页面.html?topic={suffix}"
    new_block = (
        '<div class="la-workflow-actions la-workflow-actions--dual">'
        "<span>What would you like to do?</span>"
        f'<a class="la-btn-maroon" href="{esc(wizard_href)}">Submit a claim <span aria-hidden="true">›</span></a>'
        '<a class="la-btn-teal" href="Contact.html">Contact for support <span aria-hidden="true">›</span></a>'
        "</div>"
    )
    raw2 = OLD_ACTIONS.sub(new_block, raw, count=1)
    raw2 = raw2.replace(LEAD_OLD, LEAD_NEW, 1)
    if raw2 != raw:
        path.write_text(raw2, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    seen: set[str] = set()
    for path in sorted(BASE.glob("workflow-*.html")):
        key = str(path.resolve())
        if key in seen:
            continue
        seen.add(key)
        suffix = path.name.removeprefix("workflow-").removesuffix(".html")
        if patch_workflow(path):
            print("patched", path.name)
        h1, back_href, back_label = parse_workflow(path)
        claim_name = f"claim-{suffix}.html"
        html_out = build_claim_page(
            suffix=suffix,
            h1_topic=h1,
            wf_file=path.name,
            back_href=back_href,
            back_label=back_label,
        )
        (BASE / claim_name).write_text(html_out, encoding="utf-8", newline="\n")
        print("wrote", claim_name)


if __name__ == "__main__":
    main()
