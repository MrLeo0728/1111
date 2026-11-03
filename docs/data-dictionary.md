# 数据口径与填写规则

## 通用

日期 `YYYY-MM-DD`，广告周期采用账户时区并包含首尾日期；金额 USD，不含货币符号；比例为 0–1 小数；件数、曝光、点击和订单是非负整数。未知字段留空，不能用 0 替代。`source_type` 使用 user_provided / verified_public / third_party_estimate / hypothesis；来源链接和采集时间随记录保留。ASIN 是子体还是父体必须注明。

## 竞品档案与价格卖点

`competitors.csv`：asin、marketplace、parent_asin、variant、brand、category、product_url、source_type、checked_on、notes。每个子 ASIN 一行；父 ASIN 不计入同一商品销量之和。

`price_selling_points.csv`：snapshot_date、asin、variant、list_price_usd（页面划线价，可空）、sale_price_usd（显示售价）、coupon_usd（已核实的等值优惠）、coupon_eligibility、effective_price_usd、pack_qty、unit_price_usd、rating、review_count、estimated_monthly_units、visual_style、main_claim、customer_pain、evidence_url、source_type、notes。优惠是否可叠加、Prime/订阅等条件写入 eligibility；不明确时到手价留空。评分和评论量按当时页面口径记录，不推断子体独立评论。

Excel：到手价=已确认售价−可用优惠；单位价=到手价/件数。件数必须同口径，例如套装不能与单个混比。销量估算没有来源时留空，评分不构成销量证据。

## 广告输入 ads.csv

| 字段 | 定义 |
|---|---|
| start_date / end_date / account_timezone | 周期与账户时区；同一文件须一致 |
| attribution_window | 归因窗口标签，例如 7d；同文件一致，勿混合不同报表类型 |
| campaign / ad_group / target / search_term / match_type | 行唯一粒度；无搜索词可空，其他身份字段必填 |
| impressions / clicks / spend_usd / sales_usd / orders | 同周期同归因指标，不要混入总销售额 |
| contribution_margin | 广告前贡献毛利率=(净销售额−货品−包装−运费关税−佣金−履约费−退货准备)/净销售额 |
| target_acos | 当前策略目标 ACOS，非平台默认标准 |

脚本要求完整数字、非负、点击≤曝光、orders≤clicks（此模板限定订单口径，非售出件数），毛利率和 target_acos 在 (0,1]。周期内不重复相同五项身份字段；不能把 campaign 汇总与搜索词明细重复导入。若业务归因口径确实允许订单超过点击，请先修改口径和校验，再导入。

| 指标 | 公式 | 分母为零 |
|---|---|---|
| CTR | clicks/impressions | 未定义 |
| CPC | spend/clicks | 未定义 |
| CVR | orders/clicks | 未定义 |
| ACOS | spend/广告归因 sales | 未定义，单独筛查有花费无销售 |
| ROAS | 广告归因 sales/spend | 未定义 |
| 盈亏平衡 ACOS | contribution_margin | 毛利未知则不判断 |
| 广告后贡献利润估算 | sales×contribution_margin−spend | 仅归因销售口径，非店铺净利润 |

Excel 示例：`=IF(sales_cell=0,"",spend_cell/sales_cell)`；不要用 IFERROR(...,0) 掩盖无分母。汇总 ACOS 使用总花费/总销售额，不平均行 ACOS；各行毛利不同时先逐行计算利润再相加。不计算 TACOS，除非另有匹配周期的店铺总销售额。

## 差异化与实验

`differentiation.csv` 包含 concept_id、direction、target_customer、scenario、pain_evidence、competitor_gap、pack_qty、style_mix、material_process、target_price_usd、target_landed_cost_usd、moq、lead_days、commercial_score、production_score、ip_score、weighted_score、ip_status、ip_evidence、fatal_blocker、validation、decision。成本和规格均为开发目标，未报价不视为事实。

评分 1–5，高分更优：总分=商业×40%+生产×40%+IP可控性×20%。任一评分缺失则总分留空；IP 未检索不得给分。`fatal_blocker` 为重大生产障碍或明显侵权线索时不得用总分抵消。IP 状态：未检索 / 需进一步核查 / 发现明显线索 / 本次范围内未发现明显线索；记录数据库、检索词、日期、地域、编号链接和覆盖范围。初查不是法律意见或不侵权保证。

`experiments.csv`：记录问题、假设、基线、单项改动、主指标、护栏指标、期限、负责人、结果及下一步。尚无基线时先采集，不填虚构结论。
