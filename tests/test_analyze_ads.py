import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ads', ROOT / 'automation/analyze_ads.py')
ads = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ads)


class AdsTests(unittest.TestCase):
    def setUp(self):
        self.rows = ads.read_rows(ROOT / 'examples/ads_sample.csv')
        self.config = dict(min_clicks=20, no_order_spend_usd=15, scale_min_orders=3)

    def test_known_metrics(self):
        m = ads.metrics(self.rows[1])
        self.assertEqual(m['acos'], .5)
        self.assertEqual(m['roas'], 2)
        self.assertAlmostEqual(m['profit'], -9)
        self.assertAlmostEqual(m['ctr'], .04)
        self.assertAlmostEqual(m['cvr'], .1)

    def test_zero_denominators(self):
        row = dict(self.rows[0], impressions=0, clicks=0, spend_usd=0, sales_usd=0, orders=0)
        self.assertTrue(all(ads.metrics(row)[k] is None for k in ('ctr', 'cpc', 'cvr', 'acos', 'roas')))

    def test_review_routes(self):
        expected = ['有花费无单', '超过盈亏线', '可评估小幅扩量', '样本不足']
        for row, label in zip(self.rows, expected):
            self.assertIn(label, ads.suggest(row, self.config))

    def check_bad(self, rows):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.csv'
            with path.open('w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=ads.FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaises(ValueError):
                ads.read_rows(path)

    def test_bad_values_and_duplicates(self):
        for key, value in [('clicks', -1), ('spend_usd', 'NaN'), ('orders', 100), ('contribution_margin', 0), ('impressions', 1.2), ('start_date', 'bad')]:
            self.check_bad([dict(self.rows[0], **{key: value})])
        self.check_bad([self.rows[0], self.rows[0]])
        self.check_bad([self.rows[0], dict(self.rows[1], attribution_window='14d')])
        self.check_bad([])

    def test_weighted_totals(self):
        result = ads.report(self.rows, self.config)
        self.assertIn('ACOS 38.33%', result)
        self.assertIn('贡献利润 USD -6.00', result)

    def test_all_template_row_widths(self):
        for path in (ROOT / 'templates').glob('*.csv'):
            with path.open(newline='', encoding='utf-8') as f:
                rows = list(csv.reader(f))
            for row in rows[1:]:
                self.assertEqual(len(row), len(rows[0]), path.name)


if __name__ == '__main__':
    unittest.main()
