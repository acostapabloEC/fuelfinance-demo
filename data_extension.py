"""
Extended data layer — historical, proforma, headcount, pipeline, cohorts, unit economics.
Appended to mock_data by importing: from data_extension import *
"""

# ── Monthly Historical P&L + Metrics (Jan–Jun 2026) ──────────────────────────
# Seed note ($750k) raised Aug 2024. First paying customer Jan 2025.

MONTHLY_HISTORY = [
    {
        "month": "Jan 2026", "period": "2026-01",
        "mrr": 18000, "arr": 216000,
        "new_mrr": 3200, "expansion_mrr": 0, "churned_mrr": -800, "net_new_mrr": 2400,
        "customers": 7, "new_customers": 1, "churned_customers": 1,
        "revenue_recognized": 18000, "cash_collected": 19200,
        "cogs": 6800, "gross_profit": 11200, "gross_margin_pct": 62.2,
        "payroll_gross": 30000, "payroll_net": 26500,
        "opex_rd": 1200, "opex_sales_mktg": 4800, "opex_ga": 6200, "total_opex": 12200,
        "ebitda": -1000, "ebitda_margin_pct": -5.6,
        "cash": 207500, "gross_burn": 49000, "net_burn": 30800, "headcount": 9,
    },
    {
        "month": "Feb 2026", "period": "2026-02",
        "mrr": 22000, "arr": 264000,
        "new_mrr": 4500, "expansion_mrr": 200, "churned_mrr": -700, "net_new_mrr": 4000,
        "customers": 8, "new_customers": 2, "churned_customers": 1,
        "revenue_recognized": 22000, "cash_collected": 24500,
        "cogs": 7400, "gross_profit": 14600, "gross_margin_pct": 66.4,
        "payroll_gross": 30000, "payroll_net": 26500,
        "opex_rd": 1200, "opex_sales_mktg": 5200, "opex_ga": 5800, "total_opex": 12200,
        "ebitda": 2400, "ebitda_margin_pct": 10.9,
        "cash": 198000, "gross_burn": 49600, "net_burn": 25600, "headcount": 9,
    },
    {
        "month": "Mar 2026", "period": "2026-03",
        "mrr": 27000, "arr": 324000,
        "new_mrr": 5500, "expansion_mrr": 300, "churned_mrr": -800, "net_new_mrr": 5000,
        "customers": 10, "new_customers": 2, "churned_customers": 0,
        "revenue_recognized": 27000, "cash_collected": 29800,
        "cogs": 8200, "gross_profit": 18800, "gross_margin_pct": 69.6,
        "payroll_gross": 30000, "payroll_net": 26500,
        "opex_rd": 1200, "opex_sales_mktg": 5600, "opex_ga": 5800, "total_opex": 12600,
        "ebitda": 6200, "ebitda_margin_pct": 23.0,
        "cash": 196500, "gross_burn": 50800, "net_burn": 21000, "headcount": 9,
    },
    {
        "month": "Apr 2026", "period": "2026-04",
        "mrr": 32000, "arr": 384000,
        "new_mrr": 5800, "expansion_mrr": 500, "churned_mrr": -1300, "net_new_mrr": 5000,
        "customers": 12, "new_customers": 3, "churned_customers": 1,
        "revenue_recognized": 32000, "cash_collected": 35500,
        "cogs": 9200, "gross_profit": 22800, "gross_margin_pct": 71.3,
        "payroll_gross": 31000, "payroll_net": 27500,
        "opex_rd": 1400, "opex_sales_mktg": 6000, "opex_ga": 5600, "total_opex": 13000,
        "ebitda": 9800, "ebitda_margin_pct": 30.6,
        "cash": 194200, "gross_burn": 53200, "net_burn": 17700, "headcount": 10,
    },
    {
        "month": "May 2026", "period": "2026-05",
        "mrr": 38000, "arr": 456000,
        "new_mrr": 7200, "expansion_mrr": 800, "churned_mrr": -2000, "net_new_mrr": 6000,
        "customers": 13, "new_customers": 2, "churned_customers": 1,
        "revenue_recognized": 38000, "cash_collected": 41200,
        "cogs": 10200, "gross_profit": 27800, "gross_margin_pct": 73.2,
        "payroll_gross": 32000, "payroll_net": 28000,
        "opex_rd": 1400, "opex_sales_mktg": 6400, "opex_ga": 5600, "total_opex": 13400,
        "ebitda": 14400, "ebitda_margin_pct": 37.9,
        "cash": 188750, "gross_burn": 55600, "net_burn": 14400, "headcount": 10,
    },
    {
        "month": "Jun 2026", "period": "2026-06",
        "mrr": 42000, "arr": 504000,
        "new_mrr": 4500, "expansion_mrr": 500, "churned_mrr": -1000, "net_new_mrr": 4000,
        "customers": 14, "new_customers": 3, "churned_customers": 1,
        "revenue_recognized": 42000, "cash_collected": 64200,  # inflated — $22.2k deferred
        "cogs": 11000, "gross_profit": 31000, "gross_margin_pct": 73.8,
        "payroll_gross": 32000, "payroll_net": 28000,
        "opex_rd": 1200, "opex_sales_mktg": 4800, "opex_ga": 5000, "total_opex": 11000,
        "ebitda": 0, "ebitda_margin_pct": 0.0,
        "cash": 185000, "gross_burn": 46750, "net_burn": 4750, "headcount": 10,
    },
]

