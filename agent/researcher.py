"""
Research engine: breaks the daily scan into 3 focused search blocks that run
sequentially, avoiding rate-limit errors caused by one massive API call.

Each block uses claude-sonnet-4-6 with a short, targeted prompt.
A 15-second pause between blocks keeps token-per-minute usage well within
Anthropic's standard rate limits.

Threat-vector framing (reflected in search blocks):
  1. Core replacement competitors (Duck Creek, Socotra, EIS, BriteCore, Instanda, Openkoda)
  2. Unbundlers / workflow attackers — HIGHEST PRIORITY (Federato, Sixfold, Cytora, Send,
     Shift Technology, Indico Data, Gradient AI)
  3. Market signals + horizontal disruptors (AgentSync, Novidea, Combined Ratio Solutions,
     Sureify) + VC activity
"""

import logging
import time
from datetime import datetime, timedelta

import anthropic

import config
from data.competitors import (
    COMPETITOR_DOMAIN_KEYWORDS,
    DIRECT_COMPETITOR_NAMES,
    INDIRECT_COMPETITOR_NAMES,
    UNBUNDLER_NAMES,
)

logger = logging.getLogger(__name__)

# ── Compact system prompt ─────────────────────────────────────────────────────

_SEARCH_SYSTEM = """\
You are a competitive intelligence analyst for Guidewire Software (GWRE), \
the #1 P&C insurance core system (policy admin, billing, claims).

THREAT VECTOR 1 — Core replacement: Duck Creek Technologies, Majesco, Sapiens International, \
Insurity, OneShield, EIS Group, Socotra, Instanda, BriteCore, Openkoda.

THREAT VECTOR 2 — Unbundlers (HIGHEST PRIORITY — wedge into workflows, risk commoditizing Guidewire): \
Federato, Sixfold, Indico Data, Shift Technology, Cytora, Send Technology Solutions, Gradient AI, \
Snapsheet, Five Sigma, CLARA Analytics, Tractable.

THREAT VECTOR 3 — Horizontal/architectural disruptors: Combined Ratio Solutions, Sureify, \
AgentSync, Novidea, Appian, Salesforce Financial Services Cloud.

For each finding, output one line in this EXACT format (pipe-delimited):
FINDING|||[Company]|||[investment|product|metrics|partnership|platform_shift|vc_signal]|||[HIGH|MEDIUM]|||[VC firm or N/A]|||[One sentence with key detail: $amount, product name, carrier name, etc.]|||[Source URL]

HIGH relevance: unbundler raises funding / wins Tier 1 carrier / expands product scope; \
direct competitor wins carrier switching from Guidewire; SI steers client away from Guidewire; \
horizontal disruptor gains major carrier adoption.
MEDIUM relevance: insurtech Series B+ for underwriting/claims/policy/billing; VC blog about \
core-system disruption; unbundler integrates with Guidewire (watch for scope creep).
Do NOT output LOW relevance findings.
When done searching, output: BLOCK_COMPLETE
"""

# ── Three focused search blocks ───────────────────────────────────────────────

def _date_range() -> str:
    today    = datetime.now()
    week_ago = today - timedelta(days=7)
    return f"{week_ago.strftime('%B %d')}\u2013{today.strftime('%B %d, %Y')}"


_SEARCH_BLOCKS = [
    {
        "name": "direct_competitors",
        "prompt_template": """\
Search for news from the past 7 days ({date_range}) about these \
Guidewire core-replacement competitors:

\u2022 Duck Creek Technologies \u2014 product news, funding, customer wins
\u2022 Majesco (MJCO) \u2014 earnings, new releases, customer announcements
\u2022 Sapiens International (SPNS) \u2014 M&A, product, customer news
\u2022 Insurity \u2014 funding, product, partnerships
\u2022 EIS Group \u2014 new deals, product launches, carrier wins
\u2022 Socotra \u2014 funding rounds, new carrier customers, product updates
\u2022 Instanda \u2014 funding, growth metrics, new markets
\u2022 BriteCore \u2014 funding, new carrier customers, product news
\u2022 Openkoda \u2014 adoption news, carrier announcements, open-source traction

Search each company + \"news\" OR \"announcement\" OR \"funding\" OR \"customer\" 2025 2026.
Output all HIGH and MEDIUM relevance FINDING||| lines, then: BLOCK_COMPLETE""",
    },
    {
        "name": "unbundlers_workflow_attackers",
        "prompt_template": """\
Search for news from the past 7 days ({date_range}) about these companies \
that attack Guidewire by owning specific high-value workflows \
(underwriting, claims decisioning, intake) — the highest-priority competitive category:

\u2022 Federato \u2014 RiskOps / portfolio underwriting optimization; funding, carrier wins, product expansion
\u2022 Sixfold \u2014 GenAI underwriting co-pilot; funding, new carrier deployments, product scope expansion
\u2022 Cytora \u2014 digital risk flow / underwriting workflow; funding, partnerships, carrier traction
\u2022 Send Technology Solutions \u2014 underwriting workbench; Lloyd's traction, new carrier wins, funding
\u2022 Indico Data \u2014 submission intake + document processing; funding, carrier deployments
\u2022 Shift Technology \u2014 claims + fraud + underwriting AI; new deals, product expansion, funding
\u2022 Gradient AI \u2014 underwriting pricing + claims severity ML; funding, partnerships
\u2022 Snapsheet \u2014 digital claims management; funding, new carrier wins
\u2022 Five Sigma \u2014 AI-native claims platform; funding, carrier announcements
\u2022 CLARA Analytics \u2014 claims AI (litigation, medical); funding or product news
\u2022 Tractable \u2014 AI claims for accident/disaster recovery; partnerships or expansion

For each, also search: [company name] + \"Guidewire\" to find any integration announcements \
(integrations = initial wedge; watch for scope creep into broader platform).

Output all HIGH and MEDIUM relevance FINDING||| lines, then: BLOCK_COMPLETE""",
    },
    {
        "name": "market_signals",
        "prompt_template": """\
Search for news from the past 7 days ({date_range}) about:

PART A \u2014 Horizontal / architectural disruptors chipping away at Guidewire's integration moat:
\u2022 Combined Ratio Solutions \u2014 open-source policy admin; carrier adoption, funding, announcements
\u2022 AgentSync \u2014 insurance compliance + distribution infrastructure; funding, growth, partnerships
\u2022 Novidea \u2014 broker + MGA platform; new deals, funding, market expansion
\u2022 Sureify \u2014 customer engagement + digital front-end; carrier wins, funding, product news

PART B \u2014 Broader market signals:
\u2022 insurtech funding round Series B C D 2026 \"underwriting\" OR \"claims management\" OR \"policy administration\"
\u2022 insurance carrier \"replaced\" OR \"migrated\" OR \"switched from\" Guidewire
\u2022 Guidewire competitor announcement {month_year}
\u2022 SI \"Accenture\" OR \"TCS\" OR \"Capgemini\" insurance core system replacement 2026

PART C \u2014 VC signals:
\u2022 \"Anthemis\" OR \"QED Investors\" OR \"Munich Re Ventures\" insurance investment 2026
\u2022 \"Nationwide Ventures\" OR \"XL Innovate\" OR \"Aquiline\" insurtech portfolio news
\u2022 \"Insight Partners\" OR \"TCV\" OR \"General Catalyst\" insurance software investment 2026

Output all HIGH and MEDIUM relevance FINDING||| lines, then: BLOCK_COMPLETE""",
    },
]


