"""
Fuel MCP — FastAPI backend
Routes:
  GET  /         -> chat UI
  GET  /metrics  -> KPI data
  GET  /context  -> full data context for AI
  POST /ask      -> AI answer from live data
  POST /run      -> SSE check stream (kept for export compatibility)
  GET  /report   -> last saved report
"""

import json, asyncio, os
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")  # local dev
load_dotenv()  # Railway / production (env vars already set)

import sys
sys.path.insert(0, str(Path(__file__).parent))
from checks.engine import run_all_checks, compute_score

app = FastAPI()

REPORTS_DIR = Path(__file__).parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)
STATIC_DIR  = Path(__file__).parent / "static"

_cached_report = None


# ── Startup: run checks once, cache results ───────────────────────────────────

@app.on_event("startup")
async def startup():
    global _cached_report
    results = await asyncio.to_thread(run_all_checks)
    score   = compute_score(results)
    counts  = {s: sum(1 for r in results if r["status"] == s) for s in ["pass","warn","fail"]}
    _cached_report = {
        "period":  "June 2026",
        "company": "Acme SaaS Inc.",
        "run_at":  datetime.now().isoformat(),
        "score":   score,
        "counts":  counts,
        "results": results,
    }
    report_path = REPORTS_DIR / "latest.json"
    report_path.write_text(json.dumps(_cached_report, indent=2), encoding="utf-8")


def get_report():
    if _cached_report:
        return _cached_report
    p = REPORTS_DIR / "latest.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


# ── Serve UI ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return HTMLResponse(
        content=(STATIC_DIR / "index.html").read_text(encoding="utf-8"),
        headers={"Content-Type": "text/html; charset=utf-8"}
    )


# ── Metrics ───────────────────────────────────────────────────────────────────

@app.get("/metrics")
async def get_metrics():
    import mock_data as md
    return JSONResponse({
        "mrr": md.MRR_CURRENT, "arr": md.ARR_CURRENT,
        "mrr_prior": md.MRR_PRIOR_MONTH,
        "mom_growth": round(md.MOM_MRR_GROWTH * 100, 1),
        "new_mrr": md.NEW_MRR, "expansion_mrr": md.EXPANSION_MRR,
        "churned_mrr": md.CHURNED_MRR,
        "nrr": round(md.NRR * 100, 1),
        "active_customers": md.ACTIVE_CUSTOMERS,
        "ltv_cac": round(md.LTV_CAC_RATIO, 1),
        "cac_payback": round(md.CAC_PAYBACK_MONTHS, 1),
        "monthly_churn": round(md.MONTHLY_CHURN_RATE * 100, 1),
        "gross_margin": round(md.GROSS_MARGIN_PCT * 100, 1),
        "cash": md.BS_CASH,
        "runway": md.REAL_RUNWAY_MONTHS,
        "roster": md.CUSTOMER_ROSTER,
        "churned": md.CHURNED_THIS_MONTH,
        "new_customers": md.NEW_CUSTOMERS_THIS_MONTH,
        "history": md.MONTHLY_HISTORY,
        "forecast": md.FORECAST,
        "pipeline": md.SALES_PIPELINE,
        "pipeline_summary": md.PIPELINE_SUMMARY,
        "headcount": md.HEADCOUNT,
        "headcount_summary": md.HEADCOUNT_SUMMARY,
        "planned_hires": md.PLANNED_HIRES,
        "hiring_scenario": md.HIRING_SCENARIO,
        "unit_economics": md.UNIT_ECONOMICS,
        "cohort_retention": md.COHORT_RETENTION,
        "cac_by_channel": md.CAC_BY_CHANNEL,
        "ltv_by_segment": md.LTV_BY_SEGMENT,
        "forecast_summary": md.FORECAST_SUMMARY,
    })


@app.get("/report")
async def get_report_endpoint():
    r = get_report()
    if not r:
        return JSONResponse({"error": "No report yet."}, status_code=404)
    return JSONResponse(r)


# ── SSE run (kept for export) ─────────────────────────────────────────────────

@app.post("/run")
async def run_checks_sse():
    async def event_stream():
        for system in ["Stripe","QuickBooks","Gusto","HubSpot","Carta"]:
            await asyncio.sleep(0.1)
            yield f"data: {json.dumps({'type':'connect','system':system})}\n\n"
        r = get_report()
        if r:
            for res in r["results"]:
                await asyncio.sleep(0.2)
                yield f"data: {json.dumps({'type':'check','result':res})}\n\n"
            yield f"data: {json.dumps({'type':'score','score':r['score'],'counts':r['counts']})}\n\n"
        yield 'data: {"type":"done"}\n\n'
    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── Ask ────────────────────────────────────────────────────────────────────────

class AskRequest(BaseModel):
    question: str


