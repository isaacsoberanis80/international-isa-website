"""
One-time seed: load the 28 real estate/insurance/A&E/trades leads already
researched (see LEAD_LIST.md) into the structured ProspectLead table, with
scoring done directly by Claude (pain point, estimated value, solution fit,
1-10 score) -- no separate Anthropic API call needed, since this analysis
is the same work Claude Code already does when researching leads.

Run with: python seed_prospect_leads.py
"""

from app import create_app
from app.db import add_prospect_lead
from app.models import ProspectLead, db

# (company_name, industry, location, contact_info, pain_point, estimated_value, solution_fit, score)
LEADS = [
    # --- Real Estate: High priority, contact confirmed ---
    ("Treasure Coast House Hunters (Ann Marie Chauss)", "Real Estate", "Port St. Lucie, FL",
     "ann.chauss@cbrealty.com / (772) 732-2800",
     "Top 1% FL team by volume with a luxury book of business -- at this deal size, every dropped or slow-followed lead is a large dollar loss.",
     "$40-60K/yr equivalent (full-time bilingual ISA vs. in-house hire)",
     "AI Agent + Human Rep Bundle or hourly ISA -- luxury clientele needs a human touch, not pure automation.",
     9),
    ("Caplicki Home Team (Brian Caplicki)", "Real Estate", "Middletown, NY",
     "brian@caplickihometeam.com / (845) 237-2368",
     "1,300+ career transactions and still growing -- follow-up capacity is almost certainly the constraint on further scale, not lead volume.",
     "$40-60K/yr equivalent",
     "Hourly ISA labor -- proven high-volume team likely already has a process, just needs more hands.",
     9),
    ("Whissel Realty Group", "Real Estate", "La Mesa/San Diego, CA",
     "info@whisselrealty.com / 858-348-5800",
     "Publicly on record (via Ylopo testimonial) wanting to spend less time on lead gen and more on closing -- already paying for AI lead gen but still needs humans to convert it.",
     "$75K+/yr equivalent at this volume (1,042 sides/yr)",
     "Revenue-share or AI Agent + Human Rep Bundle -- complements their existing Ylopo stack rather than competing with it.",
     10),
    ("Kaminsky Real Estate Group", "Real Estate", "Hermosa Beach, CA",
     "(310) 798-1277 (email not public)",
     "#1 team in South Bay LA -- high volume implies high call/follow-up load; email needs to be found before outreach.",
     "$40-60K/yr equivalent",
     "Hourly ISA labor",
     8),
    # --- Real Estate: hiring an ISA now (hottest signal, contact TBD) ---
    ("The Ryan & Brian Real Estate Team", "Real Estate", "Unknown",
     "Not yet found",
     "Actively posted an ISA job opening -- already budgeted and decided they need this role filled.",
     "Cost of a full in-house hire avoided (~$40-50K/yr)",
     "AI Agent + Human Rep Bundle pitched as faster/lower-risk than hiring.",
     7),
    ("Velocity Realty", "Real Estate", "San Diego, CA",
     "Not yet found",
     "Hiring an ISA for a self-described 'high-performance' team -- growth-stage, likely feeling the follow-up gap acutely.",
     "~$40-50K/yr avoided hire cost",
     "AI Agent + Human Rep Bundle",
     7),
    ("At Your Home Sold Guaranteed Realty", "Real Estate", "Tennessee",
     "Not yet found",
     "#1 team in TN with a pre-set-appointment model -- entire business model depends on ISA-style follow-up capacity.",
     "$50K+/yr equivalent given scale (6,000+ homes sold)",
     "Hourly ISA labor at scale, possibly multiple agents",
     7),
    ("Axis Real Estate Team", "Real Estate", "Las Vegas, NV",
     "Not yet found",
     "Hiring a remote ISA -- already comfortable with a remote/outsourced model, an easier sell than a team used to in-office only.",
     "~$40-50K/yr avoided hire cost",
     "AI Agent + Human Rep Bundle",
     7),
    ("Central Texas Real Estate Investment Company", "Real Estate", "Central TX",
     "Not yet found",
     "ISA described as 'engine of acquisitions team' -- investor-focused, implies high call volume and urgency-driven deals.",
     "~$45K/yr avoided hire cost",
     "Hourly ISA labor -- investor deals often need fast, consistent follow-up",
     7),
    ("The Thomas March Home Selling Group", "Real Estate", "Unknown",
     "Not yet found",
     "Actively hiring an ISA -- same direct-need signal as others in this group.",
     "~$40-50K/yr avoided hire cost",
     "AI Agent + Human Rep Bundle",
     6),
    # --- Real Estate: Ylopo/AI-tool clients (tech-forward, contact TBD) ---
    ("Wemert Group Realty", "Real Estate", "Unknown", "Not yet found",
     "Already investing in AI lead gen (Ylopo) -- proves budget exists, but still needs a human to close what the AI surfaces.",
     "$30-50K/yr equivalent", "Revenue-share or AI Agent + Human Rep Bundle", 6),
    ("Realty Group", "Real Estate", "Multi-state", "Not yet found",
     "800+ agents, Ylopo client since 2017 -- large org, likely already has some ISA function; the opportunity is a specific region or team within it, not the whole company.",
     "Varies by region -- needs a named regional contact first", "Hourly ISA labor at the team level", 5),
    ("The Creighton Rinaldi Team", "Real Estate", "Las Vegas, NV", "Not yet found",
     "Ylopo client -- same AI-plus-human-closer gap as Whissel.",
     "$30-50K/yr equivalent", "AI Agent + Human Rep Bundle", 6),
    ("Matt Curtis Realty", "Real Estate", "Huntsville, AL", "Not yet found",
     "Top-33 team nationally, 1,000+ deals/year, Ylopo client -- high volume with existing AI investment.",
     "$50K+/yr equivalent at this volume", "Revenue-share", 7),
    ("Exit Realty Consultants", "Real Estate", "Unknown", "Not yet found",
     "Ylopo client -- same general fit as other AI-tool users.",
     "$30-50K/yr equivalent", "AI Agent + Human Rep Bundle", 5),
    ("DLP Realty, Inc", "Real Estate", "Unknown", "Not yet found",
     "Ylopo client.", "$30-50K/yr equivalent", "AI Agent + Human Rep Bundle", 5),
    ("Merrill and Associates", "Real Estate", "Unknown", "Not yet found",
     "Ylopo client.", "$30-50K/yr equivalent", "AI Agent + Human Rep Bundle", 5),
    # --- Real Estate: RealTrends press-verified, no direct signal yet ---
    ("The Short Term Shop", "Real Estate", "Santa Rosa Beach, FL", "Not yet found",
     "753 sides/$481M, but a short-term-rental/vacation niche -- verify the bilingual angle actually fits this specific market before prioritizing.",
     "$50K+/yr equivalent at this volume", "Hourly ISA labor", 6),
    ("Align", "Real Estate", "Hoboken, NJ", "Not yet found",
     "1,009 sides/$644.3M -- high volume, no specific pain point confirmed yet, cold outreach on numbers alone.",
     "$50K+/yr equivalent", "Revenue-share", 6),
    ("Zac Nelson Team", "Real Estate", "Denver, CO", "Not yet found",
     "RealTrends Top Team by Volume -- verified performer, no specific pain point confirmed yet.",
     "$40-50K/yr equivalent", "Hourly ISA labor", 6),
    # --- Insurance ---
    ("Bellido Insurance Brokerage, Inc.", "Insurance", "Glendale, NY",
     "Info@BellidoIns.com / 718.326.2992",
     "Independent since 1983, currently hiring a bilingual commercial Account Executive themselves -- they've already named the exact need in a job posting.",
     "$45-55K/yr equivalent (avoided hire) + ongoing policy/quote support value",
     "AI Agent + Human Rep Bundle -- founder's own ProTech insurance background is a strong credibility angle here.",
     9),
    ("Redberry Insurance Group", "Insurance", "San Antonio, TX", "210-686-5848 (email TBD)",
     "Growing independent agency hiring bilingual commercial producers -- same direct-need signal as Bellido.",
     "$40-50K/yr equivalent", "AI Agent + Human Rep Bundle", 8),
    ("Superior Insurance Partners (Noblesville, IN)", "Insurance", "Indianapolis area",
     "(317) 774-9400 (named contact TBD)",
     "Hiring a bilingual Commercial Lines Account Manager -- direct-need signal, but needs a named contact before outreach.",
     "$40-50K/yr equivalent", "Hourly ISA labor", 7),
    # --- Architecture & Engineering ---
    ("Duvall Decker Architects, P.A.", "Architecture", "Jackson, MS",
     "info@duvalldecker.com / (601) 713-1128",
     "2026 AIA Architecture Firm Award winner -- prestige target, but no confirmed admin/hiring pain point, so this is a cold outreach on firm quality alone, not a proven need.",
     "Unclear -- needs discovery call to size", "AI Agent + Human Rep Bundle (client intake/scheduling only, not design work)", 5),
    # --- Trades ---
    ("Abacus Plumbing, Air Conditioning & Electrical", "Trades/HVAC", "Houston, TX",
     "(713) 812-7070 (email TBD)",
     "24-hour operation with 546+ reviews, actively hiring customer service across plumbing/HVAC/electrical -- high call volume implies real dispatch/follow-up strain.",
     "$40-50K/yr equivalent", "Hourly ISA labor (dispatch support)", 7),
    ("Kansas City Plumbing Company (KCPC)", "Trades/Plumbing", "Kansas City, MO",
     "info@kansascityplumbing.com / (816) 873-5272",
     "25 years in business, hiring for both Dispatch Coordinator and Office Administrator -- two open admin roles at once signals real operational strain.",
     "$45-55K/yr equivalent (two roles' worth of avoided hiring)", "Hourly ISA labor or AI Agent + Human Rep Bundle", 8),
    ("Dynamic Air Solutions", "Trades/HVAC", "Louisville, KY", "502-742-7413 (email TBD)",
     "Founded 2019, fast-growing reputation, hiring an HVAC Dispatcher -- a young, scaling company is a good fit for outsourcing instead of building an ops team from scratch.",
     "$35-45K/yr equivalent", "Hourly ISA labor", 7),
    ("Lozier Heating & Cooling", "Trades/HVAC", "West Des Moines, IA", "(515) 267-1000 (email TBD)",
     "Established since 1906, 24/7 operation, hiring a Service Dispatcher -- long-standing, stable business, likely values reliability over lowest cost.",
     "$40-50K/yr equivalent", "Hourly ISA labor", 7),
]

app = create_app()
with app.app_context():
    existing = ProspectLead.query.count()
    if existing > 0:
        print(f"ProspectLead table already has {existing} rows -- skipping seed to avoid duplicates.")
    else:
        for row in LEADS:
            add_prospect_lead(*row)
        print(f"Seeded {len(LEADS)} prospect leads.")
        db.session.close()