# ── Parsing ───────────────────────────────────────────────────────────────────

def _parse_findings(text: str) -> list[dict]:
    findings = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("FINDING|||"):
            continue
        parts = line.split("|||")
        if len(parts) < 7:
            logger.warning("Skipping malformed finding: %s", line[:100])
            continue
        findings.append({
            "company":     parts[1].strip(),
            "type":        parts[2].strip().lower(),
            "relevance":   parts[3].strip().upper(),
            "vc_firm":     parts[4].strip(),
            "description": parts[5].strip(),
            "source":      parts[6].strip(),
            "found_at":    datetime.now().isoformat(),
        })
    return findings


# ── Single block runner ───────────────────────────────────────────────────────

def _run_block(client: anthropic.Anthropic, block: dict) -> list[dict]:
    """Run one focused search block. Returns findings (empty list on failure)."""
    date_range  = _date_range()
    month_year  = datetime.now().strftime("%B %Y")
    user_prompt = block["prompt_template"].format(
        date_range=date_range,
        month_year=month_year,
    )

    messages       = [{"role": "user", "content": user_prompt}]
    accumulated    = ""
    continuations  = 0
    max_cont       = 3

    while continuations <= max_cont:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
            system=_SEARCH_SYSTEM,
            tools=[{"type": "web_search_20260209", "name": "web_search"}],
            messages=messages,
        )

        for content_block in response.content:
            if hasattr(content_block, "text"):
                accumulated += content_block.text + "\n"

        if response.stop_reason == "end_turn":
            break
        elif response.stop_reason == "pause_turn":
            messages.append({"role": "assistant", "content": response.content})
            continuations += 1
            logger.debug("Block '%s' pause_turn %d/%d", block["name"], continuations, max_cont)
        else:
            logger.warning("Block '%s' unexpected stop_reason=%s", block["name"], response.stop_reason)
            break

    return _parse_findings(accumulated)


# ── Main entry point ──────────────────────────────────────────────────────────

BLOCK_PAUSE_SECONDS = 15


def run_research() -> list[dict]:
    """
    Run daily research across 3 sequential focused search blocks.
    """
    client = anthropic.Anthropic(
        api_key=config.ANTHROPIC_API_KEY,
        timeout=180.0,
    )

    all_findings: list[dict] = []

    for i, block in enumerate(_SEARCH_BLOCKS):
        logger.info(
            "Search block %d/%d \u2014 %s", i + 1, len(_SEARCH_BLOCKS), block["name"]
        )
        try:
            findings = _run_block(client, block)
            all_findings.extend(findings)
            logger.info("  \u2192 %d finding(s)", len(findings))
        except anthropic.RateLimitError:
            logger.warning(
                "Block '%s' hit rate limit \u2014 waiting 60 s then skipping.",
                block["name"],
            )
            time.sleep(60)
        except Exception as exc:
            logger.error(
                "Block '%s' failed (%s) \u2014 continuing with remaining blocks.",
                block["name"], exc,
            )

        if i < len(_SEARCH_BLOCKS) - 1:
            logger.debug("Pausing %d s before next block \u2026", BLOCK_PAUSE_SECONDS)
            time.sleep(BLOCK_PAUSE_SECONDS)

    seen:    set[str]  = set()
    deduped: list[dict] = []
    for f in all_findings:
        key = f"{f['company'].lower()}|{f['type'].lower()}"
        if key not in seen:
            seen.add(key)
            deduped.append(f)

    deduped.sort(key=lambda f: (0 if f.get("relevance") == "HIGH" else 1))

    logger.info(
        "Research complete \u2014 %d unique findings (%d HIGH, %d MEDIUM) across %d blocks",
        len(deduped),
        sum(1 for f in deduped if f.get("relevance") == "HIGH"),
        sum(1 for f in deduped if f.get("relevance") == "MEDIUM"),
        len(_SEARCH_BLOCKS),
    )
    return deduped
