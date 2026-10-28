# GSC “已发现但尚未编入索引”页面优化记录

更新时间：2026-09-09  
资源：sc-domain:glorystarwears.com  
来源：/Users/kevintang/Downloads/glorystarwears.com-Coverage-Drilldown-2026-09-09.zip

## 本次范围

Search Console 导出的 60 个目标 URL 包含：

- 56 个 /products/*.html 产品页；
- contact.html、customization.html、quality.html、resources/index.html 4 个支撑页。

这批 URL 的共同状态是 Google 已发现但没有实际抓取记录；因此本次重点是提高页面独立价值、商业意图清晰度和从目录到页面的可发现路径，不对 60 个 URL 做批量“请求编入索引”。

## 已完成的优化

### 1. 页面内容质量

- 34 个旧版产品页新增“Commercial buyer brief”区块，围绕产品/使用者、尺码与数量、面料与装饰、包装、样品批准和质量记录组织内容；
- 22 个原本已有较完整的产品扩展页保留现有差异化内容，未重复添加模板段落；
- contact.html 新增询盘字段准备路径；
- customization.html 新增装饰、品牌资料、审批和询盘路径；
- quality.html 新增质量证据、检验范围、异常处理和报价交接路径；
- resources/index.html 新增按产品、规格、供应商验证、质量和询盘阶段选择指南的路径。

所有新增文案只描述采购方应准备、确认和留存的资料。没有新增虚假的工厂照片、证书、产能、价格、交期或客户结果。

### 2. 内部链接和商业搜索覆盖

- 首页新增 4 个商业搜索路线，直链到 private-label activewear、teamwear、endurance 和 specialist sportswear 的高价值产品页；
- 产品目录新增 4 个购买意图分组，直链到本次 56 个目标产品页；
- 每个旧版目标产品页连接父级产品范围、报价清单、Process、Quality 和 FAQ；
- llms.txt 新增可读的 Priority Product Page Index，按 activewear、teamwear、endurance、court/combat 等商业主题列出 56 个目标 URL；
- 60 个目标 URL 的 sitemap lastmod 同步为 2026-09-09；
- 目录显示的产品卡数量保持为实际 87 个，避免用户看到错误的分类数量。

## 验证结果

本地检查已通过：

- scripts/audit_static_site.py：通过；最大点击深度 2，不可达可索引页面 0；
- scripts/audit_locales.py：通过；5 个语言版本、725 个本地化页面结构检查通过；
- scripts/test_lead_flow.mjs：通过；
- git diff --check：通过。

线上已回读确认：

- 产品页包含 Commercial buyer brief；
- 产品目录包含 Browse product pages by buying intent；
- llms.txt 包含 Priority Product Page Index 和 2026-09-09 更新日期；
- sitemap.xml 中产品页、联系页和资源页的 lastmod 均为 2026-09-09。

生产部署：

- Vercel deployment：dpl_7KiKzEyYKewAxEzErSrR4pX2Wy4c
- 生产域名：https://glorystarwears.com

## 后续观察

已存在的 Search Console 观察任务继续按 7、14、28 天节点运行：

- 2026-09-16：观察抓取、收录数量和新出现的未收录原因；
- 2026-09-23：判断目录入口和重点产品页是否开始被抓取；
- 2026-10-07：决定是否只对少量高商业价值 URL 做单页检查。

收录不是 sitemap 或单次请求可以保证的结果。下一次判断应以实际抓取、规范 URL、页面选择和搜索表现为依据，不以“已发现”数量单独作为成功标准。
