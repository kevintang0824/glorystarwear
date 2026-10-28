# Search Console 未收录原因与处理计划

更新时间：2026-09-09  
资源：`sc-domain:glorystarwears.com`  
Search Console 报告更新时间：2026-09-04

## 结果总览

概览显示：81 个网页已编入索引，69 个网页未编入索引，累计 3 次网页搜索点击。

| Search Console 原因 | 数量 | 结论 |
| --- | ---: | --- |
| 已发现 - 尚未编入索引 | 60 | Google 已发现 URL，但尚未抓取；优先级和抓取排期问题，暂未看到 noindex 或规范化阻断证据 |
| 已抓取 - 尚未编入索引 | 2 | 已抓取但尚未选择收录，需要优先做页面内容差异、首手证据和内部链接强化，再单次申请收录 |
| 网页会自动重定向 | 6 | 预期行为，不是故障；保留统一 HTTPS、非 www 和 canonical 目标 |
| 被“noindex”标记排除了 | 1 | 预期行为：隐私政策页不应进入自然搜索结果 |
| 备用网页（有适当的规范标记） | 0 | 暂无 Google 报告的 canonical 冲突 |

## 已确认的 2 个“已抓取但尚未编入索引”页面

| URL | 上次抓取 |
| --- | --- |
| `https://glorystarwears.com/faq.html` | 2026-09-06 |
| `https://glorystarwears.com/process.html` | 2026-06-18 |

这两页都有 200 状态、canonical、hreflang 和结构化数据。当前更值得处理的是页面是否给 Google 足够明确、独立且有实际帮助的内容信号，而不是继续堆 meta 标签。

### FAQ 页面

- 已有独立的 FAQPage 内容和买家问题分组。
- 下一步应补充来自真实询盘的高频问题、明确的适用范围和可核验的工厂/交付证据。
- FAQ 内容不能用虚构的客户结果、产能、交期、MOQ 或证书承诺来填充。

### Process 页面

- 已有从 brief、报价/打样、样衣确认到大货/QC/出货的流程说明。
- 已提供 sample approval register 和 checklist 下载入口。
- 下一步应把真实的样衣、面料确认、检验、包装或出货记录接到对应流程节点，并说明资料的主体、日期和授权范围。

## 60 个“已发现但尚未编入索引”页面

这 60 个 URL 的导出记录显示：Google 尚未对这些 URL 完成抓取，抓取日期显示为 `1970-01-01`（代表没有实际抓取记录）。示例包括：

- `/contact.html`
- `/customization.html`
- `/products/accessories.html`
- `/products/athleisure.html`
- `/products/badminton-uniforms.html`
- `/products/baseball-uniforms.html`
- `/products/basketball-jerseys.html`
- `/products/club-fan-merchandise.html`
- `/products/club-hoodies-varsity-jackets.html`
- `/products/cricket-uniforms.html`

报告曲线显示该组数量在 2026-08-29 从 54 增至 60。现阶段不要对 60 个 URL 逐个重复申请收录；应先确保 sitemap、首页/产品集群内部链接和高商业价值页面的优先级清晰，然后等待新的抓取排期。

## 预期排除项

以下 URL 是正常的技术处理，不应为了减少“未收录”数字而改成可索引页面：

- 重定向：`/index.html`、HTTP、www 版本，以及旧的产品路径。
- noindex：`https://glorystarwears.com/privacy.html`。

## 执行顺序

1. 保持当前重定向、canonical、robots 和隐私页 noindex，不对这 7 个预期排除项申请“验证修复”。
2. 对 FAQ 和 Process 做一次真实内容增强：加入真实、获授权的工厂/质检/样衣/交付证据；没有资料前继续保持示意图和规划信息的透明标注。
3. 部署后在 URL 检查中分别检查 FAQ 和 Process，确认线上版本、canonical 和可抓取性无误；每页只申请一次收录。
4. 确认 sitemap 已提交且包含高优先级商业页面；不要批量重复提交同一批 URL。
5. 观察 7、14、28 天的抓取和收录变化，再决定是否对少量高价值“已发现未抓取”页面做 URL 检查。

## 2026-09-09 执行结果

- FAQ URL 检查显示已收录，并已完成一次更新后的收录请求；Search Console 确认网址已加入优先抓取队列。
- Process URL 检查显示已收录，并已完成一次更新后的收录请求；Search Console 确认网址已加入优先抓取队列。
- 已开启第 7、14、28 天观察任务，基线为本次部署和申请收录时的状态；不会因未变化而重复申请。

## 真实证据发布门槛

在收到资料前，不把现有示意视觉改写成“工厂实拍”“客户案例”或“认证证明”。需要的最小资料是：

- 工厂：带拍摄日期/地点和授权的车间、样衣、质检、包装或出货照片/视频；
- 证书：证书 PDF 或核验页，包含持证主体、编号、签发方、范围和有效期；
- 案例：至少 2 个真实项目的产品、数量区间、开发轮次、QC/交付结果和公开授权或脱敏说明。

资料收齐后先做真实性、主体一致性、有效期、隐私脱敏和授权检查，再发布到 `about-factory`、`quality`、`certificates`、`case-studies` 或对应产品页。

## 本次导出

- “已发现 - 尚未编入索引”：`/Users/kevintang/Downloads/glorystarwears.com-Coverage-Drilldown-2026-09-09.zip`
- “已抓取 - 尚未编入索引”：`/Users/kevintang/Downloads/glorystarwears.com-Coverage-Drilldown-2026-09-09 (1).zip`
