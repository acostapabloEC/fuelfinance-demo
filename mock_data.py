"""
Mock data layer — realistic early-stage SaaS company (B2B, ~$2M ARR)
Period: June 2026
"""
from data_extension import *  # historical, proforma, headcount, pipeline, cohorts

PERIOD = "June 2026"
COMPANY = "Acme SaaS Inc."

# ── Stripe ────────────────────────────────────────────────────────────────────

STRIPE_TRANSACTIONS = [
    {"id": "ch_001", "date": "2026-06-03", "amount": 12000.00, "type": "charge",   "customer": "Orbits Inc",      "status": "succeeded"},
    {"id": "ch_002", "date": "2026-06-04", "amount":  1200.00, "type": "charge",   "customer": "Bluewave LLC",    "status": "succeeded"},
    {"id": "ch_003", "date": "2026-06-05", "amount":  8000.00, "type": "charge",   "customer": "Apex Systems",    "status": "succeeded"},
    {"id": "ch_004", "date": "2026-06-07", "amount":  6000.00, "type": "charge",   "customer": "Novu Corp",       "status": "succeeded"},
    {"id": "ch_005", "date": "2026-06-10", "amount":  5600.00, "type": "charge",   "customer": "DataCore Inc",    "status": "succeeded"},
    {"id": "ch_006", "date": "2026-06-12", "amount":  4800.00, "type": "charge",   "customer": "Stackr Co",       "status": "succeeded"},
    {"id": "ch_007", "date": "2026-06-14", "amount":   800.00, "type": "charge",   "customer": "Fintex Ltd",      "status": "disputed"},
    {"id": "ch_008", "date": "2026-06-16", "amount":  3600.00, "type": "charge",   "customer": "Primex Tech",     "status": "succeeded"},
    {"id": "ch_009", "date": "2026-06-18", "amount":  3200.00, "type": "charge",   "customer": "Loopify Inc",     "status": "succeeded"},
    {"id": "ch_010", "date": "2026-06-20", "amount":  2400.00, "type": "charge",   "customer": "Clearpath AI",    "status": "succeeded"},
    {"id": "ch_011", "date": "2026-06-22", "amount":  2400.00, "type": "charge",   "customer": "Heliosoft",       "status": "succeeded"},
    {"id": "ch_012", "date": "2026-06-24", "amount":  1200.00, "type": "charge",   "customer": "Veridian Co",     "status": "succeeded"},
    {"id": "re_001", "date": "2026-06-20", "amount":  -600.00, "type": "refund",   "customer": "Orbits Inc",      "status": "succeeded"},
]

STRIPE_FEES_TOTAL     = 892.00   # processing fees for the month
STRIPE_GROSS          = sum(t["amount"] for t in STRIPE_TRANSACTIONS if t["amount"] > 0)
STRIPE_NET_DEPOSITED  = STRIPE_GROSS - STRIPE_FEES_TOTAL + sum(t["amount"] for t in STRIPE_TRANSACTIONS if t["amount"] < 0)

STRIPE_PAYOUTS = [
    {"date": "2026-06-05", "amount": 4180.00,  "period_charges": ["ch_001_partial", "ch_002"]},
    {"date": "2026-06-12", "amount": 3491.00,  "period_charges": ["ch_003"]},
    {"date": "2026-06-19", "amount": 2330.00,  "period_charges": ["ch_005"]},
    {"date": "2026-06-26", "amount": 5808.00,  "period_charges": ["ch_006", "ch_007"]},
    # ch_001 partial ($7,820) crosses into July — period mismatch
]

# ── QuickBooks ─────────────────────────────────────────────────────────────────

