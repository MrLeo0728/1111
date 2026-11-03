"""Offline ad review, standard library only. No account writes."""
import argparse
import csv
import json
import math
from datetime import date
from pathlib import Path

FIELDS = 'start_date,end_date,account_timezone,attribution_window,campaign,ad_group,target,search_term,match_type,impressions,clicks,spend_usd,sales_usd,orders,contribution_margin,target_acos'.split(',')
NUMBERS = 'impressions clicks spend_usd sales_usd orders contribution_margin target_acos'.split()


def read_rows(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise ValueError('CSV headers/order must match templates/ads.csv')
        rows, seen, period = [], set(), None
        for line, row in enumerate(reader, 2):
            try:
                if None in row or any(v is None for v in row.values()):
                    raise ValueError('missing or extra columns')
                for key in FIELDS:
                    row[key] = row[key].strip()
                    if key != 'search_term' and not row[key]:
                        raise ValueError(f'{key} is required')
                if date.fromisoformat(row['start_date']) > date.fromisoformat(row['end_date']):
                    raise ValueError('start_date after end_date')
                context = tuple(row[k] for k in FIELDS[:4])
                if period is not None and period != context:
                    raise ValueError('mixed periods, timezones or attribution windows')
                period = context
                identity = tuple(row[k] for k in FIELDS[4:9])
                if identity in seen:
                    raise ValueError('duplicate row identity')
                seen.add(identity)
                for key in NUMBERS:
                    row[key] = float(row[key])
                    if not math.isfinite(row[key]) or row[key] < 0:
                        raise ValueError(f'{key} must be finite and nonnegative')
                for key in ('impressions', 'clicks', 'orders'):
                    if not row[key].is_integer():
                        raise ValueError(f'{key} must be an integer')
                if row['clicks'] > row['impressions'] or row['orders'] > row['clicks']:
                    raise ValueError('orders <= clicks <= impressions required')
                for key in ('contribution_margin', 'target_acos'):
                    if not 0 < row[key] <= 1:
                        raise ValueError(f'{key} must be in (0,1]')
                rows.append(row)
            except ValueError as error:
                raise ValueError(f'line {line}: {error}') from error
    if not rows:
        raise ValueError('no data rows; use examples/ads_sample.csv for a demo')
    return rows


def divide(a, b):
    return a / b if b else None


def metrics(row):
    return dict(ctr=divide(row['clicks'], row['impressions']),
                cpc=divide(row['spend_usd'], row['clicks']),
                cvr=divide(row['orders'], row['clicks']),
                acos=divide(row['spend_usd'], row['sales_usd']),
                roas=divide(row['sales_usd'], row['spend_usd']),
                profit=row['sales_usd'] * row['contribution_margin'] - row['spend_usd'])


def suggest(row, config):
    m = metrics(row)
    if row['clicks'] < config['min_clicks']:
        return '样本不足：继续观察并检查相关性'
    if row['orders'] == 0 and row['spend_usd'] >= config['no_order_spend_usd']:
        return '有花费无单：复核搜索意图、Listing 与归因回补后评估降价或否词'
    if row['sales_usd'] == 0:
        return '暂无归因销售：复核归因与样本，继续观察'
    if m['acos'] > row['contribution_margin']:
        return '超过盈亏线：优先复核成本、相关性与出价'
    if m['acos'] > row['target_acos']:
        return '超过目标 ACOS：评估出价与转化改进'
    if row['orders'] >= config['scale_min_orders']:
        return '可评估小幅扩量：先检查库存、预算与利润护栏'
    return '继续观察，积累转化样本'


def fmt(value, percent=False):
    if value is None:
        return '—'
    return f'{value:.2%}' if percent else f'{value:.2f}'


def escape(value):
    return str(value).replace('|', '\\|').replace('\n', ' ').replace('\r', ' ')


def report(rows, config):
    totals = {k: sum(row[k] for row in rows) for k in NUMBERS[:5]}
    period = rows[0]
    result = ['# 广告复盘报告', '',
              f"周期：{period['start_date']} 至 {period['end_date']}；时区：{escape(period['account_timezone'])}；归因：{escape(period['attribution_window'])}", '',
              '输入 examples 时全部为虚构示例。建议仅供人工复核，不执行广告变更。利润为广告归因销售的贡献利润估算，非店铺净利润。', '',
              f"总花费 USD {totals['spend_usd']:.2f}；归因销售 USD {totals['sales_usd']:.2f}；ACOS {fmt(divide(totals['spend_usd'], totals['sales_usd']), True)}；ROAS {fmt(divide(totals['sales_usd'], totals['spend_usd']))}；贡献利润 USD {sum(metrics(r)['profit'] for r in rows):.2f}", '',
              '| Campaign / Ad group / Target / Search / Match | CTR | CPC USD | CVR | ACOS | ROAS | 盈亏ACOS | 目标ACOS | 贡献利润 USD | 建议 |',
              '|---|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for row in rows:
        m = metrics(row)
        label = ' / '.join(escape(row[k]) for k in FIELDS[4:9])
        result.append('| ' + ' | '.join([label, fmt(m['ctr'], True), fmt(m['cpc']), fmt(m['cvr'], True), fmt(m['acos'], True), fmt(m['roas']), fmt(row['contribution_margin'], True), fmt(row['target_acos'], True), fmt(m['profit']), suggest(row, config)]) + ' |')
    result += ['', '筛查阈值（可调整假设）：' + json.dumps(config, ensure_ascii=False), '', '操作后在 templates/experiments.csv 记录基线、改动、负责人和复盘日期。']
    return '\n'.join(result) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--config', default=str(Path(__file__).with_name('config.json')))
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.config).read_text(encoding='utf-8'))
        for key in ('min_clicks', 'no_order_spend_usd', 'scale_min_orders'):
            value = config[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                raise ValueError(f'invalid threshold: {key}')
        rows = read_rows(args.input)
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report(rows, config), encoding='utf-8')
        print(f'Analyzed {len(rows)} rows; report: {output}')
    except (ValueError, OSError, KeyError) as error:
        parser.exit(2, f'Input error: {error}\n')


if __name__ == '__main__':
    main()
