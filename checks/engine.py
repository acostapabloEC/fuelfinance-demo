"""
Month-end close checks engine.
Each check returns a dict: { id, name, status, detail, impact, action, stakeholders }
status: "pass" | "warn" | "fail"
stakeholders: list of roles this check is relevant to
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mock_data import (
    STRIPE_TRANSACTIONS, STRIPE_GROSS, STRIPE_FEES_TOTAL, STRIPE_NET_DEPOSITED,
    QB_REVENUE_TOTAL, QB_REVENUE_ENTRIES, QB_DEFERRED_REVENUE_BALANCE,
    QB_AR_AGING, QB_LAST_RECONCILIATION_DATE, QB_EXPENSES,
    QB_ACCRUED_LIABILITIES, QB_PREPAID_BALANCE, QB_PREPAID_MOVEMENT,
    QB_PAYROLL_RECORDED, QB_PAYROLL_SPLIT, GUSTO_GROSS_TOTAL, GUSTO_PAYROLL,
    HUBSPOT_CLOSED_WON, CARTA_CAP_TABLE
)
from datetime import datetime, date

PERIOD_END = date(2026, 6, 30)


def check_stripe_qb_alignment():
    stripe_excl_refunds = sum(t["amount"] for t in STRIPE_TRANSACTIONS if t["type"] == "charge" and t["status"] == "succeeded")
    gap = stripe_excl_refunds - QB_REVENUE_TOTAL
    if abs(gap) < 1:
        return {
            "id": 1, "name": "Stripe -> QB Revenue Alignment",
            "status": "pass",
            "detail": f"Stripe gross (${stripe_excl_refunds:,.2f}) matches QB revenue (${QB_REVENUE_TOTAL:,.2f}).",
            "impact": None, "action": None,
            "stakeholders": ["Finance", "Sales"]
        }
    return {
        "id": 1, "name": "Stripe -> QB Revenue Alignment",
        "status": "fail",
        "detail": f"Stripe gross: ${stripe_excl_refunds:,.2f} - QB revenue: ${QB_REVENUE_TOTAL:,.2f} - Gap: ${gap:,.2f}",
        "impact": f"${gap:,.2f} in revenue unaccounted for between systems.",
        "action": "Reconcile Stripe payout report against QB invoice list line by line.",
        "stakeholders": ["Finance", "Sales"]
    }


def check_stripe_fees_netted():
    fee_entry = [e for e in QB_EXPENSES if e["vendor"] == "Stripe" and e["account"] == "Revenue"]
    if not fee_entry:
        fee_expense = [e for e in QB_EXPENSES if e["vendor"] == "Stripe" and "expense" in e["account"].lower()]
        if fee_expense:
            return {
                "id": 2, "name": "Stripe Fees - Correctly Recorded",
                "status": "pass",
                "detail": f"Stripe processing fees (${STRIPE_FEES_TOTAL:,.2f}) recorded as payment processing expense.",
                "impact": None, "action": None,
                "stakeholders": ["Finance"]
            }
    return {
        "id": 2, "name": "Stripe Fees Netted Against Revenue",
        "status": "fail",
        "detail": f"Stripe processing fees (${STRIPE_FEES_TOTAL:,.2f}) are netted from the bank deposit - not recorded as a separate expense in QB.",
        "impact": f"Revenue understated by ${STRIPE_FEES_TOTAL:,.2f}. Gross margin overstated.",
        "action": "Create a separate journal entry: Debit Payment Processing Expense / Credit Revenue for $892.00.",
        "stakeholders": ["Finance"]
    }


def check_chargebacks_reversed():
    disputed = [t for t in STRIPE_TRANSACTIONS if t["status"] == "disputed"]
    refunds   = [t for t in STRIPE_TRANSACTIONS if t["type"] == "refund"]
    issues = []
    for t in disputed:
        issues.append(f"{t['customer']} - ${abs(t['amount']):,.2f} disputed on {t['date']} (no QB reversal found)")
    for t in refunds:
        issues.append(f"{t['customer']} - ${abs(t['amount']):,.2f} refund on {t['date']} (no QB reversal found)")
    total = sum(abs(t["amount"]) for t in disputed + refunds)
    if not issues:
        return {
            "id": 3, "name": "Refunds & Chargebacks Reversed in QB",
            "status": "pass",
            "detail": "All Stripe disputes and refunds have corresponding QB reversals.",
            "impact": None, "action": None,
            "stakeholders": ["Finance", "Sales"]
        }
    return {
        "id": 3, "name": "Refunds & Chargebacks Not Reversed in QB",
        "status": "warn",
        "detail": " | ".join(issues),
        "impact": f"QB revenue overstated by ${total:,.2f}.",
        "action": "Create credit memos in QB for each disputed charge and refund.",
        "stakeholders": ["Finance", "Sales"]
    }


def check_cash_basis_bleed():
    deposit_dates = {p["date"] for p in [
        {"date": "2025-06-05"}, {"date": "2025-06-12"},
        {"date": "2025-06-19"}, {"date": "2025-06-26"}
    ]}
    bleed = [e for e in QB_REVENUE_ENTRIES if e["date"] in deposit_dates]
    if not bleed:
        return {
            "id": 4, "name": "Cash-Basis Bleed-Through",
            "status": "pass",
            "detail": "Revenue entry dates match invoice dates, not bank deposit dates.",
            "impact": None, "action": None,
            "stakeholders": ["Finance"]
        }
    return {
        "id": 4, "name": "Cash-Basis Bleed-Through",
        "status": "fail",
        "detail": f"{len(bleed)} revenue entries dated on bank deposit dates instead of invoice/delivery dates.",
        "impact": "Revenue is recognized when cash arrives, not when earned. Violates accrual basis.",
        "action": "Re-date revenue entries to match invoice dates. Review revenue recognition policy with bookkeeper.",
        "stakeholders": ["Finance"]
    }


def check_deferred_revenue():
    expected_deferred = 11000.00
    gap = expected_deferred - QB_DEFERRED_REVENUE_BALANCE
    if abs(gap) < 1:
        return {
            "id": 5, "name": "Deferred Revenue - Balance Sheet",
            "status": "pass",
            "detail": f"Deferred revenue balance (${QB_DEFERRED_REVENUE_BALANCE:,.2f}) matches expected unearned contract value.",
            "impact": None, "action": None,
            "stakeholders": ["Finance", "Sales", "Investors"]
        }
    return {
        "id": 5, "name": "Deferred Revenue Not Recorded",
        "status": "fail",
        "detail": f"Orbits Inc paid $12,000 annual upfront. Only $1,000 earned in June. Expected deferred: ${expected_deferred:,.2f} - QB balance: ${QB_DEFERRED_REVENUE_BALANCE:,.2f}.",
        "impact": f"Revenue overstated by ${gap:,.2f}. ARR inflated.",
        "action": "Create deferred revenue liability of $11,000. Recognize $1,000/month over remaining contract term.",
        "stakeholders": ["Finance", "Sales", "Investors"]
    }


def check_duplicate_transactions():
    seen = {}
    dupes = []
    for e in QB_EXPENSES:
        key = (e["vendor"], e["amount"], e["date"][:7])
        if key in seen:
            dupes.append(e)
        else:
            seen[key] = e
    if not dupes:
        return {
            "id": 6, "name": "Duplicate Transactions",
            "status": "pass",
            "detail": "No duplicate transactions found in QB for the period.",
            "impact": None, "action": None,
            "stakeholders": ["Finance", "Ops"]
        }
    total = sum(d["amount"] for d in dupes)
    return {
        "id": 6, "name": "Duplicate Transactions Found",
        "status": "fail",
        "detail": f"{len(dupes)} duplicate(s): " + ", ".join(f"{d['vendor']} ${d['amount']:,.2f}" for d in dupes),
        "impact": f"Expenses overstated by ${total:,.2f}.",
        "action": "Void duplicate entries in QB. Review AP workflow to prevent double entry.",
        "stakeholders": ["Finance", "Ops"]
    }


def check_bank_rec():
    last_rec = datetime.strptime(QB_LAST_RECONCILIATION_DATE, "%Y-%m-%d").date()
    days_ago = (PERIOD_END - last_rec).days
    if days_ago <= 30:
        return {
            "id": 7, "name": "Bank Reconciliation Current",
            "status": "pass",
            "detail": f"Last reconciliation: {QB_LAST_RECONCILIATION_DATE} ({days_ago} days ago).",
            "impact": None, "action": None,
            "stakeholders": ["Finance"]
        }
    return {
        "id": 7, "name": "Bank Reconciliation Overdue",
        "status": "warn",
        "detail": f"Last reconciliation: {QB_LAST_RECONCILIATION_DATE} - {days_ago} days ago. Threshold: 30 days.",
        "impact": "Unreconciled transactions may be masking errors or missing entries.",
        "action": "Complete bank reconciliation for June immediately. Set monthly close reminder.",
        "stakeholders": ["Finance"]
    }


def check_ar_aging():
    overdue = [i for i in QB_AR_AGING if i["days_overdue"] >= 30]
    if not overdue:
        return {
            "id": 8, "name": "AR Aging - No Overdue Invoices",
            "status": "pass",
            "detail": "No invoices 30+ days past due.",
            "impact": None, "action": None,
            "stakeholders": ["Finance", "Sales"]
        }
    total = sum(i["amount"] for i in overdue)
    details = " | ".join(f"{i['customer']} {i['invoice']} ${i['amount']:,.2f} ({i['days_overdue']}d overdue)" for i in overdue)
    return {
        "id": 8, "name": "AR Aging - Overdue Invoices",
        "status": "fail",
        "detail": details,
        "impact": f"${total:,.2f} in receivables at risk. Cash flow impact if uncollected.",
        "action": "Send collection notices immediately. Escalate invoices 45+ days to founder for direct outreach.",
        "stakeholders": ["Finance", "Sales"]
    }


def check_hubspot_qb_gap():
    unbilled = [d for d in HUBSPOT_CLOSED_WON if not d["invoiced_in_qb"]]
    if not unbilled:
        return {
            "id": 9, "name": "HubSpot -> QB - All Deals Invoiced",
            "status": "pass",
            "detail": "All closed-won deals in HubSpot have matching invoices in QB.",
            "impact": None, "action": None,
            "stakeholders": ["Sales", "Finance"]
        }
    total = sum(d["amount"] for d in unbilled)
    details = " | ".join(f"{d['deal']} ${d['amount']:,.2f} (closed {d['close_date']})" for d in unbilled)
    return {
        "id": 9, "name": "HubSpot -> QB Gap - Deals Not Invoiced",
        "status": "fail",
        "detail": details,
        "impact": f"${total:,.2f} in closed revenue never billed. Customers using product without being charged.",
        "action": "Create invoices in QB immediately for Meridian Health ($3,600) and Vanta Partners ($1,800).",
        "stakeholders": ["Sales", "Finance"]
    }


def check_ap_balance():
    ap_balance = 0.00
    if ap_balance > 0:
        return {
            "id": 10, "name": "AP Balance - Bills Entered on Receipt",
            "status": "pass",
            "detail": f"AP balance: ${ap_balance:,.2f}. Bills are being entered on receipt.",
            "impact": None, "action": None,
            "stakeholders": ["Finance", "Ops"]
        }
    return {
        "id": 10, "name": "AP Balance Zero - Bills Entered When Paid",
        "status": "warn",
        "detail": "AP balance is $0.00 at month end despite known outstanding vendor bills (legal, contractors).",
        "impact": "Expenses hitting wrong period. Liabilities understated on balance sheet.",
        "action": "Enter bills on receipt date, not payment date. Review June outstanding bills and accrue.",
        "stakeholders": ["Finance", "Ops"]
    }


def check_gusto_qb_match():
    gap = GUSTO_GROSS_TOTAL - QB_PAYROLL_RECORDED
    if abs(gap) < 1:
        return {
            "id": 11, "name": "Gusto -> QB Payroll Match",
            "status": "pass",
            "detail": f"QB wages (${QB_PAYROLL_RECORDED:,.2f}) matches Gusto gross (${GUSTO_GROSS_TOTAL:,.2f}).",
            "impact": None, "action": None,
            "stakeholders": ["Finance", "HR"]
        }
    return {
        "id": 11, "name": "Gusto -> QB Payroll Mismatch",
        "status": "warn",
        "detail": f"Gusto gross: ${GUSTO_GROSS_TOTAL:,.2f} - QB wages recorded: ${QB_PAYROLL_RECORDED:,.2f} - Gap: ${gap:,.2f}",
        "impact": f"Payroll taxes (${3800:,.2f}) and benefits (${2200:,.2f}) missing from QB. Expenses understated.",
        "action": "Record employer taxes and benefits as separate QB journal entries. Use Gusto payroll summary as source.",
        "stakeholders": ["Finance", "HR"]
    }


def check_payroll_split():
    if QB_PAYROLL_SPLIT:
        return {
            "id": 12, "name": "Payroll Split by Function",
            "status": "pass",
            "detail": "Payroll is split by Engineering, Sales, and G&A in QB.",
            "impact": None, "action": None,
            "stakeholders": ["Finance", "HR", "Engineering"]
        }
    run = GUSTO_PAYROLL[0]
    split = run["departments"]
    detail = " | ".join(f"{dept}: ${amt:,.2f}" for dept, amt in split.items())
    return {
        "id": 12, "name": "Payroll Not Split by Function",
        "status": "fail",
        "detail": f"All payroll sits in one QB account. Gusto shows: {detail}",
        "impact": "Department P&Ls show zero labor cost. Gross margin and unit economics are unreliable.",
        "action": "Split payroll journal entry by department using Gusto department totals as the basis.",
        "stakeholders": ["Finance", "HR", "Engineering"]
    }


def check_accrued_liabilities():
    if QB_ACCRUED_LIABILITIES > 0:
        return {
            "id": 13, "name": "Accrued Liabilities - Month End",
            "status": "pass",
            "detail": f"Accrued liabilities: ${QB_ACCRUED_LIABILITIES:,.2f} at June 30.",
            "impact": None, "action": None,
            "stakeholders": ["Finance"]
        }
    return {
        "id": 13, "name": "Accrued Liabilities - Missing at Month End",
        "status": "warn",
        "detail": "Accrued liabilities balance is $0.00 at June 30 despite known unpaid contractor invoices and commissions.",
        "impact": "June expenses understated. Balance sheet liabilities missing.",
        "action": "Book accrual journal entries for known unpaid obligations before closing the period.",
        "stakeholders": ["Finance"]
    }


def check_prepaid_amortization():
    if QB_PREPAID_MOVEMENT > 0:
        return {
            "id": 14, "name": "Prepaid Amortization - Running",
            "status": "pass",
            "detail": f"Prepaid balance decreased by ${QB_PREPAID_MOVEMENT:,.2f} in June. Amortization is current.",
            "impact": None, "action": None,
            "stakeholders": ["Finance"]
        }
    return {
        "id": 14, "name": "Prepaid Amortization - Stopped",
        "status": "warn",
        "detail": f"Prepaid balance unchanged at ${QB_PREPAID_BALANCE:,.2f} for June. No amortization entry found.",
        "impact": "Prepaid assets overstated. Monthly expenses understated.",
        "action": "Calculate monthly amortization amount and post journal entry. Set recurring entry going forward.",
        "stakeholders": ["Finance"]
    }


def check_carta_interest():
    notes = CARTA_CAP_TABLE["convertible_notes"]
    total_principal = sum(n["amount"] for n in notes)
    monthly_interest = sum(n["amount"] * n["interest_rate"] / 12 for n in notes)
    if CARTA_CAP_TABLE["accrued_interest_in_qb"]:
        return {
            "id": 15, "name": "Convertible Note Interest - Accrued",
            "status": "pass",
            "detail": f"Monthly interest (${monthly_interest:,.2f}) on ${total_principal:,.2f} in convertible notes is being accrued.",
            "impact": None, "action": None,
            "stakeholders": ["Finance", "Investors"]
        }
    return {
        "id": 15, "name": "Convertible Note Interest - Not Accrued",
        "status": "fail",
        "detail": f"${total_principal:,.2f} in convertible notes at 6% - monthly interest of ${monthly_interest:,.2f} not being accrued in QB.",
        "impact": f"Interest expense understated by ${monthly_interest:,.2f}/month. Balance sheet liabilities missing.",
        "action": f"Book monthly accrual: Debit Interest Expense ${monthly_interest:,.2f} / Credit Accrued Interest Payable ${monthly_interest:,.2f}.",
        "stakeholders": ["Finance", "Investors"]
    }


def run_all_checks():
    checks = [
        check_stripe_qb_alignment,
        check_stripe_fees_netted,
        check_chargebacks_reversed,
        check_cash_basis_bleed,
        check_deferred_revenue,
        check_duplicate_transactions,
        check_bank_rec,
        check_ar_aging,
        check_hubspot_qb_gap,
        check_ap_balance,
        check_gusto_qb_match,
        check_payroll_split,
        check_accrued_liabilities,
        check_prepaid_amortization,
        check_carta_interest,
    ]
    return [c() for c in checks]


def compute_score(results):
    score_map = {"pass": 10, "warn": 5, "fail": 0}
    total = sum(score_map[r["status"]] for r in results)
    max_score = len(results) * 10
    return round((total / max_score) * 100)


if __name__ == "__main__":
    results = run_all_checks()
    score = compute_score(results)
    counts = {s: sum(1 for r in results if r["status"] == s) for s in ["pass", "warn", "fail"]}
    print("\nData Quality Score: %d/100" % score)
    print("Pass: %d  Warn: %d  Fail: %d\n" % (counts["pass"], counts["warn"], counts["fail"]))
    for r in results:
        icon = {"pass": "[PASS]", "warn": "[WARN]", "fail": "[FAIL]"}[r["status"]]
        print("%s [%02d] %s" % (icon, r["id"], r["name"]))
        print("     %s" % r["detail"])
        if r["action"]:
            print("     -> %s" % r["action"])
        print()
