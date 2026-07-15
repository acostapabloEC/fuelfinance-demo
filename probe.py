"""
Probe agent — sends a comprehensive list of CFO/investor questions to /ask,
scores each answer, and reports gaps that need pre-wired coverage.
"""
import urllib.request, json, textwrap, sys

BASE = "http://localhost:8000"

QUESTIONS = [
    # Revenue / MRR
    ("MRR", "What is our current MRR?"),
    ("ARR", "What is our current ARR?"),
    ("Revenue bridge", "Walk me through the MRR bridge from last month to this month."),
    ("Revenue by segment", "What is our ARR broken down by customer segment?"),
    ("YoY growth", "What is our year-over-year revenue growth?"),
    # Unit economics
    ("LTV:CAC", "What is our LTV to CAC ratio?"),
    ("Burn multiple", "What is our burn multiple?"),
    ("Magic number", "What is our magic number?"),
    ("Rule of 40", "What is our Rule of 40 score?"),
    ("Payback period", "What is our CAC payback period in months?"),
    ("CAC by channel", "What is our CAC broken down by channel?"),
    # Cash / burn
    ("Runway", "How many months of runway do we have?"),
    ("Burn rate", "What is our monthly burn rate?"),
    ("Cash position", "What is our cash on hand?"),
    # P&L
    ("EBITDA", "What is our EBITDA?"),
    ("Gross margin", "What is our gross margin?"),
    ("COGS", "What makes up our cost of goods sold?"),
    ("OpEx", "Break down our operating expenses."),
    ("Payroll by dept", "What is our payroll broken down by department?"),
    ("Budget vs actuals", "How are we tracking against budget?"),
    # Balance sheet
    ("Balance sheet", "Show me the balance sheet."),
    ("AR aging", "What does our accounts receivable aging look like?"),
    ("AP", "What do we owe vendors in accounts payable?"),
    ("Deferred revenue", "What is our deferred revenue balance?"),
    ("Convertible notes", "What is our convertible note situation?"),
    ("Cap table", "What does our cap table look like?"),
    # Customers
    ("Customer roster", "Who are our customers and what do they pay?"),
    ("Revenue concentration", "What is our revenue concentration risk?"),
    ("Top customers", "Who are our top 3 customers by MRR?"),
    ("Churn", "Which customers churned this month?"),
    ("New customers", "Which customers did we add this month?"),
    ("ACV", "What is our average contract value?"),
    # Pipeline / sales
    ("Pipeline", "Show me the sales pipeline."),
    ("Win rate", "What is our sales win rate?"),
    ("Sales cycle", "What is our average sales cycle length?"),
    ("Forecast", "What is the revenue forecast through December?"),
    # Hiring / headcount
    ("Headcount", "How many people do we have and what are the roles?"),
    ("Hiring plan", "What is the hiring plan for H2?"),
    ("Hiring scenario", "What happens to runway if we hire 2 AEs and 1 engineer in Q3?"),
    # Fundraise
    ("Raise readiness", "Am I ready to raise a Series A?"),
    ("Close issues", "What is blocking a clean month-end close?"),
    ("CFO memo", "Draft a CFO memo for the board."),
    # Cohorts / retention
    ("NRR", "What is our net revenue retention?"),
    ("Cohorts", "Show me cohort retention by vintage."),
    ("Churn risk", "Which customers are at churn risk?"),
    # Misc
    ("Expense anomalies", "Are there any unusual or duplicate expenses?"),
    ("Interest expense", "What is our interest expense on the convertible notes?"),
    ("409a", "What is our current 409a valuation?"),
    ("Equity", "What is the equity structure?"),
]

def ask(question):
    payload = json.dumps({"question": question}).encode()
    req = urllib.request.Request(
        f"{BASE}/ask",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())["answer"]

WEAK_SIGNALS = [
    "connection error",
    "sorry, couldn",
    "i don't have",
    "i'm not sure",
    "not available",
    "as an ai",
    "i cannot",
    "i don't know",
    "no data",
]

def score(answer):
    lo = answer.lower()
    if any(s in lo for s in WEAK_SIGNALS):
        return "WEAK"
    if len(answer) < 120:
        return "THIN"
    return "OK"

print(f"\n{'-'*70}")
print(f"  FUEL MCP -- Answer probe  ({len(QUESTIONS)} questions)")
print(f"{'-'*70}\n")

results = {"OK": [], "THIN": [], "WEAK": []}

for label, q in QUESTIONS:
    try:
        ans = ask(q)
        grade = score(ans)
        results[grade].append((label, q, ans))
        icon = {"OK": "OK", "THIN": "TH", "WEAK": "XX"}[grade]
        snippet = ans[:80].replace("\n", " ").encode("ascii","replace").decode()
        print(f"  {icon} [{label:22s}]  {snippet}")
    except Exception as e:
        results["WEAK"].append((label, q, str(e)))
        print(f"  XX [{label:22s}]  ERROR: {e}")

print(f"\n{'-'*70}")
print(f"  OK:   {len(results['OK'])}")
print(f"  THIN: {len(results['THIN'])}")
print(f"  WEAK: {len(results['WEAK'])}")
print(f"{'-'*70}\n")

if results["THIN"] or results["WEAK"]:
    print("GAPS TO FILL:\n")
    for label, q, ans in results["THIN"] + results["WEAK"]:
        print(f"  [{label}] \"{q}\"")
        preview = ans[:120].replace("\n", " ")
        print(f"    → {preview}")
        print()
