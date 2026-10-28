# GloryStarWear 网站流量增长与改版执行计划

更新时间：2026-09-15

## 先说结论

网站当前的主要问题不是缺少页面或基础 SEO 标签，而是：

1. 非品牌搜索曝光和收录仍然偏少；
2. 页面数量较多，需要继续强化“一个页面只解决一个采购问题”；
3. 工厂、质检、证书和真实案例的一手证据不足；
4. 流量、询盘和“合格询盘”还没有形成稳定的复盘闭环；
5. 当前工作区有 889 个未提交改动，不能在未确认归属和发布范围前整体上线。

共享对话链接目前只能读取到标题“分析网站流量策略”，正文没有被公开抓取出来，浏览器加载也未完成。因此本计划不臆测共享对话的具体内容；它先基于当前仓库、Search Console 记录和 Google Search 官方原则制定。拿到共享对话正文后，只需把其中可验证的方法映射到本计划的对应阶段即可。

本轮已交付一套独立的供应商图册浏览工具：`/products/catalog.html`。它参考 Healongsportswear Yupoo 的真实分组，使用 noindex 控制，服务于买家选款和询盘，不把大量相册直接扩张成搜索引擎薄内容页。

## 当前基线

- 本地审计：146 个 HTML 页面、146 个唯一 canonical/title/description，669 张图片均有 AVIF，最大站内点击深度 2，不可达可索引页面 0；静态站点审计 0 errors。
- 多语言：5 个语言版本、725 个本地化页面，结构审计通过。
- 询盘链路：lead flow contract tests 通过；GA4、首触归因、WhatsApp/邮件点击和资源下载事件已经存在。
- 图册工具：已实时复核 Yupoo，3,373 个参考相册、45 个顶层分类与本地目录逐项一致，新增/缺失产品均为 0，分类数量也无差异；`Stock Item` 下的 11 个子分类和 708 个产品已同步到筛选界面。本地生成 3,372 张来自 `logo_removed` 图册的产品封面缩略图（约 144 MB）和 5.3 MB 目录索引，详情图按点击从原始相册地址加载，并保留失败回退。
- Search Console 最新已记录状态（2026-09-09）：81 个网页已收录、69 个未收录、累计 3 次搜索点击；其中 60 个 URL 属于“已发现但尚未编入索引”。
- 早期查询机会：`/products/private-label-gym-clothing.html` 有 63 次曝光但平均排名 76.4；`/resources/custom-sportswear-tech-pack.html` 平均排名 12.9 但没有点击；首页平均排名 5.7 并产生 2 次点击，因此首页不应大改。
- 站外权威：目前缺少明确的独立公司资料、合作伙伴引用、客户授权案例或行业目录背书。

## 增长策略

用下面的链路做决策：

`可抓取与收录 → 查询/页面匹配 → 一手证据与信任 → 点击 → 询盘 → 合格询盘`

图册目录采用“选款工具 → 询盘”路径，不作为主要自然搜索落地页。自然搜索仍由有明确采购意图的产品页、制造商页和 buyer resources 承接；图册只通过产品 hub、询盘入口和适当的内部链接获得访问。

第一阶段先做一个主题集群，不同时铺开所有运动品类。默认候选是“private-label activewear”；如果新的 28 天 Search Console 数据显示 teamwear 的商业曝光更高，就切换到 custom teamwear。不要因为同义词而新建一批薄页面。

## 分阶段执行

### 阶段 0：基线与发布闸门（1–3 天）

- 导出 Search Console 最近 28 天与前 28 天的 Query、Page、Country、Device 数据，排除品牌词后建立机会表。
- 导出 GA4 落地页、`session_landing`、`quote_start`、`lead_submit_success`、`generate_lead`、WhatsApp、邮件和资源下载数据。
- 将 889 个未提交改动按“生产已上线 / 本地待发布 / 不明归属”分类；没有确认前不整体部署。
- 固定当前生产版本、canonical 域名、sitemap、robots 和 lead 接收状态，建立 7/28/90 天对比基线。

交付物：一份查询—页面—询盘机会表、一份发布范围清单、一份 10 个优先 URL 清单。

### 阶段 1：页面架构与收录质量（第 1–2 周）

- 保持首页主标题和主要信息稳定，仅做 CTA 或模块级实验。
- 维持页面职责：宽页面负责品类/采购项目规划，窄页面负责单品规格、样品和验证；重复意图合并，不再用关键词变体批量建页。
- 建立清晰的内部路径：`首页 → 商业支柱页 → 产品页 → buyer resource → quote/contact`。
- 重点检查 `sportswear-manufacturer.html`、`private-label-activewear-manufacturer.html`、`low-moq-sportswear-manufacturer.html`、`custom-teamwear-uniforms.html` 和高曝光产品页，每页补 2–4 条有决策帮助的上下文内链。
- 对 60 个“已发现未收录”URL，不批量重复申请收录；先提升高商业价值页面的独立价值、目录入口和内容差异，再在 7/14/28 天观察。
- 每次实质改动后再同步 sitemap `lastmod`，并重新生成语言版本；不为了刷新日期而改日期。

交付物：更新后的页面意图表、内链关系、少量优先 URL 的 Search Console 检查记录。

### 阶段 2：商业落地页升级（第 2–4 周）

按“一个页面一个采购决策”逐页升级，优先顺序如下：