QB_REVENUE_ENTRIES = [
    {"date": "2026-06-03", "amount": 12000.00, "account": "Revenue",          "memo": "Orbits Inc — annual contract (12 mo prepay)",   "entry_type": "invoice"},
    {"date": "2026-06-04", "amount":  1200.00, "account": "Revenue",          "memo": "Bluewave LLC — monthly",                        "entry_type": "invoice"},
    {"date": "2026-06-05", "amount":  8000.00, "account": "Revenue",          "memo": "Apex Systems — monthly",                        "entry_type": "invoice"},
    {"date": "2026-06-07", "amount":  6000.00, "account": "Revenue",          "memo": "Novu Corp — monthly",                           "entry_type": "invoice"},
    {"date": "2026-06-10", "amount": 16800.00, "account": "Revenue",          "memo": "DataCore Inc — quarterly prepay (3 mo)",        "entry_type": "invoice"},
    {"date": "2026-06-12", "amount":  4800.00, "account": "Revenue",          "memo": "Stackr Co — monthly",                           "entry_type": "invoice"},
    {"date": "2026-06-16", "amount":  3600.00, "account": "Revenue",          "memo": "Primex Tech — monthly",                         "entry_type": "invoice"},
    {"date": "2026-06-18", "amount":  3200.00, "account": "Revenue",          "memo": "Loopify Inc — monthly",                         "entry_type": "invoice"},
    {"date": "2026-06-20", "amount":  2400.00, "account": "Revenue",          "memo": "Clearpath AI — monthly",                        "entry_type": "invoice"},
    {"date": "2026-06-22", "amount":  2400.00, "account": "Revenue",          "memo": "Heliosoft — monthly",                           "entry_type": "invoice"},
    {"date": "2026-06-24", "amount":  1200.00, "account": "Revenue",          "memo": "Veridian Co — monthly",                         "entry_type": "invoice"},
    # NOTE: ch_007 ($800 disputed Fintex) has NO reversal in QB
    # NOTE: re_001 ($600 refund) has NO reversal in QB
    # NOTE: Stripe fees are NOT recorded anywhere — netted from deposit
    # NOTE: Orbits $11,000 NOT moved to Deferred Revenue in QB — booked as revenue
    # NOTE: DataCore $11,200 NOT moved to Deferred Revenue in QB — booked as revenue
]

QB_REVENUE_TOTAL = 64200.00  # cash collected June — OVERSTATED; includes $22,200 of prepaid unearned revenue

QB_DEFERRED_REVENUE_BALANCE = 0.00  # should be 6000 (Orbits annual — 6 months remaining)

QB_AR_AGING = [
    {"customer": "Driftly Co",    "invoice": "INV-0441", "amount": 2400.00,  "days_overdue": 47, "status": "open"},
    {"customer": "Prism Labs",    "invoice": "INV-0448", "amount": 1200.00,  "days_overdue": 33, "status": "open"},
    {"customer": "Fintex Ltd",    "invoice": "INV-0451", "amount":  800.00,  "days_overdue": 31, "status": "open"},
    {"customer": "Stackr Co",     "invoice": "INV-0462", "amount": 2400.00,  "days_overdue":  5, "status": "open"},
    {"customer": "Loopify Inc",   "invoice": "INV-0470", "amount": 4800.00,  "days_overdue":  0, "status": "open"},
]

QB_LAST_RECONCILIATION_DATE = "2026-05-12"  # 34 days ago — warn threshold is 30

QB_EXPENSES = [
    {"date": "2026-06-01", "vendor": "AWS",           "amount": 3200.00, "account": "G&A - Software"},
    {"date": "2026-06-01", "vendor": "AWS",           "amount": 3200.00, "account": "G&A - Software"},  # duplicate
    {"date": "2026-06-05", "vendor": "Notion",        "amount":  240.00, "account": "G&A - Software"},
    {"date": "2026-06-10", "vendor": "Gusto",         "amount": 28000.00,"account": "Payroll"},
    {"date": "2026-06-15", "vendor": "Stripe",        "amount":   892.00,"account": "Revenue"},         # fees netted against revenue
    {"date": "2026-06-20", "vendor": "WeWork",        "amount":  4800.00,"account": "G&A - Rent"},
    {"date": "2026-06-28", "vendor": "Carta",         "amount":  1200.00,"account": "G&A - Legal"},
]

QB_ACCRUED_LIABILITIES = 0.00   # should have wages payable and accrued expenses
QB_PREPAID_BALANCE     = 8400.00
QB_PREPAID_MOVEMENT    = 0.00   # hasn't moved — amortization stopped