# ── Revenue Streams — June 2026 ────────────────────────────────────────────────

REVENUE_STREAMS_JUNE = {
    "subscription": {
        "enterprise_plan":  {"mrr": 21600, "customers": 3, "avg_arr": 86400,
                             "names": ["Apex Systems", "Novu Corp", "DataCore Inc"]},
        "growth_plan":      {"mrr": 16000, "customers": 6, "avg_arr": 32000,
                             "names": ["Stackr Co", "Primex Tech", "Loopify Inc",
                                       "Clearpath AI", "Heliosoft", "Meridian Health"]},
        "starter_plan":     {"mrr":  2600, "customers": 3, "avg_arr": 10400,
                             "names": ["Veridian Co", "Fintex Ltd", "Vanta Partners"]},
        "legacy_orbits":    {"mrr":  1000, "customers": 1, "avg_arr": 12000,
                             "note": "Old annual plan — renewal negotiation Aug 2026"},
        "subtotal_mrr": 41200,
    },
    "professional_services": {
        "meridian_onboarding":  {"amount": 3500, "type": "one_time", "recognized_june": 1167},
        "apex_integration":     {"amount": 2000, "type": "one_time", "recognized_june": 2000},
        "subtotal_recognized": 3167,
    },
    "usage_overage": {
        "apex_systems": {"amount": 800, "overage_units": 4000, "rate_per_1k": 0.20},
        "subtotal": 800,
    },
    "total_recognized_revenue": 45167,
    "total_cash_collected": 68167,
}

# ── COGS Breakdown — June 2026 ─────────────────────────────────────────────────

COGS_BREAKDOWN_JUNE = {
    "cloud_infrastructure": {
        "aws_compute":  4200,
        "aws_rds":      1100,
        "aws_s3":        400,
        "cloudflare":    300,
        "subtotal":     6000,
    },
    "payment_processing": {
        "stripe_fees":   892,
        "subtotal":      892,
    },
    "customer_support": {
        "zendesk":       308,
        "cs_salary_alloc": 1800,
        "subtotal":     2108,
    },
    "devops_tools": {
        "datadog":       600,
        "github_actions": 200,
        "sentry":        200,
        "subtotal":     1000,
    },
    "total_cogs": 10000,
    "gross_margin_pct": 73.8,
}

# ── OpEx Breakdown — June 2026 ─────────────────────────────────────────────────

OPEX_BREAKDOWN_JUNE = {
    "research_and_development": {
        "engineering_salaries": 16000,
        "linear_figma_cursor":   1200,
        "subtotal":             17200,
        "pct_of_revenue":       40.95,
    },
    "sales_and_marketing": {
        "ae_salaries":          8000,
        "marketing_manager":    2917,
        "linkedin_google_ads":  1800,
        "hubspot_crm":           600,
        "apollo_loom_other":     400,
        "subtotal":            13717,
        "pct_of_revenue":      32.66,
        "pipeline_generated":  28000,
    },
    "general_and_administrative": {
        "ceo_cto_draws":        9333,
        "finance_ops":          2917,
        "csm_ga_alloc":         2083,
        "wework_rent":          4800,
        "carta":                1200,
        "notion":                240,
        "google_workspace":      180,
        "accounting_software":   120,
        "insurance":             800,
        "legal_misc":            400,
        "subtotal":            22073,
        "pct_of_revenue":      52.55,
    },
    "interest_expense": {
        "convertible_note": 3750,
        "subtotal":         3750,
    },
    "total_opex": 56740,
}

