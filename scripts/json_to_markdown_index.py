#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import yaml
import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path
import re

def load_config(config_path="index_config.yml"):
    """Load and parse the YAML configuration file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

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
    """Render grouped data into Markdown text."""
    lines = []
    for region in sorted(grouped_data.keys()):
        lines.append(f"### {region}\n")

        months_sorted = sorted(grouped_data[region].keys(), reverse=False)
        for month_key in months_sorted:
            if month_key == "Unknown":
                lines.append(f"#### 未知月份\n")
            else:
                try:
                    month_obj = datetime.strptime(month_key, "%Y-%m")
                    month_header = month_obj.strftime("%Y年%m月")
                    lines.append(f"#### {month_header}\n")
                except ValueError:
                    lines.append(f"#### {month_key}\n")

            items = grouped_data[region][month_key]
            def parse_date_or_9999(x):
                try:
                    return datetime.strptime(x["date"], "%Y-%m-%d")
                except ValueError:
                    return datetime.max
            items.sort(key=parse_date_or_9999, reverse=True)

            for entry in items:
                url_clean = entry["url"].rstrip("/")
                last_part = url_clean.split("/")[-1]
                # remove xxx_ from the start of the string, xxx can be 0-9 and a-z
                title = re.sub(r'^[0-9a-z]+_', '', last_part)

                # If original link is available, use both links
                if entry.get('link') and entry['link'].lower() != 'unknown':
                    line = f"[{title}]({entry['link']}) [archive]({entry['url']})"
                else:
                    # If no original link, use archive link as the main link
                    line = f"[{title}]({entry['url']})"

                if include_desc and entry["desc"]:
                    line += (
                        f"\n\n{entry['desc']}\n"
                    )
                lines.append(line)

            lines.append("\n")
        lines.append("")
    return "\n".join(lines)

def generate_markdown_from_json(input_json, output_markdown, template_path="templates/新闻报道/新闻索引.template.md", include_desc=False):
    # 读取JSON数据
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data["metadata"]
    items = data["items"]
    
    # 读取模板
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Get all unique years from all metadata entries
    all_years = set()
    for meta in metadata:
        all_years.update(meta["years"])
    years_sorted = sorted(all_years)
    
    # 确定年份范围
    year_range = f"{years_sorted[0]}-{years_sorted[-1]}" if len(years_sorted) > 1 else str(years_sorted[0])
    
    # 生成年份范围描述
    if len(years_sorted) > 1:
        year_range_description = f"> 本索引收录了{years_sorted[0]}年至{years_sorted[-1]}年的相关信息。"
    else:
        year_range_description = f"> 本索引收录了{years_sorted[0]}年的相关信息。"
    
    # 处理数据并生成Markdown
    grouped = group_data_by_region_and_month(items)
    content_md = render_markdown_from_grouped_data(grouped, include_desc=include_desc)
    
    # 填充模板
    final_md = template.format(
        year_range=year_range,
        current_date=datetime.now().strftime("%Y-%m-%d"),
        year_range_description=year_range_description,
        content=content_md
    )
    
    # 输出
    if output_markdown:
        Path(output_markdown).write_text(final_md, encoding='utf-8')
        print(f"[INFO] Generated markdown saved to: {output_markdown}")
    else:
        print(final_md)

def main():
    parser = argparse.ArgumentParser(description='Generate markdown from JSON data and YAML config.')
    parser.add_argument('--input', '-i', required=True, help='Input JSON file path.')
    parser.add_argument('--output', '-o', help='Output markdown file path (if not set, print to stdout).')
    parser.add_argument('--description', '-d', action='store_true', help='Include foldable descriptions.')
    parser.add_argument('--config', default="index_config.yml", help='Path to config file.')
    
    args = parser.parse_args()
    generate_markdown_from_json(args.input, args.output, args.config, args.description)

if __name__ == "__main__":
    main() 