# COGS: hosting ($4,500) + Stripe processing ($892) + support allocation ($2,608)
# Reclassified from G&A/OpEx — EBITDA unchanged, gross margin visible
QB_COGS_JUNE           = 11000.00   # hosting $6k + Stripe fees $1.1k + support allocation $3.9k
QB_GROSS_PROFIT        = QB_REVENUE_TOTAL - QB_COGS_JUNE   # 53,200 cash-basis (overstated); 31,000 accrual

# ── Plan vs Actuals (Budget) ──────────────────────────────────────────────────

PLAN_REVENUE_JUNE       = 48000.00   # budgeted revenue
PLAN_PAYROLL_JUNE       = 45000.00   # budgeted payroll (gross)
PLAN_OTHER_OPEX_JUNE    =  8500.00   # budgeted non-payroll opex

# ── Prior Year (June 2025) ────────────────────────────────────────────────────

PRIOR_YEAR_REVENUE      = 18500.00
PRIOR_YEAR_PAYROLL      = 35000.00
PRIOR_YEAR_OTHER_OPEX   =  6200.00

# ── Prior Month (May 2026) ────────────────────────────────────────────────────

PRIOR_MONTH_REVENUE     = 22800.00
PRIOR_MONTH_PAYROLL     = 47000.00

# ── Cash & Runway ─────────────────────────────────────────────────────────────

CASH_ON_HAND            = 185000.00
MONTHLY_GROSS_BURN      =  46750.00  # total cash out (payroll $32k + COGS $8k + OpEx $3k + interest $3,750)
MONTHLY_NET_BURN        =  28750.00  # gross burn minus normalized MRR ($18,000)

# ── HubSpot ───────────────────────────────────────────────────────────────────

HUBSPOT_CLOSED_WON = [
    {"deal": "Orbits Inc expansion",  "close_date": "2026-06-01", "amount": 12000.00, "invoiced_in_qb": True},
    {"deal": "Bluewave renewal",      "close_date": "2026-06-04", "amount":  1200.00, "invoiced_in_qb": True},
    {"deal": "Novu Corp new",         "close_date": "2026-06-09", "amount":  3600.00, "invoiced_in_qb": True},
    {"deal": "Stackr Co new",         "close_date": "2026-06-17", "amount":  2400.00, "invoiced_in_qb": True},
    {"deal": "Loopify Inc expansion", "close_date": "2026-06-21", "amount":  4800.00, "invoiced_in_qb": True},
    {"deal": "Meridian Health",       "close_date": "2026-06-24", "amount":  3600.00, "invoiced_in_qb": False},  # never invoiced
    {"deal": "Vanta Partners",        "close_date": "2026-06-28", "amount":  1800.00, "invoiced_in_qb": False},  # never invoiced
]

# ── Gusto ─────────────────────────────────────────────────────────────────────

GUSTO_PAYROLL = [
    {
        "run_date":     "2026-06-10",
        "gross_payroll": 32000.00,
        "net_payroll":   28000.00,   # what actually hit bank accounts
        "employer_taxes":  2600.00,
        "benefits":        1400.00,
        "headcount":          10,
        "departments": {
            "Engineering": 16000.00,
            "Sales":        8000.00,
            "G&A":          8000.00,
        }
    }
]

# QB only recorded net pay ($28,000) — missing employer taxes + benefits ($4,000)
QB_PAYROLL_RECORDED = 28000.00
GUSTO_GROSS_TOTAL   = 32000.00

# Payroll not split by department in QB — all sits in one "Payroll" account
QB_PAYROLL_SPLIT    = False

# ── Carta ─────────────────────────────────────────────────────────────────────

CARTA_CAP_TABLE = {
    "last_updated":     "2026-04-30",
    "total_shares":      10_000_000,
    "option_pool":        1_500_000,
    "latest_409a_date": "2025-11-15",
    "convertible_notes": [
        {"investor": "Seed Fund I",  "amount": 500000, "interest_rate": 0.06, "maturity": "2027-03-01"},
        {"investor": "Angel Group",  "amount": 250000, "interest_rate": 0.06, "maturity": "2027-03-01"},
    ],
    "accrued_interest_in_qb": False,   # interest not being accrued monthly
}

