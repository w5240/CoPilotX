---
name: tender-search
description: Search and retrieve tender/bidding information from Chinese government procurement websites. Use when user needs to find tenders, filter by region, or get detailed tender information.
allowed-tools: Bash(uv run python ~/.openclaw/skills/tender-search/tender_search.py *)
---

# Tender Search Skill

Searches and retrieves tender/bidding information from Chinese government procurement websites.

## Prerequisites

This skill requires `curl` to be available on the system.

## Usage

### Search Tenders

Search for tenders with optional filters:

```bash
tender-search search [query] [options]
```

**Options:**
- `--region <region>` - Filter by region (e.g., 东阳市, 南浔区, 南漳县)
- `--type <type>` - Filter by type (e.g., 招标, 预告)
- `--limit <number>` - Limit results (default: 20)

**Examples:**
```bash
# Search all tenders
tender-search search

# Search by region
tender-search search --region 东阳市

# Search by region and type
tender-search search --region 南浔区 --type 招标

# Search with query and filters
tender-search search 消毒产品 --region 东阳市 --type 招标
```

### Get Tender Details

Get detailed information about a specific tender:

```bash
tender-search detail <tender-id>
```

**Example:**
```bash
tender-search detail 12345
```

### List Recent Tenders

List the most recent tenders:

```bash
tender-search list [options]
```

**Options:**
- `--limit <number>` - Number of results (default: 20)
- `--region <region>` - Filter by region
- `--type <type>` - Filter by type

**Example:**
```bash
# List recent tenders
tender-search list

# List with filters
tender-search list --region 东阳市 --limit 10
```

## Response Format

The skill returns tender information in the following format:

```json
{
  "date": "2026-03-02",
  "region": "东阳市",
  "type": "招标",
  "title": "消毒产品生产企业卫生许可（延续）",
  "url": "https://..."
}
```

## Common Regions

Common regions that can be used for filtering:
- 东阳市
- 南浔区
- 南漳县
- 滨江区
- 番禺区
- 越秀区
- 荔湾区
- 苍南县
- 永嘉县
- 景东

## Common Types

Common tender types:
- 招标 (Tender)
- 预告 (Pre-announcement)
- 采购 (Procurement)