# ── Headcount — June 30 2026 ──────────────────────────────────────────────────

HEADCOUNT = [
    {"id": "HC001", "name": "Jordan Lee",  "title": "Co-founder / CEO",
     "dept": "G&A",        "level": "Executive",
     "salary_annual": 120000, "current_draw": 80000, "equity_pct": 28.0,
     "start_date": "2024-01-15", "location": "Remote — NYC"},
    {"id": "HC002", "name": "Sam Chen",    "title": "Co-founder / CTO",
     "dept": "Engineering","level": "Executive",
     "salary_annual": 130000, "current_draw": 90000, "equity_pct": 22.0,
     "start_date": "2024-01-15", "location": "Remote — SF"},
    {"id": "HC003", "name": "Priya Nair",  "title": "Sr. Software Engineer",
     "dept": "Engineering","level": "Senior",
     "salary_annual": 148000, "current_draw": 148000, "equity_pct": 0.80,
     "start_date": "2024-08-01", "location": "Remote — Austin"},
    {"id": "HC004", "name": "Alex Torres", "title": "Software Engineer",
     "dept": "Engineering","level": "Mid",
     "salary_annual": 118000, "current_draw": 118000, "equity_pct": 0.40,
     "start_date": "2025-03-01", "location": "Remote — Chicago"},
    {"id": "HC005", "name": "Marcus Webb", "title": "Software Engineer",
     "dept": "Engineering","level": "Mid",
     "salary_annual": 112000, "current_draw": 112000, "equity_pct": 0.35,
     "start_date": "2025-06-01", "location": "Remote — Miami"},
    {"id": "HC006", "name": "Tanya Blake", "title": "Account Executive",
     "dept": "Sales",      "level": "Mid",
     "salary_annual": 80000, "ote_annual": 160000, "current_draw": 80000,
     "commission_ytd": 18400, "equity_pct": 0.25,
     "start_date": "2025-09-01", "location": "Remote — NYC",
     "quota_annual": 480000, "quota_attainment_ytd_pct": 72},
    {"id": "HC007", "name": "Chris Nguyen","title": "Account Executive",
     "dept": "Sales",      "level": "Mid",
     "salary_annual": 80000, "ote_annual": 160000, "current_draw": 80000,
     "commission_ytd": 9200, "equity_pct": 0.20,
     "start_date": "2026-01-15", "location": "Remote — LA",
     "quota_annual": 480000, "quota_attainment_ytd_pct": 41},
    {"id": "HC008", "name": "Dana Kim",    "title": "Customer Success Manager",
     "dept": "G&A",        "level": "Mid",
     "salary_annual": 85000, "current_draw": 85000, "equity_pct": 0.20,
     "start_date": "2025-11-01", "location": "Remote — Seattle",
     "accounts_managed": 10, "nrr_owned_pct": 94},
    {"id": "HC009", "name": "Riley Ortiz", "title": "Finance & Operations",
     "dept": "G&A",        "level": "Mid",
     "salary_annual": 90000, "current_draw": 90000, "equity_pct": 0.15,
     "start_date": "2026-02-01", "location": "Remote — Denver"},
    {"id": "HC010", "name": "Morgan Shah", "title": "Marketing Manager",
     "dept": "Sales",      "level": "Mid",
     "salary_annual": 95000, "current_draw": 95000, "equity_pct": 0.18,
     "start_date": "2026-04-01", "location": "Remote — Boston"},
]

HEADCOUNT_SUMMARY = {
    "total": 10,
    "by_dept": {"Engineering": 5, "Sales": 3, "G&A": 2},
    "total_salary_annual": sum(h["salary_annual"] for h in HEADCOUNT),
    "avg_tenure_months": 16,
    "open_roles": 0,
}

# ── Planned Hires — H2 2026 ───────────────────────────────────────────────────

