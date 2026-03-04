---
name: email-assistant
description: 智能邮箱管理助手。支持 Gmail/QQ 邮箱，自动同步联系人（自动过滤广告），智能分类邮件为"需要处理"、"到期提醒"、"不需要处理"，每日推送到飞书。支持用户询问任意日期的邮件汇总，以及快速回复指定编号的邮件。
---

# Email Assistant - 智能邮箱管理助手

## 功能概述

1. **多邮箱智能选择** - 配置了 QQ 则只用 QQ，两个都配则汇总两个
2. **智能联系人库** - 自动同步 + 广告发件人过滤
3. **AI 邮件分类** - 自动判断需要处理 / 到期提醒 / 广告
4. **每日推送** - 早上自动推送到飞书
5. **历史查询** - 可查询任意日期的邮件汇总
6. **快速回复** - 说"回复 3 号邮件"可直接回复

## 配置文件

位置：`~/.openclaw/email-config.json`

```json
{
  "timezone": "Asia/Shanghai",  // 邮件日期时区（支持 IANA 时区，如 Asia/Shanghai, UTC, America/New_York）
  "gmail": {
    "email": "your@gmail.com",
    "app_password": "xxx"
  },
  "qq": {
    "email": "your@qq.com",
    "授权码": "xxx"
  },
  "feishu": {
    "webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
  }
}
```

> ⚠️ **timezone** 字段用于解析邮件日期的时区，默认 `Asia/Shanghai`

## 使用方法

### 1. 首次配置

```bash
# 复制配置模板
cp ~/.openclaw/skills/email-assistant/references/config_template.json \
   ~/.openclaw/email-config.json

# 编辑配置
nano ~/.openclaw/email-config.json

# 测试连接
python ~/.openclaw/skills/email-assistant/scripts/test_connection.py
```

### 2. 同步联系人

```bash
python ~/.openclaw/skills/email-assistant/scripts/sync_contacts.py
```

### 3. 每日邮件摘要

```bash
# 今天的摘要（推送到飞书）
python ~/.openclaw/skills/email-assistant/scripts/daily_digest.py

# 只输出，不推送
python ~/.openclaw/skills/email-assistant/scripts/daily_digest.py --no-push
```

### 4. 查询历史邮件

```bash
# 查询 3 月 2 日的邮件
python ~/.openclaw/skills/email-assistant/scripts/daily_digest.py --date 2026-03-02
python ~/.openclaw/skills/email-assistant/scripts/daily_digest.py --date 2026.3.2
```

### 5. 快速回复

```bash
# 预览回复内容（默认模式，不会真的发送）
python ~/.openclaw/skills/email-assistant/scripts/reply_mail.py \
  --index 3 \
  --body "好的，我确认收到，会尽快处理"

# 确认发送（需要加 --confirm 才真正发送）
python ~/.openclaw/skills/email-assistant/scripts/reply_mail.py \
  --index 3 \
  --body "好的，我确认收到，会尽快处理" \
  --confirm
```

> ⚠️ **安全机制**：回复邮件默认只预览，需要加 `--confirm` 参数才真正发送

## 智能分类规则

### 🟡 需要处理
- 包含"请确认"、"请回复"、"需签字"、"需决策"
- 发件人是已知联系人

### ⚠️ 到期提醒
- 域名到期、ASIC/年审、续费
- 包含"到期"、"expire"、"renewal"、"续费"

### ⚪ 不需要处理
- 广告发件人（自动过滤）
- CC 的邮件
- 营销类（LinkedIn、AWS 账单等）

## 输出示例

```
📧 今日邮件摘要 (10封新邮件，4封需要你处理)

🟡 需要你处理:
1. 会计 — BAS季度申报材料需签字确认
2. 律师 — 合同修改意见等你回复
3. 供应商 — XXX项目第二批报价单，需决策
4. GoDaddy — 域名 braidengine.com.au 30天后到期

⚠️ 到期提醒:
• ASIC Annual Review — BraidEngine — 到期: 2026-11-28
• 域名 braidengine.com.au — 到期: 2026-03-28 (30天!)

⚪ 不需要你处理 (6封):
• LinkedIn
• 内部员工 — 周五聚餐投票
• AWS — 账单
```

## 依赖

```bash
uv pip install requests
```

## 文件结构

```
email-assistant/
├── SKILL.md
├── scripts/
│   ├── test_connection.py   # 测试连接
│   ├── sync_contacts.py     # 智能联系人同步
│   ├── daily_digest.py      # AI 分类摘要
│   └── reply_mail.py        # 快速回复
└── references/
    └── config_template.json
```