1. `/products/private-label-gym-clothing.html`：承接 white-label/private-label gym clothing 查询，首屏直接回答供应范围、路线差异、所需报价资料，并把 CTA 连接到 quote form。
2. `/resources/custom-sportswear-tech-pack.html`：这是当前最接近首页的机会页，强化免费 CSV 的用途、适用边界、下载后的下一步和询盘入口，优化 title/snippet 的点击理由。
3. `/private-label-activewear-manufacturer.html`：明确多款式 activewear collection 的规划、尺码、面料、品牌标签、包装、打样和补单流程，避免与 gym clothing 页重复。
4. `/sportswear-manufacturer.html`、`/low-moq-sportswear-manufacturer.html`、`/custom-teamwear-uniforms.html`：强化买家类型、开发路线、责任交接、报价假设和证据边界。
5. 从新的 GSC 数据中再选 5 个排名 8–20 且有商业曝光的页面做升级，不凭感觉批量改 85 个产品页。

每页升级最低标准：唯一 title/H1、首屏直接答案、采购范围、决策表或清单、可核验证据/限制、2–4 条相关内链、明确 CTA、与可见内容一致的结构化数据和图片 alt。

### 阶段 3：一手证据与品牌权威（第 2–8 周）

优先收集并审核：

- 带日期、地点、主体和授权范围的工厂/样衣/面料/测量/质检/包装/出货照片或视频；
- 证书 PDF 或核验页，包含持证主体、编号、范围、签发方和有效期；
- 至少 1–2 个经客户授权或脱敏的真实项目记录，包含需求、开发决策、样品轮次、QC 节点和交付结果。

资料审核通过后，分别放入 `about-factory.html`、`process.html`、`quality.html`、`certificates.html` 和 `case-studies.html`。在此之前继续明确标注示意图、规划案例和未核验信息，不把它们改写成真实工厂或客户证明。

站外只经营少量可维护渠道：公司 LinkedIn、YouTube、正在使用的 B2B 供应商资料、真实行业/展会/协会目录和获授权的合作伙伴页面。每次分发都提供平台原生内容和稳定 UTM；不买链接、不群发索链、不复制相同宣传文案。

### 阶段 4：内容集群与分发（第 4–12 周）

围绕一个主题集群，优先复用现有资源和文章，而不是继续大量新建 URL。private-label activewear 的建议链路是：

`activewear manufacturer → MOQ → tech pack → fabric → size grading → sample approval → AQL/QC → packaging/labels → quote`

每 4 周完成：4 个旧页面实质升级、2 个有独立价值的 buyer asset、1 个真实证据或项目记录、1–2 次有针对性的专业分发。选题来源按优先级取自 GSC 查询、真实询盘、销售异议和生产记录。

### 阶段 5：转化和数据闭环（持续）

- 在 GA4 中把 `generate_lead` 标记为关键事件，注册 `page_type`、`content_group`、`traffic_channel`、`traffic_source`、`form_location`、`product_interest` 和 `resource_name`。
- 用 DebugView 验证一次完整流程：访问落地页 → 开始报价 → 服务端确认接收 → 只产生一次成功 lead 事件。
- 按落地页、国家、设备、查询主题、来源渠道和合格询盘率复盘；姓名、电话、邮箱和项目自由文本不得送入分析系统。
- 商业页主 CTA 使用 “Build Your Brief”；信息页使用“下载清单 + 进入报价”；WhatsApp/邮件点击只算联系意图，不算已确认 lead。

## 指标与复测节奏

| 时间 | 重点指标 | 判断动作 |
| --- | --- | --- |
| 7 天 | HTTP、canonical、sitemap、抓取、事件和 lead 接收 | 有错误先修复，不做内容大改 |
| 28 天 | 非品牌曝光、点击、CTR、平均排名、Top 20 查询、落地页转化 | 排名 8–20 且有曝光的页面优先升级；排名 1–10 但 CTR 弱的页面先改标题/摘要 |
| 60–90 天 | 合格询盘数、合格率、首次响应时间、来源质量、品牌搜索与回访 | 决定扩展主题、合并页面、保留页面或停止低价值选题 |

## 发布验收

每次 English 页面改动后，生成本地化版本并运行：

```bash
python3 scripts/audit_static_site.py
python3 scripts/audit_locales.py
node scripts/test_lead_flow.mjs
git diff --check
```

通过后再部署；部署后只对少量优先 URL 做 URL Inspection，并记录生产版本、canonical、抓取日期和下一次复测日期。

## 明确不做的事

- 不批量生产同义词页面或仅靠 AI 改写扩大页面数量；
- 不为了“收录数字好看”把隐私页、重定向页或重复页改成可索引；
- 不购买外链、制造论坛链接或交换锚文本；
- 不发布未经核验的 MOQ、价格、交期、产能、证书、客户和工厂所有权声明；
- 不用一次 sitemap 提交或一次“请求编入索引”承诺排名和流量增长。

## 依据

- Google Search Essentials：以有帮助、可靠、面向用户的内容、可抓取链接和真实分发为基础。
- Google AI features：AI Overviews/AI Mode 没有独立的特殊 SEO 技巧，页面仍须先满足普通 Search 的抓取、收录、内容和体验要求。
- Google Search spam policies：大规模无原创价值的页面和操纵性链接可能造成搜索风险。