PLANNED_HIRES = [
    {"role": "Account Executive", "dept": "Sales", "count": 2,
     "target_start": "2026-09-01", "salary_annual": 80000, "ote_annual": 160000,
     "ramp_months": 3, "quota_annual": 480000,
     "monthly_cost_fully_loaded": 13333,
     "rationale": "Pipeline at $468k ARR needs more closers. Current AEs at capacity."},
    {"role": "Sr. Software Engineer", "dept": "Engineering", "count": 1,
     "target_start": "2026-10-01", "salary_annual": 150000,
     "ramp_months": 1, "monthly_cost_fully_loaded": 12500,
     "rationale": "Platform scaling ahead of Series A. Eng team at 90% capacity."},
    {"role": "Customer Success Manager", "dept": "G&A", "count": 1,
     "target_start": "2026-10-01", "salary_annual": 85000,
     "ramp_months": 2, "monthly_cost_fully_loaded": 7083,
     "rationale": "Dana Kim at 10 accounts — churn risk above $60k MRR without split."},
]

HIRING_SCENARIO = {
    "base_monthly_burn": 46750,
    "additional_burn_when_all_ramped": 32916,
    "new_monthly_burn": 79666,
    "runway_without_hires_months": 18.9,
    "runway_with_hires_months": 10.2,
    "ebitda_impact_dec_2026": -8500,
    "arr_uplift_by_dec_2026": 96000,
    "break_even_month": "2027-03",
}

# ── Sales Pipeline — as of June 30 2026 ──────────────────────────────────────

SALES_PIPELINE = [
    {"deal": "TechNova Corp",   "arr": 72000,  "stage": "Negotiation",   "close_date": "2026-07-15", "owner": "Tanya Blake",  "prob_pct": 80, "plan": "Enterprise"},
    {"deal": "Cirrus Systems",  "arr": 96000,  "stage": "Negotiation",   "close_date": "2026-07-22", "owner": "Jordan Lee",   "prob_pct": 70, "plan": "Enterprise"},
    {"deal": "Relay Health",    "arr": 48000,  "stage": "Proposal",      "close_date": "2026-07-30", "owner": "Chris Nguyen", "prob_pct": 60, "plan": "Growth"},
    {"deal": "Pulsar Bio",      "arr": 24000,  "stage": "Proposal",      "close_date": "2026-08-01", "owner": "Chris Nguyen", "prob_pct": 50, "plan": "Starter"},
    {"deal": "Vertex AI Co",    "arr": 36000,  "stage": "Demo",          "close_date": "2026-08-15", "owner": "Tanya Blake",  "prob_pct": 40, "plan": "Growth"},
    {"deal": "Momentum Labs",   "arr": 48000,  "stage": "Discovery",     "close_date": "2026-09-01", "owner": "Tanya Blake",  "prob_pct": 25, "plan": "Growth"},
    {"deal": "Fieldstone RE",   "arr": 24000,  "stage": "Discovery",     "close_date": "2026-09-15", "owner": "Chris Nguyen", "prob_pct": 20, "plan": "Starter"},
    {"deal": "Atlas Analytics", "arr": 120000, "stage": "Inbound — New", "close_date": "2026-10-01", "owner": "TBD",          "prob_pct": 15, "plan": "Enterprise"},
]

PIPELINE_SUMMARY = {
    "total_arr_pipeline": 468000,
    "weighted_arr": round(sum(d["arr"] * d["prob_pct"] / 100 for d in SALES_PIPELINE)),
    "avg_deal_size_arr": 58500,
    "avg_sales_cycle_days": 62,
    "pipeline_coverage_ratio": 3.7,   # weighted pipeline / quarterly ARR target
}

# ── Cohort Retention ──────────────────────────────────────────────────────────

COHORT_RETENTION = [
    {"cohort": "Jan 2025",  "initial_mrr": 6000,  "m1": 100, "m3": 95, "m6": 90, "m12": 88, "current_mrr": 9000,  "nrr": 150, "note": "Apex + Orbits — expansion via seat adds"},
    {"cohort": "Q2 2025",   "initial_mrr": 8000,  "m1": 100, "m3": 92, "m6": 88, "m12": 85, "current_mrr": 9200,  "nrr": 115},
    {"cohort": "Q3 2025",   "initial_mrr": 5000,  "m1": 100, "m3": 90, "m6": 82, "m12": None,"current_mrr": 4100,  "nrr":  82, "note": "Driftly churned — price sensitivity"},
    {"cohort": "Q4 2025",   "initial_mrr": 9000,  "m1": 100, "m3": 96, "m6": 94, "m12": None,"current_mrr": 10800, "nrr": 120},
    {"cohort": "Q1 2026",   "initial_mrr": 12000, "m1": 100, "m3": 98, "m6": None,"m12": None,"current_mrr": 12200, "nrr": 102},
    {"cohort": "Q2 2026",   "initial_mrr": 5800,  "m1": 100, "m3": None,"m6": None,"m12": None,"current_mrr": 5800,  "nrr": 100, "note": "Too early to measure"},
]

