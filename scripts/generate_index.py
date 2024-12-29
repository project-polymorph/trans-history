#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import yaml
import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import re

def load_config(config_path="index_config.yml"):
    """
    Load and parse the YAML configuration file.
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def fetch_data(term="", year="2024", domain="news.transchinese.org"):
    """
    Fetch JSON data from the transchinese.org API using requests.
    Returns a list of dict items, each containing:
      - date: e.g. "2024-11-02"
      - region: e.g. "中国大陆"
      - url:    archive link
      - link:   original link
      - description: text summary
    """
    api_url = f"https://transchinese.org/api/search?term={term}&year={year}&domain={domain}"
    try:
        resp = requests.get(api_url, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[WARN] Failed to fetch data from {api_url} -> {e}")
        return []

def group_data_by_region_and_month(data_list):
    """
    Group data by region -> month_key(YYYY-MM).
    Return a nested dict: { region: { 'YYYY-MM': [items...] } }
    """
    grouped = defaultdict(lambda: defaultdict(list))
    for item in data_list:
        date_str = item.get("date", "")
        region = item.get("region", "未知地区") or "未知地区"
        url = item.get("url", "")
        link = item.get("link", "")
        desc = item.get("description", "")

        # Attempt to parse date
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            month_key = date_obj.strftime("%Y-%m")
        except ValueError:
            month_key = "Unknown"

        grouped[region][month_key].append({
            "date": date_str,
            "url": url,
            "link": link,
            "desc": desc
        })
    return grouped

def render_markdown_from_grouped_data(grouped_data, include_desc=False):
    """
    Render grouped data into Markdown text.
    """
    lines = []
    # 按region的名字进行排序
    for region in sorted(grouped_data.keys()):
        lines.append(f"### {region}\n")

        # 按月份逆序（从大到小）排序
        months_sorted = sorted(grouped_data[region].keys(), reverse=True)
        for month_key in months_sorted:
            # 解析YYYY-MM -> "YYYY年MM月"
            if month_key == "Unknown":
                lines.append(f"#### 未知月份\n")
            else:
                try:
                    month_obj = datetime.strptime(month_key, "%Y-%m")
                    month_header = month_obj.strftime("%Y年%m月")
                    lines.append(f"#### {month_header}\n")
                except ValueError:
                    lines.append(f"#### {month_key}\n")

            # 对同一月份内的条目再按日期逆序
            items = grouped_data[region][month_key]
            # 先按照 date_obj 降序
            def parse_date_or_9999(x):
                try:
                    return datetime.strptime(x["date"], "%Y-%m-%d")
                except ValueError:
                    return datetime.max
            items.sort(key=parse_date_or_9999, reverse=True)

            for entry in items:
                # 做一个简易标题，比如根据URL取最后段
                url_clean = entry["url"].rstrip("/")
                last_part = url_clean.split("/")[-1]
                # 尝试去掉非中文(除去a-zA-Z0-9等)
                title = re.sub(r'[a-zA-Z0-9_\-\.]+', '', last_part)
                title = re.sub(r'[^\u4e00-\u9fff]+', '', title)
                # 如果title为空，就用last_part
                if not title:
                    title = last_part

                # 生成Markdown项目
                line = f"- [{title} - archive]({entry['url']}) [original]({entry['link']})"
                if include_desc and entry["desc"]:
                    line += (
                        "\n  <details><summary>查看简要</summary>\n\n"
                        f"  {entry['desc']}\n"
                        "  </details>"
                    )
                lines.append(line)

            lines.append("")  # 分行
        lines.append("")  # 分行
    return "\n".join(lines)

def generate_markdown(term="", years=None, output_file=None, include_desc=False, config_path="index_config.yml"):
    if years is None:
        years = ["2024"]

    # 获取年份范围 - 移到最前面
    years_sorted = sorted([int(y) for y in years])
    year_range = f"{years_sorted[0]}-{years_sorted[-1]}" if len(years_sorted) > 1 else str(years_sorted[0])

    cfg = load_config(config_path=config_path)
    seo = cfg.get("seo", {})
    now_str = datetime.now().strftime("%Y-%m-%d")

    # -- 构建 front matter
    front_matter_lines = []
    year_title = f'{seo.get("title", "信息导航")} ({year_range}年)'
    front_matter_lines.append("---")
    front_matter_lines.append(f'title: "{year_title}"')
    front_matter_lines.append(f'description: "{seo.get("description", "")}"')
    front_matter_lines.append(f'date: "{now_str}"')
    tags = seo.get("tags", [])
    if tags:
        front_matter_lines.append("tags:")
        for t in tags:
            front_matter_lines.append(f"  - {t}")
    front_matter_lines.append("---\n")

    # -- 主体内容
    # 大标题(包含年份)
    main_title = year_title
    body_lines = []
    body_lines.append(f"# {main_title}\n")
    
    # 简要描述
    desc_text = seo.get("description", "")
    if desc_text:
        body_lines.append(f"{desc_text}\n")
        
    # Add year range description
    if len(years_sorted) > 1:
        body_lines.append(f"> 本索引收录了{years_sorted[0]}年至{years_sorted[-1]}年的相关信息。\n")
    else:
        body_lines.append(f"> 本索引收录了{years_sorted[0]}年的相关信息。\n")

    # domains列表
    domains_cfg = cfg.get("domains", [])
    for domain_info in domains_cfg:
        domain_name = domain_info.get("name", "")
        domain_title = domain_info.get("text", "")
        domain_intro = domain_info.get("introduction", "")

        body_lines.append(f"## {domain_title}\n")
        if domain_intro:
            body_lines.append(f"> {domain_intro}\n")

        # 收集所有年份数据
        all_data = []
        for year in years:
            data = fetch_data(term=term, year=year, domain=domain_name)
            all_data.extend(data)

        # 分组 -> 渲染
        grouped = group_data_by_region_and_month(all_data)
        domain_md = render_markdown_from_grouped_data(grouped, include_desc=include_desc)
        body_lines.append(domain_md)

    # 合成
    final_md = "\n".join(front_matter_lines) + "\n".join(body_lines)

    # 写文件 or print
    if output_file:
        Path(output_file).write_text(final_md, encoding='utf-8')
        print(f"[INFO] Generated markdown saved to: {output_file}")
    else:
        print(final_md)

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
    parser = argparse.ArgumentParser(description='Generate markdown index from TransChinese API and YAML config.')
    parser.add_argument('--term', default="", help='Search term (optional).')
    parser.add_argument(
        '--years', 
        nargs='+', 
        default=["2024"], 
        help='Years to search. Can be single years or ranges (e.g. 2024 or 1980-1999)'
    )
    parser.add_argument('--output', '-o', help='Output file path (if not set, print to stdout).')
    parser.add_argument('--description', '-d', action='store_true', help='Include foldable descriptions.')
    parser.add_argument('--config', default="index_config.yml", help='Path to config file.')
    
    args = parser.parse_args()
    years_list = parse_years(args.years)
    
    generate_markdown(
        term=args.term,
        years=years_list,
        output_file=args.output,
        include_desc=args.description,
        config_path=args.config
    )

if __name__ == "__main__":
    main()