# ── SaaS Metrics ──────────────────────────────────────────────────────────────

CUSTOMER_ROSTER = [
    {"name": "Apex Systems",    "mrr": 8000.00, "since": "2025-09-01", "plan": "Enterprise", "active": True},
    {"name": "Novu Corp",       "mrr": 6000.00, "since": "2026-03-01", "plan": "Enterprise", "active": True},
    {"name": "DataCore Inc",    "mrr": 5600.00, "since": "2025-11-01", "plan": "Enterprise", "active": True},
    {"name": "Stackr Co",       "mrr": 4800.00, "since": "2026-04-01", "plan": "Growth",     "active": True},
    {"name": "Primex Tech",     "mrr": 3600.00, "since": "2026-02-01", "plan": "Growth",     "active": True},
    {"name": "Loopify Inc",     "mrr": 3200.00, "since": "2026-05-01", "plan": "Growth",     "active": True},
    {"name": "Clearpath AI",    "mrr": 2400.00, "since": "2026-02-01", "plan": "Growth",     "active": True},
    {"name": "Heliosoft",       "mrr": 2400.00, "since": "2026-04-01", "plan": "Growth",     "active": True},
    {"name": "Orbits Inc",      "mrr": 1000.00, "since": "2025-01-01", "plan": "Enterprise", "active": True},
    {"name": "Bluewave LLC",    "mrr": 1200.00, "since": "2025-08-01", "plan": "Growth",     "active": True},
    {"name": "Veridian Co",     "mrr": 1200.00, "since": "2026-04-01", "plan": "Starter",    "active": True},
    {"name": "Meridian Health", "mrr": 1200.00, "since": "2026-06-24", "plan": "Growth",     "active": True},
    {"name": "Fintex Ltd",      "mrr":  800.00, "since": "2026-06-01", "plan": "Starter",    "active": True},
    {"name": "Vanta Partners",  "mrr":  600.00, "since": "2026-06-28", "plan": "Starter",    "active": True},
]

CHURNED_THIS_MONTH = [
    {"name": "Driftly Co", "mrr": 900.00, "churned_date": "2026-06-15", "reason": "Went to competitor on price"},
]

NEW_CUSTOMERS_THIS_MONTH = [
    {"name": "Meridian Health", "mrr": 1200.00, "signed_date": "2026-06-24", "plan": "Growth"},
    {"name": "Vanta Partners",  "mrr":  600.00, "signed_date": "2026-06-28", "plan": "Starter"},
]

MRR_PRIOR_MONTH    = 38000.00   # May 2026
EXPANSION_MRR      =  2500.00   # Apex upsell + DataCore seat expansion
CHURNED_MRR        =  1000.00   # Driftly churned Jun 15
NEW_MRR            =  4500.00   # Meridian Health + Vanta Partners + Heliosoft
MRR_CURRENT        = 44000.00                                                   # 44,000 (38,000 + 4,500 + 2,500 - 1,000)
ARR_CURRENT        = MRR_CURRENT * 12                                           # 528,000

ACTIVE_CUSTOMERS   = len(CUSTOMER_ROSTER)   # 14
LOGO_COUNT_PRIOR   = 13                     # May (Driftly was active)

# CAC
SALES_MARKETING_SPEND_JUNE = 8000.00        # sales salary allocation
NEW_CUSTOMERS_JUNE         = 2             # Clearpath AI + Veridian Co
CAC                        = SALES_MARKETING_SPEND_JUNE / NEW_CUSTOMERS_JUNE   # 4,000

# LTV
GROSS_MARGIN_PCT          = 0.778   # MRR-basis: ($44,000 MRR - $9,800 COGS) / $44,000
GROSS_MARGIN_PCT_CASH_BASIS = 0.810  # cash-basis (QB booked)
CHURN_RATE_PCT      = 0.015                  # 1.5% monthly churn
MONTHLY_CHURN_RATE  = CHURN_RATE_PCT
AVG_MRR_PER_CUSTOMER = 3143.00              # $44,000 / 14 customers
ARPU                = MRR_CURRENT / ACTIVE_CUSTOMERS  # 3,143/mo
LTV                 = 163000.00             # (3,143 * 0.778) / 0.015
LTV_CAC_RATIO       = 5.5                   # LTV / blended CAC $29,600
CAC_PAYBACK_MONTHS  = 8.1                   # $29,600 CAC / ($3,143 * 77.8% margin)

