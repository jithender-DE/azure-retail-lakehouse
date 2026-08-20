import csv, tempfile, unittest
from pathlib import Path
from src.pipeline import run
class PipelineTests(unittest.TestCase):
 def test_creates_daily_metric(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/"out"; run(Path(__file__).parents[1]/"data/orders.csv", out)
   with open(out/"gold/daily_sales.csv") as f: rows=list(csv.DictReader(f))
   self.assertEqual(rows[0]["revenue"], "65.0")
if __name__ == "__main__": unittest.main()
