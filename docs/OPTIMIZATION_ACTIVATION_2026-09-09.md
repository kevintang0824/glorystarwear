# SEO / 收录 / 信任证据 / Analytics 激活记录

更新时间：2026-09-09

## 当前状态

### 1. Google Search Console

- 已用 `kevintang0824@gmail.com` 打开 `sc-domain:glorystarwears.com`。
- 概览当前显示：81 个网页已编入索引、69 个网页未编入索引、累计 3 次网页搜索点击。
- 线上验证文件 `https://glorystarwears.com/8022fa20d2ef4befc52093d274ae7687.txt` 返回 HTTP 200。
- DNS TXT 中存在 Google 站点验证记录。
- 线上 `sitemap.xml` 当前包含 142 个 URL；语言 sitemap 当前包含 710 个 URL。

下一步：在正确的 `glorystarwears.com` 资源中读取 69 个未收录 URL 的具体原因，再按原因处理；不对全部 URL 重复申请收录。

> 状态更新：69 个未收录页面的原因已经读取完成；具体拆分与处理顺序见 `docs/GSC_INDEXING_ACTION_PLAN_2026-09-09.md`。当前只对 FAQ、Process 做证据增强和后续单页申请收录，不对预期排除项或 60 个未抓取 URL 批量申请。

### 2. 真实工厂、案例和证书

- 当前仓库没有可公开核验的工厂实拍、客户授权案例、证书 PDF 或审厂报告。
- 现有工厂、质检、包装和案例视觉必须继续标注为示意或规划内容。
- 已准备资料收集和发布规则：`docs/TRUST_EVIDENCE_INTAKE.md`。

下一步：收到真实资料后，先记录主体、拍摄日期、地点、范围、授权、证书有效期和脱敏状态，再替换页面视觉和文字。

### 3. GA4 / GTM / 询盘接收

- 站点已接入 GA4 Measurement ID：`G-3QHK9TGCHQ`。
- 已实现 Consent Mode；访客同意前不加载 Google Analytics。
- 线上 `GET https://glorystarwears.com/api/lead` 返回 `configured: true`，并返回 Turnstile site key。
- `node scripts/test_lead_flow.mjs` 已通过，包含成功、重试、非法来源、缺字段和失败路径测试。
- 仍需在 GA4 后台完成：将 `generate_lead` 标记为关键事件、注册事件级自定义维度、用 DebugView 验证一次真实测试访问，并把 Search Console 资源关联到同一 GA4 媒体资源。
- GTM 不是必须项；当前采用直接 GA4 事件发送。如果要统一管理其他营销标签，需要提供目标 GTM 容器 ID 后再接入。

## 发布前闸门

1. 不提交未经核验的工厂、客户、证书、产能、MOQ、价格或交期声明。
2. 每次页面或 sitemap 改动后运行：

   ```bash
   python3 scripts/audit_static_site.py
   python3 scripts/audit_locales.py
   node scripts/test_lead_flow.mjs
   ```

3. GA4 后台验证 `generate_lead`、`lead_submit_success`、`resource_download`、`whatsapp_click` 和 `session_landing`。
4. 询盘接收方只有在持久化成功后返回 HTTP 2xx；失败时网站不得展示提交成功页。

## Search Console 结果已完成

69 个未编入索引页面的原因已在 `sc-domain:glorystarwears.com` 中读取并导出，具体拆分和处理顺序见 `docs/GSC_INDEXING_ACTION_PLAN_2026-09-09.md`。当前优先级是 FAQ 与 Process 两页的真实内容差异和第一手证据；不对 6 个预期重定向、隐私页 noindex 或 60 个尚未抓取 URL 做批量重复申请。

## 2026-09-09 内容部署记录

- 已部署 FAQ、Process 的证据状态和内容核验区，并同步到法语、西语、葡萄牙语、俄语和简体中文版本。
- 已更新 Factory、Quality、Certificates、Case Studies 的公开证据边界、质量记录、证书适用范围、规划案例披露和页面修改日期。
- Vercel production deployment：`dpl_28pn2wEGQt84Qhyo6sbGHs9Symcv`，生产域名 `https://glorystarwears.com`。
- 线上验收：六个重点页面均返回新内容；`sitemap.xml` 中四个信任页面的 `lastmod` 均为 `2026-09-09`；`/api/lead` 仍为 `configured: true`。
- 本次只发布可由现有资料支持的流程、核验方法和证据状态；真实工厂、证书和客户案例仍等待资料验证。

## 2026-09-09 URL Inspection 与观察任务

- `https://glorystarwears.com/faq.html`：URL 检查显示“网址已收录到 Google”；已提交一次更新后的“请求编入索引”，并确认“已将网址添加到优先抓取队列中”。
- `https://glorystarwears.com/process.html`：URL 检查显示“网址已收录到 Google”；已提交一次更新后的“请求编入索引”，并确认“已将网址添加到优先抓取队列中”。
- 本次没有重复提交其他 URL，也没有提交重定向 URL 或 `privacy.html`。
- 已在 Codex 当前任务中开启 `GloryStarWear Search Console 收录观察`：对比 2026-09-09 基线，重点观察第 7 天（2026-09-16）、第 14 天（2026-09-23）和第 28 天（2026-10-07）的抓取、收录及未收录原因变化；无变化时保持安静。

## 2026-09-09 “已发现但尚未编入索引”专项

- 已完成 60 个目标 URL 的内容、内链和商业搜索覆盖优化：56 个产品页、2 个询盘/定制页、Quality 和 Resources 各 1 页。
- 34 个旧版产品页新增买家简报；22 个已有较完整扩展页保留原差异化内容；产品目录和 llms.txt 增加按购买意图的目标页索引。
- 首页新增 4 个商业搜索路线，直接连接高价值 activewear、teamwear、endurance 和 specialist sportswear 产品页。
- 60 个目标 URL 的 sitemap lastmod 已同步为 2026-09-09；没有对这 60 个 URL 批量重复申请收录。
- 详细改动、验证结果和最新部署版本见 docs/GSC_DISCOVERED_PAGE_OPTIMIZATION_2026-09-09.md。
