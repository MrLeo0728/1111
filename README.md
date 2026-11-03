# Amazon US 运营工作台

从竞品证据到广告复盘、产品差异化决策的轻量工作台。中文说明，CSV 字段使用英文。无第三方 Python 依赖。

## 立即开始

1. 在 GitHub 打开 `templates/competitors.csv`，点击编辑，填写竞品资料；每条数据保留来源与采集日期。
2. 将其他模板复制到本地 `data/private/`，用 Excel 的“从文本/CSV”按 UTF-8 导入。ASIN 设为文本，金额统一 USD，比例用小数。
3. 先运行虚构示例：

```bash
python3 automation/analyze_ads.py --input examples/ads_sample.csv --output reports/local/ads-review.md
python3 -m unittest discover -s tests -v
```

4. 实际分析：将广告数据按模板映射为 CSV，再运行：

```bash
python3 automation/analyze_ads.py --input data/private/ads.csv --output reports/local/ads-review.md
```

5. 在 GitHub 的 Actions → Workbench checks → Run workflow 可手动运行虚构示例，并下载报告。首次上传后若 Actions 不可用，请检查仓库 Actions 权限。

## 目录与首批文件

| 路径 | 用途 |
|---|---|
| `templates/competitors.csv` | 六个既有 ASIN，身份与来源档案；未核实数据留空 |
| `templates/price_selling_points.csv` | 每个变体每次采集一行；价格、件数、单位价、卖点及证据 |
| `templates/ads.csv` | 按广告组/投放目标/搜索词/匹配类型及周期汇总的广告数据 |
| `templates/differentiation.csv` | A/B/C/D 四方案；需求、数量与款式策略、生产、IP 和加权评分 |
| `templates/experiments.csv` | 将建议转成实验、负责人、期限、指标和结论 |
| `docs/data-dictionary.md` | 字段口径、Excel 公式与空值规则 |
| `docs/weekly-playbook.md` | 每周执行顺序及七步开发流程 |
| `automation/analyze_ads.py` | 数据校验、指标计算、汇总与建议；不修改广告 |
| `automation/config.json` | 可调整的筛查阈值，属于初始假设 |
| `automation/connectors/README.md` | SP-API/Ads API/第三方导出接入约定 |
| `examples/ads_sample.csv` | 虚构广告示例，不是账户实际表现 |
| `tests/test_analyze_ads.py` | 公式、零值、校验和建议逻辑测试 |
| `.github/workflows/checks.yml` | 自动测试及虚构示例报告 artifact |

## 竞品与差异化入口

已预填 B0HJM916X6、B0HJ29ZVMD、B0HKFRH6D6、B0HHX4PFBD、B0HM2VZ1C9、B0HMD1Q18P。仅代表用户提供的研究对象；品类、有效性、价格、销量和卖点均尚待验证。

数量与款式不要直接二选一：先比较到手单位价、使用场景覆盖率、重复款占比、包装体积与退货原因；A–D 分别留作数量价值、场景组合、功能体验、设计礼赠四种待验证方向，绝非已经确定的产品设计。

## 数据边界

本仓库为公开仓库。真实账户广告报表、成本、客户信息、令牌保存在本地 `data/private/`；该目录、真实报告与 `.env` 已忽略。`.gitignore` 不能阻止手动网页上传或已跟踪文件泄露，上传前仍应检查。公开目录只提交模板、公开可核实研究或匿名数据。

空白表示未知，0 表示真实零值。第三方销量/流量估算必须注明估算来源、日期、父子变体口径；不与自有账户数据混用。当前没有接入 Amazon、卖家精灵、西柚或自动调价/竞价接口。
