import argparse, csv, json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

REQUIRED = {"order_id", "order_ts", "customer_id", "sku", "quantity", "unit_price"}

def load_orders(path):
    with open(path, newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or not REQUIRED.issubset(rows[0]):
        raise ValueError("input is missing required order columns")
    return rows

def run(input_path, output_dir):
    rows = load_orders(input_path); output = Path(output_dir)
    for layer in ("bronze", "silver", "gold"): (output / layer).mkdir(parents=True, exist_ok=True)
    with open(output / "bronze" / "orders.jsonl", "w") as out:
        for row in rows: out.write(json.dumps(row) + "\n")
    daily = defaultdict(lambda: {"orders": set(), "revenue": 0.0, "units": 0})
    normalized = []
    for row in rows:
        timestamp = datetime.fromisoformat(row["order_ts"])
        clean = {**row, "order_date": timestamp.date().isoformat(), "quantity": int(row["quantity"]), "unit_price": float(row["unit_price"])}
        clean["revenue"] = round(clean["quantity"] * clean["unit_price"], 2); normalized.append(clean)
        metric = daily[clean["order_date"]]; metric["orders"].add(clean["order_id"]); metric["units"] += clean["quantity"]; metric["revenue"] += clean["revenue"]
    with open(output / "silver" / "orders.jsonl", "w") as out:
        for row in normalized: out.write(json.dumps(row) + "\n")
    with open(output / "gold" / "daily_sales.csv", "w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=["order_date", "orders", "units", "revenue"]); writer.writeheader()
        for day, metric in sorted(daily.items()): writer.writerow({"order_date": day, "orders": len(metric["orders"]), "units": metric["units"], "revenue": round(metric["revenue"], 2)})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--input", required=True); parser.add_argument("--output", required=True)
    run(**vars(parser.parse_args()))