# ── CAC by Channel — H1 2026 ──────────────────────────────────────────────────

CAC_BY_CHANNEL = [
    {"channel": "Outbound SDR",      "customers_h1": 4, "spend_h1": 28000, "cac":  7000, "avg_arr": 52000, "ltv_cac": 5.6,  "payback_months": 5.2},
    {"channel": "Inbound / SEO",     "customers_h1": 3, "spend_h1":  8400, "cac":  2800, "avg_arr": 28800, "ltv_cac": 7.7,  "payback_months": 3.4},
    {"channel": "Founder-led",       "customers_h1": 3, "spend_h1":  4200, "cac":  1400, "avg_arr": 78000, "ltv_cac": 41.9, "payback_months": 0.7},
    {"channel": "Referral / WOM",    "customers_h1": 2, "spend_h1":  1000, "cac":   500, "avg_arr": 18000, "ltv_cac": 27.0, "payback_months": 1.1},
    {"channel": "Partner / Intro",   "customers_h1": 1, "spend_h1":  2000, "cac":  2000, "avg_arr": 72000, "ltv_cac": 27.0, "payback_months": 1.1},
]

# ── LTV by Segment ────────────────────────────────────────────────────────────

LTV_BY_SEGMENT = [
    {"segment": "Enterprise", "avg_mrr": 7200, "avg_arr": 86400, "gross_margin": 0.76, "monthly_churn": 0.012, "ltv": 456000, "cac": 18000, "ltv_cac": 25.3, "customers": 3},
    {"segment": "Growth",     "avg_mrr": 2667, "avg_arr": 32000, "gross_margin": 0.74, "monthly_churn": 0.022, "ltv":  89600, "cac":  8000, "ltv_cac": 11.2, "customers": 6},
    {"segment": "Starter",    "avg_mrr":  867, "avg_arr": 10400, "gross_margin": 0.70, "monthly_churn": 0.045, "ltv":  13500, "cac":  2500, "ltv_cac":  5.4, "customers": 3},
    {"segment": "Legacy",     "avg_mrr": 1000, "avg_arr": 12000, "gross_margin": 0.74, "monthly_churn": 0.010, "ltv":  74000, "cac":  3000, "ltv_cac": 24.7, "customers": 1},
]

# ── Forecast / Proforma — Jul–Dec 2026 ───────────────────────────────────────
# Base case: hires as planned, MRR growth ~8%/mo

