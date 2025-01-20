#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import argparse
from datetime import datetime
from pathlib import Path
import re

def fetch_data(term="", year="2024", domain="news.transchinese.org", exclude_url_reg=None):
    """
    Fetch JSON data from the transchinese.org API using requests.
    Returns a list of dict items, each containing:
      - date: e.g. "2024-11-02"
      - region: e.g. "中国大陆"
      - url:    archive link
      - link:   original link
      - description: text summary
      
    Args:
        term (str): Search term
        year (str): Year to search
        domain (str): Domain to search
        exclude_url_reg (str): Regular expression pattern to exclude URLs
    """
    api_url = f"https://transchinese.org/api/search?term={term}&year={year}&domain={domain}"
    try:
        resp = requests.get(api_url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        # Filter out items based on URL pattern if exclude_url_reg is provided
        if exclude_url_reg:
            pattern = re.compile(exclude_url_reg)
            data = [item for item in data if not (pattern.search(item.get('url', '')) or pattern.search(item.get('link', '')))]
            
        return data
    except Exception as e:
        print(f"[WARN] Failed to fetch data from {api_url} -> {e}")
        return []

def parse_years(years_arg):
    """Parse year arguments that can be single years or ranges (e.g. 1980-1999)"""
    result = []
    for year_input in years_arg:
        if '-' in year_input:
            start, end = map(int, year_input.split('-'))
            result.extend(range(start, end + 1))
        else:
            result.append(int(year_input))
    return sorted(list(set(result)))  # Remove duplicates and sort

def main():
    parser = argparse.ArgumentParser(description='Fetch data from TransChinese API and save to JSON.')
    parser.add_argument('--term', default="", help='Search term (optional).')
    parser.add_argument(
        '--years', 
        nargs='+', 
        default=["2024"], 
        help='Years to search. Can be single years or ranges (e.g. 2024 or 1980-1999)'
    )
    parser.add_argument('--output', '-o', required=True, help='Output JSON file path.')
    parser.add_argument('--domains', nargs='+', default=["news.transchinese.org"], help='Domains to fetch from.')
    parser.add_argument('--append', action='store_true', help='Append to existing JSON file if it exists.')
    parser.add_argument('--exclude-url-reg', help='Regular expression pattern to exclude URLs.')
    
    args = parser.parse_args()
    years_list = parse_years(args.years)
    
    # 收集所有数据
    all_data = []
    for domain in args.domains:
        domain_data = []
        for year in years_list:
            data = fetch_data(term=args.term, year=year, domain=domain, exclude_url_reg=args.exclude_url_reg)
            domain_data.extend(data)
        all_data.extend(domain_data)
    
    # 如果需要追加且文件存在，则读取现有数据
    existing_data = {"metadata": [], "items": []}
    if args.append and Path(args.output).exists():
        try:
            with open(args.output, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to load existing JSON file: {e}")
    
    # 准备新的元数据
    new_metadata = {
        "query_term": args.term,
        "years": years_list,
        "domains": args.domains,
        "fetch_time": datetime.now().isoformat()
    }
    
    # 保存查询信息和数据
    output_data = {
        "metadata": existing_data["metadata"] + [new_metadata],
        "items": existing_data["items"] + all_data
    }
    
    # 写入JSON文件
    Path(args.output).write_text(json.dumps(output_data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"[INFO] Fetched {len(all_data)} new items, total {len(output_data['items'])} items, saved to: {args.output}")

if __name__ == "__main__":
    main() 