# NRR
NRR_PCT             = 1.082                  # 108.2% — expansion beats churn
NRR                 = NRR_PCT

# MoM growth
MOM_MRR_GROWTH      = (MRR_CURRENT - MRR_PRIOR_MONTH) / MRR_PRIOR_MONTH  # 10.5%

# MRR bridge
MRR_PREV            = 38000.00
MRR_NEW_BIZ         =  4500.00
MRR_EXPANSION       =   500.00
MRR_CHURN           = -1000.00

# Deferred revenue — must be on balance sheet (NEITHER recorded in QB — both errors)
QB_DEFERRED_REVENUE_LOOPIFY = 0.00       # Loopify is now monthly, no deferred
QB_DEFERRED_REVENUE_ORBITS  = 11000.00  # $12,000 annual renewed Jun — 11 months remaining ($1k recognized)
QB_DEFERRED_REVENUE_DATACORP = 11200.00 # $16,800 quarterly prepay — 2 months remaining ($5.6k recognized)
QB_DEFERRED_REVENUE_TOTAL   = 22200.00  # total unearned — should be on balance sheet; QB shows $0

# Cash / burn (normalized recurring basis)
NORMALIZED_MONTHLY_CASH_IN  = 44000.00  # normalized MRR (accrual basis)
REAL_GROSS_BURN             = 43800.00  # payroll($30k) + COGS($9.8k) + OpEx($4k)
REAL_NET_BURN               =      0.00 # breakeven — cash flow positive in June
REAL_RUNWAY_MONTHS          = 24.0      # $240,000 / $10,000 blended (incl AR timing)
STATED_RUNWAY_MONTHS        = 24.0
CASH_NET_BURN_WITH_AR       = 10000.00  # conservative incl AR collection delays

# ── Balance Sheet ─────────────────────────────────────────────────────────────

BS_CASH                     = 240000.00
BS_AR                       =  11400.00   # open invoices per aging
BS_PREPAID                  =   8400.00
BS_SECURITY_DEPOSIT         =   4800.00   # WeWork
BS_TOTAL_ASSETS             = 209600.00

# Liabilities as booked (errors shown separately)
BS_DEFERRED_REVENUE_BOOKED  =      0.00   # ERROR — should be 6,000
BS_ACCRUED_LIABILITIES      =      0.00   # ERROR — should be 4,000
BS_AP                       =      0.00   # ERROR — vendors unpaid
BS_NOTE_A                   = 500000.00
BS_NOTE_B                   = 250000.00
BS_ACCRUED_INTEREST_BOOKED  =      0.00   # ERROR — 3,750/mo not accrued
BS_TOTAL_LIABILITIES_BOOKED = 750000.00
BS_ACCUMULATED_DEFICIT      = -540400.00  # plug: 209,600 - 750,000
BS_TOTAL_EQUITY             = -540400.00

# Cash flow — June 2026
CF_NET_INCOME               =  -3750.00   # net loss after interest ($42k MRR - $11k COGS - $28k payroll - $3k OpEx - $3,750 interest = -$750; rounded)
CF_DEFERRED_REV_INCREASE    =  22200.00   # cash in for future services (Orbits $11k + DataCore $11.2k)
CF_AR_INCREASE              = -26200.00   # billed not yet collected (AR outstanding at month end)
CF_ACCRUED_LIAB_INCREASE    =   4000.00   # payroll taxes owed not recorded
CF_OPERATING                =  -3750.00   # net operating cash flow (-3,750 + 22,200 - 26,200 + 4,000)
CF_INVESTING                =      0.00
CF_FINANCING                =      0.00
CF_NET_CHANGE               =  -3750.00
CF_BEGINNING_CASH           = 188750.00
CF_ENDING_CASH              = 185000.00
