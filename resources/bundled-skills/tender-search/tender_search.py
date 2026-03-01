#!/usr/bin/env python3
"""
Tender Search Skill
Search and retrieve tender/bidding information from Chinese government procurement websites.
"""

import sys
import json
import re
import argparse
from typing import List, Dict, Optional
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError
from html.parser import HTMLParser


# Base URL
BASE_URL = "https://zb.yfb.qianlima.com/yfbsemsite/mesinfo/zbpglist"


class TenderParser(HTMLParser):
    """
    HTML parser to extract tender information from table rows.
    """

    def __init__(self):
        super().__init__()
        self.tenders = []
        self.current_row = []
        self.current_cell = []
        self.in_td = False
        self.in_a = False
        self.current_href = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.current_row = []
        elif tag == 'td':
            self.in_td = True
            self.current_cell = []
        elif tag == 'a' and self.in_td:
            self.in_a = True
            for attr, value in attrs:
                if attr == 'href':
                    self.current_href = value

    def handle_endtag(self, tag):
        if tag == 'tr' and len(self.current_row) >= 4:
            self.tenders.append(self.current_row)
        elif tag == 'td':
            self.in_td = False
            self.current_row.append(''.join(self.current_cell))
        elif tag == 'a':
            self.in_a = False

    def handle_data(self, data):
        if self.in_td:
            self.current_cell.append(data)


def fetch_tenders() -> List[Dict]:
    """
    Fetch tender list from the website.

    Returns:
        List of tender dictionaries
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        request = Request(BASE_URL, headers=headers)
        with urlopen(request, timeout=30) as response:
            html = response.read().decode('utf-8')

        # Parse HTML
        parser = TenderParser()
        parser.feed(html)

        tenders = []

        # Extract data from parsed rows
        for row in parser.tenders:
            try:
                if len(row) < 4:
                    continue

                date_cell = row[0].strip()
                region_cell = row[1].strip()
                type_cell = row[2].strip()
                title_cell = row[3].strip()

                # Extract title and URL from title cell
                title_match = re.search(r'>([^<]+)<', title_cell)
                if title_match:
                    title = title_match.group(1).strip()
                else:
                    title = title_cell

                url_match = re.search(r'href="([^"]+)"', title_cell)
                if url_match:
                    url = url_match.group(1)
                    # Make URL absolute if it's relative
                    if url and not url.startswith('http'):
                        url = f"https://zb.yfb.qianlima.com{url}"
                else:
                    url = ''

                if title and date_cell:
                    tenders.append({
                        'date': date_cell,
                        'region': region_cell,
                        'type': type_cell,
                        'title': title,
                        'url': url
                    })
            except Exception:
                # Skip rows with errors
                continue

        return tenders

    except URLError as e:
        print(f"Error fetching tenders: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return []


def filter_tenders(tenders: List[Dict], region: Optional[str] = None,
                  type_filter: Optional[str] = None, query: Optional[str] = None) -> List[Dict]:
    """
    Filter tenders based on criteria.

    Args:
        tenders: List of tender dictionaries
        region: Region filter (e.g., '东阳市')
        type_filter: Type filter (e.g., '招标')
        query: Text search query

    Returns:
        Filtered list of tenders
    """
    filtered = tenders

    if region:
        filtered = [t for t in filtered if region in t.get('region', '')]

    if type_filter:
        filtered = [t for t in filtered if type_filter in t.get('type', '')]

    if query:
        filtered = [t for t in filtered if query.lower() in t.get('title', '').lower()]

    return filtered


def format_tender(tender: Dict) -> str:
    """
    Format a tender for display.

    Args:
        tender: Tender dictionary

    Returns:
        Formatted string
    """
    return f"""日期: {tender['date']}
地区: {tender['region']}
类型: {tender['type']}
标题: {tender['title']}
链接: {tender.get('url', 'N/A')}
"""


def print_tenders(tenders: List[Dict], limit: Optional[int] = None):
    """
    Print tenders in a readable format.

    Args:
        tenders: List of tender dictionaries
        limit: Maximum number of tenders to display
    """
    if not tenders:
        print("No tenders found.")
        return

    display_tenders = tenders[:limit] if limit else tenders

    for i, tender in enumerate(display_tenders, 1):
        print(f"\n--- Tender {i} ---")
        print(format_tender(tender))

    print(f"\nTotal: {len(display_tenders)} tenders displayed")


def search_tenders(query: Optional[str] = None, region: Optional[str] = None,
                  type_filter: Optional[str] = None, limit: Optional[int] = None):
    """
    Search and display tenders.

    Args:
        query: Search query
        region: Region filter
        type_filter: Type filter
        limit: Result limit
    """
    print(f"Searching tenders...")
    if query:
        print(f"Query: {query}")
    if region:
        print(f"Region: {region}")
    if type_filter:
        print(f"Type: {type_filter}")
    print()

    # Fetch all tenders
    all_tenders = fetch_tenders()

    if not all_tenders:
        print("No tenders found on the website.")
        return

    # Apply filters
    filtered = filter_tenders(all_tenders, region=region, type_filter=type_filter, query=query)

    # Display results
    print_tenders(filtered, limit=limit)


def list_recent_tenders(limit: Optional[int] = None, region: Optional[str] = None,
                      type_filter: Optional[str] = None):
    """
    List recent tenders.

    Args:
        limit: Result limit
        region: Region filter
        type_filter: Type filter
    """
    print("Fetching recent tenders...")
    if region:
        print(f"Region: {region}")
    if type_filter:
        print(f"Type: {type_filter}")
    print()

    # Fetch all tenders
    all_tenders = fetch_tenders()

    if not all_tenders:
        print("No tenders found on the website.")
        return

    # Apply filters
    filtered = filter_tenders(all_tenders, region=region, type_filter=type_filter)

    # Display results
    print_tenders(filtered, limit=limit)


def main():
    parser = argparse.ArgumentParser(
        description='Search and retrieve tender/bidding information',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search
  %(prog)s search --region 东阳市
  %(prog)s search --region 南浔区 --type 招标
  %(prog)s search 消毒产品 --region 东阳市
  %(prog)s list --limit 10
  %(prog)s list --region 东阳市 --type 招标
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for tenders')
    search_parser.add_argument('query', nargs='?', help='Search query')
    search_parser.add_argument('--region', help='Filter by region (e.g., 东阳市, 南浔区)')
    search_parser.add_argument('--type', dest='type_filter', help='Filter by type (e.g., 招标, 预告)')
    search_parser.add_argument('--limit', type=int, help='Limit results (default: 20)')

    # List command
    list_parser = subparsers.add_parser('list', help='List recent tenders')
    list_parser.add_argument('--region', help='Filter by region (e.g., 东阳市, 南浔区)')
    list_parser.add_argument('--type', dest='type_filter', help='Filter by type (e.g., 招标, 预告)')
    list_parser.add_argument('--limit', type=int, help='Limit results (default: 20)')

    args = parser.parse_args()

    if args.command == 'search':
        search_tenders(
            query=args.query,
            region=args.region,
            type_filter=args.type_filter,
            limit=args.limit
        )
    elif args.command == 'list':
        list_recent_tenders(
            limit=args.limit,
            region=args.region,
            type_filter=args.type_filter
        )
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
