"""Guidewire competitive landscape knowledge base used to power research prompts.

Organized by threat vector — not all competitors are created equal.
The 'unbundler' category (workflow attackers) is the highest-priority watch list.
"""

GUIDEWIRE_CONTEXT = """
ABOUT GUIDEWIRE (GWRE):
Guidewire Software is the system of record for Property & Casualty (P&C) insurance companies globally.

CORE PRODUCTS:
- PolicyCenter: Policy administration system — underwriting, policy lifecycle management, rating
- BillingCenter: Billing management — premium collection, payment processing, disbursements
- ClaimCenter: Claims management — FNOL, adjudication, payments, litigation management
- InsuranceSuite: Combined platform (PolicyCenter + BillingCenter + ClaimCenter)
- Guidewire Cloud: Cloud-hosted SaaS version of InsuranceSuite
- InsuranceNow: Lightweight SaaS for smaller/regional carriers
- Guidewire Marketplace: Ecosystem of 200+ partner apps
- DataHub / InfoCenter: Analytics, data warehouse, reporting

TARGET CUSTOMERS: Tier 1, 2, and 3 P&C insurers globally — auto, homeowners, commercial, specialty lines
BUSINESS MODEL: Annual cloud SaaS subscriptions + professional services
MARKET POSITION: #1 core systems vendor for P&C insurance globally; ~500 carrier customers

---

## THREAT VECTOR 1: CORE REPLACEMENT (direct platform competitors)

These are full-stack alternatives pitching carriers on replacing Guidewire entirely.
Hardest to scale but highest long-term threat. Often win greenfield / digital subsidiaries first.

- Duck Creek Technologies: Policy, billing, claims suite; owned by Vista Equity Partners
- Majesco (MJCO): Cloud-native insurance platform; CloudInsurer product
- Sapiens International (SPNS): P&C and L&H insurance software globally
- Insurity: Policy, billing, claims for specialty and personal lines; owned by GI Partners
- OneShield Enterprise: Mid-market P&C software
- EIS Group: Modern core insurance platform targeting greenfield and digital carriers
- Socotra: Cloud-native, API-first policy administration; backed by TCV; developer-friendly
- Instanda: No-code product configuration layer; often sits alongside or replaces PolicyCenter; backed by MS&AD Ventures
- BriteCore: Cloud-native core for SMB/mutual insurers; frequently cited as top Guidewire alternative
- Openkoda: Open-source/own-the-code alternative; modular policy, claims, billing; appeals to carriers wanting flexibility over vendor lock-in
- Applied Systems: Commercial lines management software
- FINEOS: Claims and benefits management for L&H/Workers Comp (ASX: FCL)
- Unqork: No-code enterprise platform used by carriers for policy/claims

---

## THREAT VECTOR 2: UNBUNDLERS / WORKFLOW ATTACKERS (highest strategic priority)

These are the most dangerous near-term category. They do NOT replace Guidewire directly.
Instead they: (1) wedge into a high-value workflow, (2) own decisioning + UX over time,
(3) risk turning Guidewire into a commoditized system of record only.

Sequence to watch: workflow wedge → system of engagement → modular replacement becomes possible.

- Federato: Portfolio-level underwriting optimization ("RiskOps"); AI-driven underwriting + portfolio management layered on top of core systems
- Sixfold: GenAI underwriting co-pilot; ingests structured + unstructured risk data; part of Guidewire Ventures ecosystem
- Indico Data: Intake + document processing; automates submission-to-underwriting funnel; part of Guidewire Ventures ecosystem
- Shift Technology: AI-powered fraud detection, claims automation, and underwriting decisions; deep EU carrier penetration; Series D (~$220M raised)
- Cytora: "Digital risk flow" platform; competes directly with underwriting workflow layer
- Send Technology Solutions: Underwriting workbench with strong Lloyd's of London traction; very similar entry point to Federato
- Gradient AI: ML for underwriting pricing and claims severity prediction
- Snapsheet: Digital claims management, virtual appraisals; backed by Insight Partners
- Five Sigma: AI-native claims management platform
- CLARA Analytics: AI for claims management (litigation, medical)
- Tractable: AI for accident and disaster recovery claims

---

## THREAT VECTOR 3: HORIZONTAL / ARCHITECTURAL DISRUPTORS

These chip away at Guidewire's integration moat piece by piece.
They attack cost structure, data model, or the implementation layer.

- Combined Ratio Solutions: Open-source policy admin alternative; explicitly targeting "expensive, clunky platforms" like Guidewire
- Sureify: Customer engagement + digital front-end layer; can displace front-end of core systems
- AgentSync: Compliance + distribution infrastructure; attacks "system glue" around Guidewire
- Novidea: Broker + MGA platform; moves power upstream from carrier core
- Appian: Low-code platform used in insurance workflows (Nasdaq: APPN)
- Salesforce Financial Services Cloud: CRM expanding into insurance workflows
- ServiceNow: Workflow platform expanding into insurance operations

---

## EMERGING THREAT — new carrier platforms bypassing Guidewire entirely

- Lemonade (NYSE: LMND): Tech-forward carrier; selling AI/tech platform to other insurers
- Kin Insurance: Home insurance tech platform; cloud-native stack
- Clearcover: Auto insurance on proprietary modern stack
- Betterview: Property intelligence/aerial imagery for underwriting
- Cape Analytics: AI property analytics for underwriting
- Verisk (Nasdaq: VRSK): Data analytics for insurance
- CCC Intelligent Solutions (CCCS): Auto claims ecosystem

---

WHAT MAKES A FINDING RELEVANT TO GUIDEWIRE:
HIGH relevance:
- Unbundler (Federato, Sixfold, Cytora, Send, Shift, Indico) raises funding, wins Tier 1 carrier, or expands product scope beyond single workflow
- Direct competitor (Duck Creek, Socotra, EIS, BriteCore, Instanda) raises funding or wins carrier switching from Guidewire
- A carrier publicly announces switching FROM Guidewire to a competitor
- SI (Accenture, TCS, Capgemini) publicly steers client away from Guidewire toward an alternative
- Horizontal disruptor (AgentSync, Novidea, Combined Ratio) gains significant carrier adoption

MEDIUM relevance:
- Insurtech raises Series B+ from a top VC for claims/policy/billing/underwriting tech
- Established carrier tech company announces new AI features competing with Guidewire modules
- Major VC publishes blog/research positioning insurtech as core system disruption
- New MGA/carrier startup chooses a modern alternative platform over Guidewire
- Unbundler integrates with Guidewire (initial wedge — watch for scope creep)

LOW relevance (exclude):
- Pure consumer/D2C insurers (car insurance apps, pet insurance, etc.)
- Life/health/dental insurance technology (not P&C)
- Pure distribution/brokerage tech (comparative raters, agency management)
- Small pre-seed / seed rounds under $5M
- International markets with no Guidewire presence
"""

