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

        months_sorted = sorted(grouped_data[region].keys(), reverse=True)
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
                title = re.sub(r'[a-zA-Z0-9_\-\.]+', '', last_part)
                title = re.sub(r'[^\u4e00-\u9fff]+', '', title)
                if not title:
                    title = last_part

                line = f"- [{title} - archive]({entry['url']}) [original]({entry['link']})"
                if include_desc and entry["desc"]:
                    line += (
                        "\n  <details><summary>查看简要</summary>\n\n"
                        f"  {entry['desc']}\n"
                        "  </details>"
                    )
                lines.append(line)

            lines.append("")
        lines.append("")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description='Generate markdown from JSON data and YAML config.')
    parser.add_argument('--input', '-i', required=True, help='Input JSON file path.')
    parser.add_argument('--output', '-o', help='Output markdown file path (if not set, print to stdout).')
    parser.add_argument('--description', '-d', action='store_true', help='Include foldable descriptions.')
    parser.add_argument('--config', default="index_config.yml", help='Path to config file.')
    
    args = parser.parse_args()
    
    # 读取JSON数据
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    metadata = data["metadata"]
    items = data["items"]
    
    # 读取配置
    cfg = load_config(config_path=args.config)
    seo = cfg.get("seo", {})
    
    # 确定年份范围
    years_sorted = sorted(metadata["years"])
    year_range = f"{years_sorted[0]}-{years_sorted[-1]}" if len(years_sorted) > 1 else str(years_sorted[0])
    
    # 生成front matter
    front_matter_lines = []
    year_title = f'{seo.get("title", "信息导航")} ({year_range}年)'
    front_matter_lines.extend([
        "---",
        f'title: "{year_title}"',
        f'description: "{seo.get("description", "")}"',
        f'date: "{datetime.now().strftime("%Y-%m-%d")}"'
    ])
    
    tags = seo.get("tags", [])
    if tags:
        front_matter_lines.append("tags:")
        for t in tags:
            front_matter_lines.append(f"  - {t}")
    front_matter_lines.append("---\n")
    
    # 生成主体内容
    body_lines = [
        f"# {year_title}\n"
    ]
    
    if seo.get("description"):
        body_lines.append(f"{seo['description']}\n")
    
    if len(years_sorted) > 1:
        body_lines.append(f"> 本索引收录了{years_sorted[0]}年至{years_sorted[-1]}年的相关信息。\n")
    else:
        body_lines.append(f"> 本索引收录了{years_sorted[0]}年的相关信息。\n")
    
    # 处理数据并生成Markdown
    grouped = group_data_by_region_and_month(items)
    content_md = render_markdown_from_grouped_data(grouped, include_desc=args.description)
    body_lines.append(content_md)
    
    # 合成最终的Markdown
    final_md = "\n".join(front_matter_lines) + "\n".join(body_lines)
    
    # 输出
    if args.output:
        Path(args.output).write_text(final_md, encoding='utf-8')
        print(f"[INFO] Generated markdown saved to: {args.output}")
    else:
        print(final_md)

if __name__ == "__main__":
    main() 