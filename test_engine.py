import sys
sys.path.insert(0, '.')
from checks.engine import run_all_checks, compute_score

results = run_all_checks()
score = compute_score(results)
counts = {s: sum(1 for r in results if r["status"] == s) for s in ["pass", "warn", "fail"]}
print("Data Quality Score: %d/100" % score)
print("Pass: %d  Warn: %d  Fail: %d\n" % (counts["pass"], counts["warn"], counts["fail"]))
for r in results:
    icon = {"pass": "[PASS]", "warn": "[WARN]", "fail": "[FAIL]"}[r["status"]]
    print("%s [%02d] %s" % (icon, r["id"], r["name"]))
    print("     %s" % r["detail"])
    if r["action"]:
        print("     -> %s" % r["action"])
    print()