# Tier 1 threat: unbundlers / workflow attackers — monitor most closely
UNBUNDLER_NAMES = [
    "federato", "sixfold", "indico data", "shift technology", "cytora",
    "send technology", "gradient ai", "snapsheet", "five sigma", "clara analytics",
    "tractable",
]

# Tier 1 threat: direct core replacement
DIRECT_COMPETITOR_NAMES = [
    "duck creek", "majesco", "sapiens", "insurity", "oneshield", "applied systems",
    "eis group", "socotra", "instanda", "britecore", "openkoda", "fineos", "unqork", "appian",
]

# Tier 2 threat: architectural / horizontal disruptors
INDIRECT_COMPETITOR_NAMES = [
    "combined ratio solutions", "sureify", "agentsync", "novidea",
    "betterview", "cape analytics", "ccc intelligent", "mitchell international", "solera", "audatex",
]

COMPETITOR_DOMAIN_KEYWORDS = [
    "policy administration", "policy management", "claims management", "claims automation",
    "billing management", "insurance platform", "insurance core system", "insurance SaaS",
    "p&c insurance software", "property casualty software", "insurtech platform",
    "insurance modernization", "carrier technology", "core insurance", "underwriting platform",
    "underwriting workbench", "RiskOps", "underwriting optimization", "portfolio underwriting",
    "FNOL", "first notice of loss", "claims adjudication", "insurance suite",
]