FORECAST = [
    {
        "month": "Jul 2026", "period": "2026-07",
        "mrr": 45400, "arr": 544800,
        "new_mrr": 4200, "expansion_mrr": 600, "churned_mrr": -1400, "net_new_mrr": 3400,
        "customers": 15, "revenue_recognized": 45400,
        "cogs": 11800, "gross_profit": 33600, "gross_margin_pct": 74.0,
        "payroll_gross": 32000, "opex_total": 11200,
        "ebitda": 2400, "ebitda_margin_pct": 5.3,
        "cash": 199900, "notes": "TechNova close expected (80% prob, $72k ARR)",
    },
    {
        "month": "Aug 2026", "period": "2026-08",
        "mrr": 53000, "arr": 636000,
        "new_mrr": 8400, "expansion_mrr": 600, "churned_mrr": -1400, "net_new_mrr": 7600,
        "customers": 16, "revenue_recognized": 53000,
        "cogs": 13000, "gross_profit": 40000, "gross_margin_pct": 75.5,
        "payroll_gross": 32000, "opex_total": 11200,
        "ebitda": 16800, "ebitda_margin_pct": 31.7,
        "cash": 211800, "notes": "TechNova + Cirrus both in. Strong month.",
    },
    {
        "month": "Sep 2026", "period": "2026-09",
        "mrr": 61000, "arr": 732000,
        "new_mrr": 9000, "expansion_mrr": 1000, "churned_mrr": -1000, "net_new_mrr": 9000,
        "customers": 18, "revenue_recognized": 61000,
        "cogs": 14200, "gross_profit": 46800, "gross_margin_pct": 76.7,
        "payroll_gross": 43333, "opex_total": 12000,
        "ebitda": 20467, "ebitda_margin_pct": 33.6,
        "cash": 222600, "notes": "2 AEs start Sep 1 (+$13.3k/mo burn). No AE revenue yet.",
    },
    {
        "month": "Oct 2026", "period": "2026-10",
        "mrr": 66000, "arr": 792000,
        "new_mrr": 6000, "expansion_mrr": 1000, "churned_mrr": -2000, "net_new_mrr": 5000,
        "customers": 19, "revenue_recognized": 66000,
        "cogs": 15200, "gross_profit": 50800, "gross_margin_pct": 77.0,
        "payroll_gross": 62916, "opex_total": 12500,
        "ebitda": 11384, "ebitda_margin_pct": 17.2,
        "cash": 232100, "notes": "Sr Eng + CSM start. Burn spike. AEs still ramping.",
    },
    {
        "month": "Nov 2026", "period": "2026-11",
        "mrr": 72000, "arr": 864000,
        "new_mrr": 7000, "expansion_mrr": 1500, "churned_mrr": -2500, "net_new_mrr": 6000,
        "customers": 21, "revenue_recognized": 72000,
        "cogs": 16400, "gross_profit": 55600, "gross_margin_pct": 77.2,
        "payroll_gross": 62916, "opex_total": 12500,
        "ebitda": 16184, "ebitda_margin_pct": 22.5,
        "cash": 247100, "notes": "AEs closing first deals from own pipeline.",
    },
    {
        "month": "Dec 2026", "period": "2026-12",
        "mrr": 80000, "arr": 960000,
        "new_mrr": 10000, "expansion_mrr": 2000, "churned_mrr": -4000, "net_new_mrr": 8000,
        "customers": 23, "revenue_recognized": 80000,
        "cogs": 17800, "gross_profit": 62200, "gross_margin_pct": 77.8,
        "payroll_gross": 62916, "opex_total": 13000,
        "ebitda": 22284, "ebitda_margin_pct": 27.9,
        "cash": 267100, "notes": "$960k ARR. Series A fundraise begins. $1M ARR target by Jan 2027.",
    },
]

FORECAST_SUMMARY = {
    "arr_jun_2026":  504000,
    "arr_dec_2026":  960000,
    "arr_growth_h2_pct": 90.5,
    "cash_dec_2026": 267100,
    "runway_dec_2026_months": 6.7,
    "target_series_a_arr": 1000000,
    "projected_series_a_close": "2027-Q1",
    "key_risk": "Runway at 6.7mo by Dec — Series A must close by Mar 2027 or burn cut needed.",
    "key_milestone": "$1M ARR — Jan 2027 at current trajectory",
}

# ── Outstanding Vendor Bills (AP) ─────────────────────────────────────────────

OUTSTANDING_VENDOR_BILLS = [
    {"vendor": "Sidley LLP",      "amount": 4200, "due": "2026-07-10", "category": "Legal",     "status": "unpaid", "note": "Series A prep — should accrue in June"},
    {"vendor": "UX Contractor",   "amount": 2800, "due": "2026-07-05", "category": "R&D",       "status": "unpaid", "note": "Freelance design sprint Jun 15-30"},
    {"vendor": "AWS (duplicate)", "amount": 3200, "due": "2026-07-01", "category": "Infra",     "status": "unpaid", "note": "Duplicate entry — one must be voided"},
    {"vendor": "Zendesk",         "amount":  308, "due": "2026-07-08", "category": "Support",   "status": "unpaid"},
    {"vendor": "Datadog",         "amount":  600, "due": "2026-07-15", "category": "DevOps",    "status": "unpaid"},
]

OUTSTANDING_AP_TOTAL = sum(v["amount"] for v in OUTSTANDING_VENDOR_BILLS)

# ── Unit Economics Summary ─────────────────────────────────────────────────────

UNIT_ECONOMICS = {
    "avg_arr_per_customer":     36000,
    "avg_mrr_per_customer":      3000,
    "gross_margin_pct":          73.8,
    "monthly_churn_rate_pct":     2.4,
    "avg_customer_life_months":  41.7,
    "ltv":                      92250,
    "blended_cac":              20000,
    "ltv_cac_ratio":              4.6,
    "cac_payback_months":         9.1,
    "magic_number":               0.72,
    "rule_of_40":                14.3,   # MoM growth 10.5% + EBITDA margin 3.8%
    "nrr_pct":                   94.1,
    "gross_churn_arr_monthly":  12000,
    "expansion_arr_monthly":     6000,
    "net_churn_arr_monthly":    -6000,
}