@app.post("/ask")
async def ask(req: AskRequest):
    import mock_data as md

    report  = get_report()
    q       = req.question.lower().strip()

    # Always available
    results = report["results"] if report else []
    counts  = report["counts"]  if report else {"fail": 0, "warn": 0, "pass": 0}
    fails   = [r for r in results if r["status"] == "fail"]
    warns   = [r for r in results if r["status"] == "warn"]

    def bullets(detail):
        parts = [p.strip() for p in detail.split(" | ") if p.strip()]
        return "\n".join(f"  • {p}" for p in parts) if len(parts) > 1 else f"  {detail}"

    # ── Pre-wired answers ──────────────────────────────────────────────────────

    if any(w in q for w in ["ready to raise", "raise", "fundrais", "series a", "investor ready"]):
        answer = (
            "## Almost — 3–4 weeks of cleanup stands between you and investor-ready books.\n\n"
            "### The business is strong\n"
            "• ARR $528k growing 15.8% MoM · 14 logos · 77.8% gross margin\n"
            "• NRR 108.2% — expansion is outpacing churn\n"
            "• 5.5x LTV:CAC · 24 months runway · Cash flow breakeven\n\n"
            "### The books have 5 open issues\n"
            "• $22,200 booked as revenue — should be Deferred (Orbits $11k + DataCore $11.2k)\n"
            "• $5,400 in closed deals never invoiced (Meridian Health + Vanta Partners)\n"
            "• $11.1k in unpaid vendor bills not in AP\n"
            "• Payroll not split by department — gross margin by function is invisible\n"
            "• Convertible note interest not being accrued monthly\n\n"
            "### This week's action list\n"
            "1. Book the $22,200 deferred revenue entry\n"
            "2. Send invoices to Meridian Health and Vanta Partners\n"
            "3. Load vendor bills into QB AP\n"
            "4. Split payroll by department in Gusto → QB\n\n"
            "Fix those and the financials match the business. The story is already there."
        )

    elif any(w in q for w in ["hire 2", "2 ae", "2 aes", "hiring", "hire", "headcount", "fte", "engineer"]):
        scenario = md.HIRING_SCENARIO
        answer = (
            "Hiring scenario: 2 AEs (Sep 1) + 1 Sr Engineer + 1 CSM (Oct 1)\n\n"
            "Impact on burn:\n"
            f"  • Current monthly burn: ${scenario['base_monthly_burn']:,.0f}\n"
            f"  • Additional when all ramped: +${scenario['additional_burn_when_all_ramped']:,.0f}/mo\n"
            f"  • New monthly burn: ${scenario['new_monthly_burn']:,.0f}/mo\n\n"
            "Impact on runway:\n"
            f"  • Without hires: {scenario['runway_without_hires_months']} months\n"
            f"  • With hires: {scenario['runway_with_hires_months']} months\n\n"
            "Revenue upside:\n"
            f"  • AEs take ~3 months to ramp\n"
            f"  • Projected ARR uplift by Dec 2026: +${scenario['arr_uplift_by_dec_2026']:,.0f}\n"
            f"  • Estimated EBITDA by Dec 2026: ${scenario['ebitda_impact_dec_2026']:,} (improving as AEs close)\n\n"
            "Bottom line: runway compresses from 18.9 to 10.2 months. "
            "The hires make sense only if you're closing a Series A by Q1 2027 — which is the plan at $960k ARR by Dec."
        )

    elif any(w in q for w in ["mrr trend", "trend", "6 month", "six month", "history", "historical", "last 6"]):
        hist = md.MONTHLY_HISTORY
        months_h = [h['month'].replace(" 2026","") for h in hist]
        col_h = "| | " + " | ".join(months_h) + " |\n"
        col_s = "|---|" + "|".join(["---:" for _ in hist]) + "|\n"
        def hrow(label, vals): return f"| {label} | " + " | ".join(vals) + " |\n"
        answer = (
            "## MRR Trend — Jan to Jun 2026\n\n"
            + col_h + col_s
            + hrow("MRR",          [f"${h['mrr']/1000:.0f}k"  for h in hist])
            + hrow("ARR",          [f"${h['arr']/1000:.0f}k"  for h in hist])
            + hrow("Customers",    [str(h['customers'])        for h in hist])
            + hrow("Gross Margin", [f"{h['gross_margin_pct']}%" for h in hist])
            + hrow("EBITDA",       [f"{'+' if h['ebitda']>=0 else ''}${h['ebitda']:,}" for h in hist])
            + "\n### Key takeaways\n"
            "• MRR grew **144%** in H1 — from $18k to $44k in 6 months\n"
            "• MoM growth avg ~18% early, stabilizing to 15.8% as base grows\n"
            "• Gross margin expanded **62.2% → 77.8%** as revenue scales into fixed infra costs\n"
            "• EBITDA trajectory: from −$1k in Jan to **breakeven** in June — ahead of plan"
        )
        chart = {
            "type": "bar",
            "title": "MRR — Jan to Jun 2026",
            "labels": [h["month"] for h in hist],
            "datasets": [
                {"label": "MRR", "values": [h["mrr"] for h in hist], "color": "#7c6fff"},
                {"label": "Gross Profit", "values": [round(h["mrr"] * h["gross_margin_pct"] / 100) for h in hist], "color": "#4ade80"},
            ],
            "yformat": "$k",
        }

    elif any(w in q for w in ["forecast", "proforma", "pro forma", "year end", "h2", "second half", "dec 2026", "by december"]):
        fc = md.FORECAST
        fs = md.FORECAST_SUMMARY
        months = [f['month'] for f in fc]
        col_header = "| | " + " | ".join(m.replace(" 2026","") for m in months) + " |\n"
        col_sep    = "|---|" + "|".join(["---:" for _ in months]) + "|\n"
        def frow(label, vals): return f"| {label} | " + " | ".join(vals) + " |\n"
        answer = (
            "## Forecast — Jul to Dec 2026\n\n"
            + col_header + col_sep
            + frow("MRR",          [f"${f['mrr']/1000:.0f}k"  for f in fc])
            + frow("ARR",          [f"${f['arr']/1000:.0f}k"  for f in fc])
            + frow("Gross Burn",   ["$43.8k" for _ in fc])
            + frow("EBITDA",       [f"{'+' if f['ebitda']>=0 else ''}${f['ebitda']/1000:.1f}k" for f in fc])
            + frow("EBITDA Margin",[f"{f['ebitda_margin_pct']}%" for f in fc])
            + frow("Cash",         [f"${f['cash']/1000:.0f}k"  for f in fc])
            + f"\n### Key milestones\n"
            f"• ARR Jun 2026: **${fs['arr_jun_2026']:,.0f}**\n"
            f"• ARR Dec 2026: **${fs['arr_dec_2026']:,.0f}** ({fs['arr_growth_h2_pct']}% H2 growth)\n"
            f"• $1M ARR: **{fs['key_milestone']}**\n"
            f"• Cash Dec 2026: **${fs['cash_dec_2026']:,.0f}** ({fs['runway_dec_2026_months']:.1f} months runway)\n\n"
            f"### Risk\n"
            f"• {fs['key_risk']}"
        )
        chart = {
            "type": "line",
            "title": "MRR Forecast — Jul to Dec 2026",
            "labels": [f["month"] for f in fc],
            "datasets": [
                {"label": "MRR", "values": [f["mrr"] for f in fc], "color": "#7c6fff"},
                {"label": "Cash", "values": [f["cash"] for f in fc], "color": "#4ade80"},
            ],
            "yformat": "$k",
        }

    elif any(w in q for w in ["pipeline", "deals", "sales", "funnel", "open deals"]):
        pipe = md.SALES_PIPELINE
        ps   = md.PIPELINE_SUMMARY
        rows = "\n".join(
            f"  {d['deal']:18s}  ${d['arr']:>7,.0f} ARR  {d['stage']:15s}  {d['prob_pct']}%  Close {d['close_date']}  Owner: {d['owner']}"
            for d in pipe
        )
        answer = (
            f"Sales pipeline — as of Jun 30 2026:\n\n"
            f"{rows}\n\n"
            f"Total pipeline ARR: ${ps['total_arr_pipeline']:,.0f}\n"
            f"Weighted ARR: ${ps['weighted_arr']:,.0f}\n"
            f"Pipeline coverage ratio: {ps['pipeline_coverage_ratio']}x\n"
            f"Avg deal size: ${ps['avg_deal_size_arr']:,.0f} ARR · Avg sales cycle: {ps['avg_sales_cycle_days']} days\n\n"
            f"If TechNova ($72k ARR, 80%) and Cirrus ($96k ARR, 70%) both close in July, "
            f"ARR jumps to $672k — puts $1M ARR in sight by Oct without new hires."
        )
        chart = {
            "type": "hbar",
            "title": "Open Pipeline by Deal (ARR)",
            "labels": [d["deal"] for d in pipe],
            "datasets": [{
                "label": "ARR",
                "values": [d["arr"] for d in pipe],
                "colors": ["#7c6fff" if d["prob_pct"] >= 60 else "#fbbf24" if d["prob_pct"] >= 30 else "#5a5a7a" for d in pipe],
                "pcts": [d["prob_pct"] for d in pipe],
            }],
            "yformat": "$k",
        }

    elif any(w in q for w in ["churn risk", "at risk", "churn", "retention", "cohort", "nrr"]):
        cohorts = md.COHORT_RETENTION
        def risk_flag(c):
            nrr = float(str(c['nrr']).replace('%',''))
            if nrr < 90: return "🔴 At risk"
            if nrr < 105: return "🟡 Watch"
            return "🟢 Healthy"
        header = (
            "## Cohort Retention & Churn Risk\n\n"
            "| Cohort | Starting MRR | Current MRR | NRR | Status | Note |\n"
            "|--------|------------:|------------:|----:|--------|------|\n"
        )
        rows = "\n".join(
            f"| {c['cohort']} | ${c['initial_mrr']:,} | ${c['current_mrr']:,} | **{c['nrr']}%** | {risk_flag(c)} | {c.get('note', '—')} |"
            for c in cohorts
        )
        answer = (
            header + rows + "\n\n"
            "### At-risk signals\n"
            "• Q3 2025 cohort NRR 82% — Driftly churned (price sensitivity). Watch **Fintex** ($800/mo, same profile)\n"
            "• Dana Kim manages all 10 accounts solo — above $60k MRR this becomes a single point of failure\n"
            "• Orbits renewal negotiation due **Aug 2026** — annual prepay relationship at risk\n\n"
            "### Positive signals\n"
            "• Jan 2025 cohort at **150% NRR** — expansion from Apex + Orbits seat adds\n"
            "• Q4 2025 at **120% NRR** — healthy upsell motion emerging across newer cohorts"
        )

    elif any(w in q for w in ["gross margin", "cogs", "cost of goods", "cost of revenue"]):
        cogs = md.COGS_BREAKDOWN_JUNE
        answer = (
            "## COGS Breakdown — June 2026\n\n"
            "| Category | Item | Amount |\n"
            "|----------|------|-------:|\n"
            f"| Cloud Infra | AWS Compute | ${cogs['cloud_infrastructure']['aws_compute']:,} |\n"
            f"| Cloud Infra | AWS RDS | ${cogs['cloud_infrastructure']['aws_rds']:,} |\n"
            f"| Cloud Infra | AWS S3 | ${cogs['cloud_infrastructure']['aws_s3']:,} |\n"
            f"| Cloud Infra | Cloudflare | ${cogs['cloud_infrastructure']['cloudflare']:,} |\n"
            f"| **Cloud Infra Total** | | **${cogs['cloud_infrastructure']['subtotal']:,}** |\n"
            f"| Payment Processing | Stripe Fees | ${cogs['payment_processing']['stripe_fees']:,} |\n"
            f"| Customer Support | Zendesk | ${cogs['customer_support']['zendesk']:,} |\n"
            f"| Customer Support | CS Salary Alloc | ${cogs['customer_support']['cs_salary_alloc']:,} |\n"
            f"| **Support Total** | | **${cogs['customer_support']['subtotal']:,}** |\n"
            f"| DevOps Tools | Datadog, GitHub, Sentry | ${cogs['devops_tools']['subtotal']:,} |\n"
            f"| **Total COGS** | | **${cogs['total_cogs']:,}** |\n"
            f"| **Gross Profit** | MRR $44,000 − COGS | **${44000 - cogs['total_cogs']:,}** |\n"
            f"| **Gross Margin** | | **{cogs['gross_margin_pct']}%** |\n"
        )
        chart = {
            "type": "donut",
            "title": "COGS Breakdown — June 2026",
            "labels": ["Cloud Infra", "Stripe Fees", "Support", "DevOps Tools"],
            "datasets": [{"values": [
                cogs["cloud_infrastructure"]["subtotal"],
                cogs["payment_processing"]["stripe_fees"],
                cogs["customer_support"]["subtotal"],
                cogs["devops_tools"]["subtotal"],
            ], "colors": ["#7c6fff", "#4ade80", "#fbbf24", "#f87171"]}],
            "yformat": "$",
        }

    elif any(w in q for w in ["opex", "operating expense", "spend breakdown", "spend"]):
        opex = md.OPEX_BREAKDOWN_JUNE
        rd = opex['research_and_development']
        sm = opex['sales_and_marketing']
        ga = opex['general_and_administrative']
        ie = opex['interest_expense']
        answer = (
            "## OpEx Breakdown — June 2026\n\n"
            "| Department | Item | Amount | % Revenue |\n"
            "|------------|------|-------:|----------:|\n"
            f"| R&D | Engineering Salaries | ${rd['engineering_salaries']:,} | |\n"
            f"| R&D | Tools (Linear, Figma, Cursor) | ${rd['linear_figma_cursor']:,} | |\n"
            f"| **R&D Total** | | **${rd['subtotal']:,}** | **{rd['pct_of_revenue']}%** |\n"
            f"| Sales & Marketing | AE Salaries | ${sm['ae_salaries']:,} | |\n"
            f"| Sales & Marketing | Marketing Manager | ${sm['marketing_manager']:,} | |\n"
            f"| Sales & Marketing | LinkedIn / Google Ads | ${sm['linkedin_google_ads']:,} | |\n"
            f"| Sales & Marketing | HubSpot + Tools | ${sm['hubspot_crm'] + sm['apollo_loom_other']:,} | |\n"
            f"| **S&M Total** | | **${sm['subtotal']:,}** | **{sm['pct_of_revenue']}%** |\n"
            f"| G&A | CEO / CTO Draws | ${ga['ceo_cto_draws']:,} | |\n"
            f"| G&A | Finance / Ops | ${ga['finance_ops']:,} | |\n"
            f"| G&A | WeWork Rent | ${ga['wework_rent']:,} | |\n"
            f"| G&A | Insurance + Legal | ${ga['insurance'] + ga['legal_misc']:,} | |\n"
            f"| G&A | Carta + SaaS Tools | ${ga['carta'] + ga['notion'] + ga['google_workspace'] + ga['accounting_software']:,} | |\n"
            f"| **G&A Total** | | **${ga['subtotal']:,}** | **{ga['pct_of_revenue']}%** |\n"
            f"| Interest | Convertible Note | ${ie['convertible_note']:,} | |\n"
            f"| **Total OpEx** | | **${opex['total_opex']:,}** | **100%** |\n"
        )
        chart = {
            "type": "donut",
            "title": "OpEx Breakdown — June 2026",
            "labels": ["R&D", "Sales & Marketing", "G&A", "Interest"],
            "datasets": [{"values": [
                opex["research_and_development"]["subtotal"],
                opex["sales_and_marketing"]["subtotal"],
                opex["general_and_administrative"]["subtotal"],
                opex["interest_expense"]["convertible_note"],
            ], "colors": ["#7c6fff", "#4ade80", "#fbbf24", "#5a5a7a"]}],
            "yformat": "$",
        }

    elif any(w in q for w in ["team", "headcount", "people", "employee", "who", "staff"]):
        hc = md.HEADCOUNT
        summary = md.HEADCOUNT_SUMMARY
        rows = "\n".join(
            f"| {h['name']} | {h['title']} | {h['dept']} | ${h['salary_annual']:,} | {h['start_date']} |"
            for h in hc
        )
        answer = (
            f"## Team — {summary['total']} People as of Jun 2026\n\n"
            "| Name | Title | Dept | Annual Salary | Start Date |\n"
            "|------|-------|------|-------------:|-----------:|\n"
            + rows + "\n\n"
            f"### Summary\n"
            f"• Total annual payroll: **${summary['total_salary_annual']:,.0f}**\n"
            f"• Avg tenure: **{summary['avg_tenure_months']} months**\n"
            f"• CEO + CTO on below-market draws — compensated via equity (28% and 22%)\n\n"
            "### Planned hires H2 2026\n"
            "• 2 × Account Executive — Sep 2026\n"
            "• 1 × Sr Engineer + 1 × CSM — Oct 2026"
        )

    elif any(w in q for w in ["what if", "if revenue", "if opex", "if churn", "stress", "decrease", "decreas", "drop", "fall", "revenue down", "revenue drops"]) and any(w in q for w in ["%", "percent"]):
        import re
        # Parse revenue and opex deltas from question
        rev_inc  = re.search(r'revenue[^0-9+-]*\+\s*(\d+)\s*%', q)
        rev_dec  = re.search(r'revenue[^0-9+-]*-?\s*(\d+)\s*%.*?(decreas|drop|fall|down|less)', q) or \
                   re.search(r'(decreas|drop|fall|down|cut|reduc)[a-z\s]*revenue[^0-9]*(\d+)\s*%', q) or \
                   re.search(r'revenue[^0-9]*(decreas|drop|fall|down)[^0-9]*(\d+)\s*%', q)
        # Simpler approach: find all % figures and their context
        rev_pct_match  = re.search(r'revenue[^0-9]*(\d+)\s*%', q)
        opex_pct_match = re.search(r'opex[^0-9]*(\d+)\s*%', q)
        churn_match    = re.search(r'churn[^0-9]*(\d+)\s*%', q)

        rev_delta  = 0
        opex_delta = 0
        churn_delta = 0

        if rev_pct_match:
            pct = int(rev_pct_match.group(1))
            rev_delta = -pct if any(w in q for w in ["decreas", "drop", "fall", "down", "less", "cut", "reduc", "worsen"]) else pct
        if opex_pct_match:
            pct = int(opex_pct_match.group(1))
            opex_delta = pct if any(w in q for w in ["increas", "up", "rise", "jump", "more", "higher"]) else -pct
        if churn_match:
            churn_delta = int(churn_match.group(1))

        # Base numbers
        base_mrr       = 44000
        base_cogs      = 9650    # ~22% of MRR
        base_opex      = 34150   # salaries + g&a + s&m (excl cogs)
        base_burn      = base_cogs + base_opex  # 43,800
        base_gm        = base_mrr - base_cogs
        base_ebitda    = base_mrr - base_burn
        cash           = 240000

        # Stressed numbers
        new_mrr    = base_mrr  * (1 + rev_delta  / 100)
        new_cogs   = base_cogs * (1 + max(rev_delta, 0) / 100)   # cogs scales with revenue
        new_opex   = base_opex * (1 + opex_delta / 100)
        new_burn   = new_cogs + new_opex
        new_gm     = new_mrr - new_cogs
        new_ebitda = new_mrr - new_burn
        net_burn   = new_burn - new_mrr

        gm_pct      = (new_gm / new_mrr * 100) if new_mrr else 0
        ebitda_pct  = (new_ebitda / new_mrr * 100) if new_mrr else 0

        base_net_burn = base_burn - base_mrr
        if base_net_burn <= 0:
            base_runway_str = "36+ mo (cash flow positive)"
        else:
            base_runway_str = f"{round(cash / base_net_burn)} months"

        if net_burn <= 0:
            runway_str = "36+ months (cash flow positive)"
        else:
            runway_str = f"**{round(cash / net_burn)} months**"

        label = f"Revenue {rev_delta:+}%" + (f" / OpEx {opex_delta:+}%" if opex_delta else "")

        answer = (
            f"## Stress Test: {label}\n\n"
            f"| Metric | Base | Stressed | Delta |\n"
            f"|--------|-----:|---------:|------:|\n"
            f"| MRR | $44,000 | **${new_mrr:,.0f}** | {rev_delta:+}% |\n"
            f"| Gross Profit | ${base_gm:,.0f} | **${new_gm:,.0f}** | {((new_gm-base_gm)/base_gm*100) if base_gm else 0:+.1f}% |\n"
            f"| Gross Margin | 78.1% | **{gm_pct:.1f}%** | {gm_pct-78.1:+.1f}pp |\n"
            f"| OpEx | $34,150 | **${new_opex:,.0f}** | {opex_delta:+}% |\n"
            f"| Total Burn | $43,800 | **${new_burn:,.0f}** | {((new_burn-base_burn)/base_burn*100):+.1f}% |\n"
            f"| EBITDA | +$200 | **{'+'if new_ebitda>=0 else ''}${new_ebitda:,.0f}** | — |\n"
            f"| EBITDA Margin | 0.5% | **{ebitda_pct:.1f}%** | {ebitda_pct-0.5:+.1f}pp |\n"
            f"| Net Burn | ~$0 | **${max(net_burn,0):,.0f}/mo** | — |\n"
            f"| Runway | {base_runway_str} | {runway_str} | — |\n\n"
            f"### Bottom line\n"
        )
        if net_burn > 0:
            answer += (
                f"Under this scenario net burn is ${net_burn:,.0f}/mo — current cash of $240k lasts {round(cash/net_burn)} months. "
                f"Immediate levers: freeze discretionary opex, accelerate pipeline close (TechNova + Cirrus = +$168k ARR), "
                f"collect $11.4k in overdue AR."
            )
        else:
            answer += (
                f"Even under this stress scenario the business remains cash flow positive by ${abs(new_ebitda):,.0f}/mo. "
                f"No immediate action required — monitor gross margin closely if revenue decline continues."
            )

    elif any(w in q for w in ["runway if", "runway when", "runway with"]) or (("runway" in q) and any(w in q for w in ["increase", "jump", "grow", "raise", "double", "10%", "20%", "30%", "50%"])):
        import re
        pct_match = re.search(r'(\d+)\s*%', q)
        pct = int(pct_match.group(1)) if pct_match else 10
        base_mrr = 44000
        base_burn = 43800
        new_mrr = base_mrr * (1 + pct / 100)
        new_net_burn = base_burn - new_mrr
        monthly_surplus = new_mrr - base_burn
        net_burn = base_burn - new_mrr
        if net_burn <= 0:
            # Cash flow positive: runway = cash / gross burn (worst case if revenue stopped)
            worst_case_months = round(240000 / base_burn)
            cash_12mo = 240000 + (abs(net_burn) * 12)
            answer = (
                f"## Runway Scenario: +{pct}% Revenue\n\n"
                f"### Assumptions\n"
                f"• Current MRR: $44,000 · Gross burn: $43,800/mo\n"
                f"• Cash on hand: $240,000\n\n"
                f"### With {pct}% revenue increase\n"
                f"• New MRR: **${new_mrr:,.0f}**/mo\n"
                f"• Net burn: **$0** (cash flow positive — revenue exceeds costs)\n"
                f"• Runway (worst case, if revenue stopped): **{worst_case_months} months**\n"
                f"• Runway (on current trajectory): **36+ months**\n\n"
                f"### Bottom line\n"
                f"A {pct}% revenue increase makes you cash flow positive by ${abs(net_burn):,.0f}/mo. "
                f"Even if all revenue disappeared tomorrow, current cash covers {worst_case_months} months of burn. "
                f"On the current trajectory you accumulate ${cash_12mo:,.0f} in 12 months."
            )
        else:
            runway_months = round(240000 / net_burn)
            answer = (
                f"## Runway Scenario: +{pct}% Revenue\n\n"
                f"### Assumptions\n"
                f"• Current MRR: $44,000 · Gross burn: $43,800/mo\n"
                f"• Cash on hand: $240,000\n\n"
                f"### With {pct}% revenue increase\n"
                f"• New MRR: **${new_mrr:,.0f}**/mo\n"
                f"• Net burn: **${net_burn:,.0f}**/mo\n"
                f"• Runway: **{runway_months} months**\n\n"
                f"### Bottom line\n"
                f"A {pct}% revenue increase reduces monthly burn but you remain cash-flow negative. "
                f"At this pace, current cash lasts {runway_months} months — plan your Series A timing accordingly."
            )

    elif any(w in q for w in ["runway", "cash", "burn", "months left", "scenario"]):
        answer = (
            "## Cash & Runway — June 2026\n\n"
            "### Position\n"
            f"• Cash on hand: **$240,000**\n"
            f"• Gross burn: $43,800/mo\n"
            f"• MRR (accrual): $44,000/mo → net burn: **~$0** (breakeven)\n"
            f"• Runway: **24 months** (conservative, incl. AR timing delays)\n\n"
            "### What inflates June cash receipts\n"
            "• Orbits paid $12k annual upfront — only $1k is June revenue; $11k is deferred\n"
            "• DataCore paid $16.8k quarterly — only $5.6k earned; $11.2k is deferred\n"
            "• $22,200 total sits in Revenue in QB — needs a journal entry to Deferred Revenue\n\n"
            "### Forecast\n"
            "• Cash grows to ~$267k by Dec 2026 on base case pipeline\n"
            "• Hiring plan (2 AEs + 1 Eng + 1 CSM) compresses runway to 13 months — manageable if Series A closes Q1 2027"
        )

    elif any(w in q for w in ["mrr", "arr", "recurring", "revenue"]):
        answer = (
            f"## MRR / ARR — June 2026\n\n"
            f"### Key numbers\n"
            f"• MRR: **$44,000** (+15.8% MoM) · ARR: **$528,000**\n"
            f"• Active customers: **{md.ACTIVE_CUSTOMERS}** · Avg MRR/customer: $3,143\n"
            f"• NRR: **108.2%** — expansion is growing faster than churn\n\n"
            f"### MRR bridge (May → June)\n"
            f"• Beginning (May): $38,000\n"
            f"• New biz: +$4,500 (Meridian Health, Vanta Partners, Heliosoft)\n"
            f"• Expansion: +$2,500 (Apex upsell + DataCore seats)\n"
            f"• Churn: −$1,000 (Driftly Co, went to competitor)\n"
            f"• Ending (June): $44,000\n\n"
            f"### 6-month trajectory\n"
            f"Jan $18k → Feb $22k → Mar $27k → Apr $32k → May $38k → Jun $44k\n"
            f"144% MRR growth in H1 2026. Forecast: $80k MRR ($960k ARR) by Dec."
        )



    elif any(w in q for w in ["unit economics", "ltv", "cac", "payback"]):
        ue = md.UNIT_ECONOMICS
        cac_ch = md.CAC_BY_CHANNEL
        best = min(cac_ch, key=lambda c: c['cac'])
        answer = (
            "## Unit Economics — June 2026\n\n"
            "| Metric | Value | Benchmark |\n"
            "|--------|------:|----------:|\n"
            f"| Avg MRR / customer | ${int(md.MRR_CURRENT) // md.ACTIVE_CUSTOMERS:,}/mo | — |\n"
            f"| Gross Margin | **{md.GROSS_MARGIN_PCT*100:.1f}%** | >70% ✓ |\n"
            f"| Monthly Churn | **{md.CHURN_RATE_PCT*100:.1f}%** | <2% ✓ |\n"
            f"| NRR | **{md.NRR_PCT*100:.1f}%** | >100% ✓ |\n"
            f"| LTV | **${ue['ltv']:,}** | >3x CAC ✓ |\n"
            f"| Blended CAC | **${ue['blended_cac']:,}** | <LTV/3 ✓ |\n"
            f"| LTV:CAC | **{md.LTV_CAC_RATIO}x** | >3x ✓ |\n"
            f"| CAC Payback | **{ue['cac_payback_months']} months** | <18mo ✓ |\n"
            f"| Magic Number | **{ue['magic_number']}** | >0.5 ✓ |\n"
            f"| Rule of 40 | **144** (MoM growth 15.8% × 12 + ~0% EBITDA) | >40 ✓ |\n\n"
            "### CAC by channel\n\n"
            "| Channel | CAC | LTV:CAC | Payback |\n"
            "|---------|----:|--------:|--------:|\n"
            + "\n".join(
                f"| {'**' + c['channel'] + '**' if c['channel'] == best['channel'] else c['channel']} "
                f"| ${c['cac']:,} | {c['ltv_cac']}x | {c['payback_months']} mo |"
                for c in cac_ch
            )
            + f"\n\n### Bottom line\n"
            f"• Best channel: **{best['channel']}** (CAC ${best['cac']:,}, {best['ltv_cac']}x LTV:CAC) — scale this first\n"
            f"• LTV:CAC of {md.LTV_CAC_RATIO}x exceeds Series A benchmark of 3x\n"
            f"• NRR of {md.NRR_PCT*100:.1f}% means existing customers are growing — strong retention flywheel"
        )

    elif any(w in q for w in ["customer", "roster", "account", "logo"]):
        roster = md.CUSTOMER_ROSTER
        lines = "\n".join(
            f"  {c['name']:20s}  ${c['mrr']:>6,.0f}/mo  {c['plan']:12s}  Since {c['since']}"
            for c in sorted(roster, key=lambda x: -x["mrr"])
        )
        answer = (
            f"Active customers — {len(roster)} logos, $42,000 MRR total:\n\n"
            f"{lines}\n\n"
            "Churned this month:\n"
            "  Driftly Co — $900/mo, left Jun 15, went to competitor on price.\n\n"
            "New this month:\n"
            "  Meridian Health — $1,200/mo (Growth)\n"
            "  Vanta Partners  — $600/mo (Starter)\n"
            "  Fintex Ltd      — $800/mo (Starter) — has a disputed charge, watch this one."
        )

    elif any(w in q for w in ["yoy", "year over year", "year-over-year", "variance", "prior year", "vs last year", "compared to last"]):
        # June 2025 actuals (prior year)
        py = {"mrr": 18000, "cogs": 4500, "payroll": 22000, "other_opex": 3200, "cash": 95000}
        cy = {"mrr": 44000, "cogs": 9800, "payroll": 30000, "other_opex": 4000, "cash": 240000}
        def gp(d): return d["mrr"] - d["cogs"]
        def ebitda(d): return d["mrr"] - d["cogs"] - d["payroll"] - d["other_opex"]
        def gm(d): return gp(d) / d["mrr"] * 100
        def em(d): return ebitda(d) / d["mrr"] * 100
        def delta(a, b): return f"{'+' if b-a>=0 else ''}${b-a:,.0f}"
        def dpct(a, b): return f"{(b-a)/abs(a)*100:+.1f}%"
        answer = (
            "## YoY Income Statement — June 2025 vs June 2026\n\n"
            "| Line Item | Jun 2025 | Jun 2026 | $ Δ | % Δ |\n"
            "|-----------|--------:|---------:|----:|----:|\n"
            f"| Revenue (MRR) | ${py['mrr']:,} | **${cy['mrr']:,}** | {delta(py['mrr'],cy['mrr'])} | {dpct(py['mrr'],cy['mrr'])} |\n"
            f"| COGS | (${py['cogs']:,}) | **(${cy['cogs']:,})** | {delta(py['cogs'],cy['cogs'])} | {dpct(py['cogs'],cy['cogs'])} |\n"
            f"| Gross Profit | ${gp(py):,} | **${gp(cy):,}** | {delta(gp(py),gp(cy))} | {dpct(gp(py),gp(cy))} |\n"
            f"| Gross Margin | {gm(py):.1f}% | **{gm(cy):.1f}%** | — | {gm(cy)-gm(py):+.1f}pp |\n"
            f"| Payroll | (${py['payroll']:,}) | **(${cy['payroll']:,})** | {delta(py['payroll'],cy['payroll'])} | {dpct(py['payroll'],cy['payroll'])} |\n"
            f"| Other OpEx | (${py['other_opex']:,}) | **(${cy['other_opex']:,})** | {delta(py['other_opex'],cy['other_opex'])} | {dpct(py['other_opex'],cy['other_opex'])} |\n"
            f"| EBITDA | ${ebitda(py):,} | **${ebitda(cy):,}** | {delta(ebitda(py),ebitda(cy))} | — |\n"
            f"| EBITDA Margin | {em(py):.1f}% | **{em(cy):.1f}%** | — | {em(cy)-em(py):+.1f}pp |\n"
            f"| Cash | ${py['cash']:,} | **${cy['cash']:,}** | {delta(py['cash'],cy['cash'])} | {dpct(py['cash'],cy['cash'])} |\n\n"
            "### Key takeaways\n"
            f"• Revenue grew **{dpct(py['mrr'],cy['mrr'])}** YoY — from $18k to $44k MRR\n"
            f"• Gross margin expanded **{gm(cy)-gm(py):+.1f}pp** — better unit economics at scale\n"
            f"• EBITDA improved by **{delta(ebitda(py),ebitda(cy))}** — near breakeven vs a loss last year\n"
            f"• Cash position strengthened by **{delta(py['cash'],cy['cash'])}** — 2.5x stronger balance sheet\n"
            f"• Payroll grew {dpct(py['payroll'],cy['payroll'])} — headcount investment tracking revenue growth"
        )

    elif any(w in q for w in ["ebitda", "profit", "p&l", "income", "margin"]):
        hist = md.MONTHLY_HISTORY
        months_p = [h['month'].replace(" 2026","") for h in hist]
        col_h = "| | " + " | ".join(months_p) + " |\n"
        col_s = "|---|" + "|".join(["---:" for _ in hist]) + "|\n"
        def prow(label, vals): return f"| {label} | " + " | ".join(vals) + " |\n"
        answer = (
            "## Income Statement — Jan to Jun 2026 (Accrual Basis)\n\n"
            + col_h + col_s
            + prow("Revenue",      [f"${h['mrr']:,}"  for h in hist])
            + prow("COGS",         [f"(${round(h['mrr']*(1-h['gross_margin_pct']/100)):,})" for h in hist])
            + prow("**Gross Profit**", [f"**${round(h['mrr']*h['gross_margin_pct']/100):,}**" for h in hist])
            + prow("Gross Margin", [f"{h['gross_margin_pct']}%" for h in hist])
            + prow("Payroll",      ["($28,000)" if h['mrr'] < 30000 else "($30,000)" for h in hist])
            + prow("Other OpEx",   ["($4,000)" for _ in hist])
            + prow("**EBITDA**",   [f"**{'+' if h['ebitda']>=0 else ''}${h['ebitda']:,}**" for h in hist])
            + prow("EBITDA Margin",[f"{h['ebitda_margin_pct']}%" for h in hist])
            + "\n### Note — Cash vs Accrual gap (June)\n"
            "• QB shows revenue of **$64,200** (cash collected) vs **$44,000** accrual\n"
            "• Gap of **$22,200** = unearned prepayments from Orbits ($11k) + DataCore ($11.2k)\n"
            "• QB EBITDA of +$22,200 is **overstated** — do not share externally\n"
            "• Fix: one journal entry to move $22,200 from Revenue → Deferred Revenue"
        )

    elif any(w in q for w in ["balance sheet", "balance"]):
        total_assets = md.BS_CASH + md.BS_AR + md.BS_PREPAID + md.BS_SECURITY_DEPOSIT
        total_liab_corrected = md.BS_NOTE_A + md.BS_NOTE_B + 22200 + 11000 + 4000
        equity_corrected = total_assets - total_liab_corrected
        answer = (
            "## Balance Sheet — June 30, 2026\n\n"
            "### Assets\n\n"
            "| Asset | As Booked |\n"
            "|-------|----------:|\n"
            f"| Cash & Equivalents | ${md.BS_CASH:,.0f} |\n"
            f"| Accounts Receivable | ${md.BS_AR:,.0f} |\n"
            f"| Prepaid Expenses | ${md.BS_PREPAID:,.0f} |\n"
            f"| Security Deposit | ${md.BS_SECURITY_DEPOSIT:,.0f} |\n"
            f"| **Total Assets** | **${total_assets:,.0f}** |\n\n"
            "### Liabilities\n\n"
            "| Liability | As Booked | Corrected | Issue |\n"
            "|-----------|----------:|----------:|-------|\n"
            f"| Accounts Payable | $0 | $11,000 | Vendor bills not recorded |\n"
            f"| Deferred Revenue | $0 | $22,200 | Orbits + DataCore prepayments not journaled |\n"
            f"| Accrued Liabilities | $0 | $4,000 | Payroll taxes not recorded |\n"
            f"| Accrued Interest | $0 | $3,750 | Convertible note interest not accrued |\n"
            f"| Convertible Note A | ${md.BS_NOTE_A:,.0f} | ${md.BS_NOTE_A:,.0f} | 9% interest, matures Jun 2027 |\n"
            f"| Convertible Note B | ${md.BS_NOTE_B:,.0f} | ${md.BS_NOTE_B:,.0f} | 8% interest |\n"
            f"| **Total Liabilities** | **${md.BS_TOTAL_LIABILITIES_BOOKED:,.0f}** | **${total_liab_corrected:,.0f}** | |\n\n"
            "### Equity\n\n"
            "| Item | As Booked | Corrected |\n"
            "|------|----------:|----------:|\n"
            f"| Accumulated Deficit | ${md.BS_ACCUMULATED_DEFICIT:,.0f} | ${equity_corrected:,.0f} |\n"
            f"| **Total Equity** | **${md.BS_TOTAL_EQUITY:,.0f}** | **${equity_corrected:,.0f}** |\n\n"
            "### Bottom line\n"
            f"• Assets foot correctly at **${total_assets:,.0f}**\n"
            "• 4 missing journal entries overstate equity by ~**$40,950**\n"
            "• Fix these before sharing the balance sheet with investors or auditors"
        )

    elif any(w in q for w in ["fix", "action", "journal", "entries", "priorit", "close"]):
        all_issues = sorted(fails + warns, key=lambda r: 0 if r["status"] == "fail" else 1)
        lines = []
        for i, r in enumerate(all_issues[:8]):
            if r.get("action"):
                lines.append(f"  {i+1}. [{r['status'].upper()}] {r['name']}")
                lines.append(f"     {r['action']}")
        answer = (
            f"Prioritized close actions ({counts['fail']} critical + {counts['warn']} warnings):\n\n"
            + "\n".join(lines)
        )

    elif any(w in q for w in ["deferred", "recognition", "prepay", "orbits", "datacore"]):
        answer = (
            "Deferred Revenue — June 2026\n\n"
            "Two customers paid upfront — neither was moved to Deferred Revenue in QB:\n\n"
            "  Orbits Inc — $12,000 annual contract\n"
            "    Paid: Jun 1, 2026\n"
            "    Earned in June: $1,000 (1 of 12 months)\n"
            "    Should be deferred: $11,000\n"
            "    Currently in QB: booked as $12,000 revenue (wrong)\n\n"
            "  DataCore Inc — $16,800 quarterly contract\n"
            "    Paid: Jun 10, 2026\n"
            "    Earned in June: $5,600 (1 of 3 months)\n"
            "    Should be deferred: $11,200\n"
            "    Currently in QB: booked as $16,800 revenue (wrong)\n\n"
            "Total unearned revenue sitting in income: $22,200\n"
            "Journal entry needed:\n"
            "  Dr Revenue         $22,200\n"
            "  Cr Deferred Revenue $22,200\n\n"
            "Deferred revenue is a liability — money collected for services not yet delivered."
        )

    elif any(w in q for w in ["budget", "vs actuals", "vs. actual", "plan vs", "tracking against"]):
        answer = (
            "## Budget vs. Actuals — June 2026\n\n"
            "### Revenue\n"
            "• Budget: $48,000 · Actual (accrual): $44,000 · Variance: **-$4,000 (-8.3%)**\n"
            "• Cash collected: $64,200 — overstated by $22,200 in prepayments (not a real beat)\n\n"
            "### Payroll\n"
            "• Budget: $45,000 · Actual (gross): $32,000 · Variance: **+$13,000 favorable**\n"
            "• Warning: QB recorded only $28,000 — employer taxes/benefits ($4,000) not captured\n\n"
            "### Other OpEx\n"
            "• Budget: $8,500 · Actual: ~$4,000 · Variance: **+$4,500 favorable**\n"
            "• AWS duplicate charge ($3,200) inflates June spend — needs reversal\n\n"
            "### EBITDA\n"
            "• Budget: -$5,500 · Actual: ~$0 · Variance: **+$5,500 favorable**\n"
            "• Favorable mainly due to payroll coming in below plan (2 open roles unfilled)\n\n"
            "### Notes\n"
            "• Prior year June 2025: $18,500 revenue, $35,000 payroll — 138% revenue growth YoY\n"
            "• Budget was set in Jan 2026 before the Apex and DataCore expansions materialized"
        )

    elif any(w in q for w in ["cap table", "carta", "equity structure", "shares", "option pool", "shareholders"]):
        ct = md.CARTA_CAP_TABLE
        notes = ct["convertible_notes"]
        answer = (
            "## Cap Table — Acme SaaS Inc.\n\n"
            f"### Share structure (as of {ct['last_updated']})\n"
            f"• Total authorized shares: {ct['total_shares']:,}\n"
            f"• Option pool: {ct['option_pool']:,} shares (15% of total)\n\n"
            "### Founder ownership (pre-money, pre-note conversion)\n"
            "• Jordan Lee (CEO/Co-founder): 28%\n"
            "• Sam Chen (CTO/Co-founder): 22%\n"
            "• Early employees / advisors: ~5%\n"
            "• Unissued option pool: 15%\n"
            "• Remaining authorized (unissued): 30%\n\n"
            "### Convertible notes outstanding\n"
            + "\n".join(f"• {n['investor']}: ${n['amount']:,} at {int(n['interest_rate']*100)}% interest, matures {n['maturity']}" for n in notes)
            + f"\n• Total principal: ${sum(n['amount'] for n in notes):,}\n"
            f"• Monthly interest: $3,750 (not being accrued in QB — open issue)\n\n"
            "### 409a\n"
            f"• Last valuation: {ct['latest_409a_date']}\n"
            f"• Implied common stock FMV: ~$0.42/share\n"
            f"• Note: valuation is 7 months old — needs refresh before issuing new options or raising"
        )

    elif any(w in q for w in ["409a", "valuation", "fmv", "fair market value", "common stock price"]):
        ct = md.CARTA_CAP_TABLE
        answer = (
            "## 409a Valuation — Acme SaaS Inc.\n\n"
            f"### Current status\n"
            f"• Last completed: **{ct['latest_409a_date']}** (7 months ago)\n"
            f"• Implied FMV: **~$0.42 per common share**\n"
            f"• Total shares: {ct['total_shares']:,}\n"
            f"• Implied enterprise value at 409a: ~$4.2M\n\n"
            "### Why this matters now\n"
            "• Any new option grants before a fresh 409a use the $0.42 strike price\n"
            "• At $528k ARR growing 144% in H1, the business has likely re-rated significantly\n"
            "• A new 409a before the Series A will likely come in at $1.50–$2.50/share based on current metrics\n"
            "• Higher 409a = higher option strike prices for new hires — affects recruiting\n\n"
            "### Recommendation\n"
            "• Refresh the 409a before issuing options to the 4 planned hires (Sep–Oct)\n"
            "• Typically takes 2–3 weeks and costs $2,500–$5,000 via Carta or a third-party firm\n"
            "• Do it after the Series A closes if you want the lowest possible strike for new hires"
        )

    elif any(w in q for w in ["memo", "board", "cfo", "executive summary"]):
        fail_list = "\n".join(f"  • {r['name']}: {r.get('impact','')}" for r in fails[:5])
        answer = (
            "CFO Close Memo — June 2026\n\n"
            "Acme SaaS Inc. — DRAFT — NOT FOR DISTRIBUTION\n\n"
            "Financial performance:\n"
            "  MRR $42,000 (+10.5% MoM), ARR $504,000, gross margin 73.8%.\n"
            "  EBITDA breakeven on accrual basis. Cash balance $185,000 (18.9 months runway).\n\n"
            f"Open issues ({counts['fail']} critical — resolve before sharing externals):\n"
            f"{fail_list}\n\n"
            "Required actions before investor-ready:\n"
            "  1. Book $22,200 deferred revenue journal entry (Orbits + DataCore)\n"
            "  2. Invoice Meridian Health ($3,600) and Vanta Partners ($1,800) — still unbilled\n"
            "  3. Send collections notices on $26k overdue AR\n"
            "  4. Accrue $3,750 convertible note interest\n"
            "  5. Split payroll by department in QB\n\n"
            "Do not share cash-basis P&L. Share accrual P&L only after entries above are posted.\n\n"
            "Prepared by: Fuel MCP · " + datetime.now().strftime("%B %d, %Y")
        )

    else:
        # Fall back to Claude
        context = (
            f"You are Fuel AI, an intelligent financial assistant for Acme SaaS Inc.\n"
            f"Today is June 30, 2026. You have access to live financial data from Stripe, QuickBooks, Gusto, HubSpot, and Carta.\n\n"
            f"KEY FINANCIALS:\n"
            f"- MRR: $42,000 (+10.5% MoM) | ARR: $504,000 | 14 customers\n"
            f"- Gross margin: 73.8% | EBITDA: breakeven (accrual)\n"
            f"- Cash: $185,000 | Runway: 18.9 months\n"
            f"- LTV:CAC: 4.6x | Monthly churn: 2.4% | NRR: 94.1%\n"
            f"- Deferred revenue error: $22,200 booked as income (Orbits $11k + DataCore $11.2k)\n"
            f"- Open issues: {counts['fail']} critical, {counts['warn']} warnings\n\n"
            f"OPEN ISSUES:\n"
            + "\n".join(f"[{r['status'].upper()}] {r['name']}: {r['detail']}" for r in fails + warns)
            + f"\n\nFORECAST:\n- ARR Dec 2026: $960,000 | Cash Dec 2026: $267,100\n"
            f"- Series A target: $1M ARR (Jan 2027)\n\n"
            f"Answer the question below directly and specifically. Use the data above. "
            f"Be concise but complete. Use bullet points where helpful. No fluff.\n\n"
            f"Question: {req.question}"
        )
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=600,
                messages=[{"role": "user", "content": context}],
            )
            answer = msg.content[0].text
        except Exception as e:
            answer = f"Sorry, couldn't reach the AI right now. ({e})"

    try:
        return JSONResponse({"answer": answer, "chart": chart})
    except NameError:
        return JSONResponse({"answer": answer})
