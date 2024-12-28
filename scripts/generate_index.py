import requests
import json
import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path

def fetch_and_generate_markdown(term="", year="2024", domain="news.transchinese.org", output_file=None, include_desc=False):
    api_url = f"https://transchinese.org/api/search?term={term}&year={year}&domain={domain}"
    
    response = requests.get(api_url, timeout=15)
    data_list = response.json()
    
    # Modified to group by region and month
    grouped = defaultdict(lambda: defaultdict(list))
    for item in data_list:
        date_str = item.get("date", "")
        region = item.get("region", "未知地区")
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
    
    # Sort articles within each month by date in reverse order
    for reg in grouped:
        for month in grouped[reg]:
            grouped[reg][month].sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"), reverse=True)
    
    markdown_lines = []
    
    for reg in sorted(grouped.keys()):
        markdown_lines.append(f"## {reg}")
        
        for month in sorted(grouped[reg].keys()):
            month_date = datetime.strptime(month, "%Y-%m")
            month_header = month_date.strftime("%Y年%m月")
            markdown_lines.append(f"\n### {month_header}\n")
            
            for entry in grouped[reg][month]:
                the_url = entry["url"].rstrip("/")
                last_part = the_url.split("/")[-1]
                
                splitted = last_part.split("_", 1)
                title = splitted[1] if len(splitted) == 2 else last_part
                
                archive_link = entry["url"]
                original_link = entry["link"]
                
                line = f"- [{title} - archive]({archive_link}) [original]({original_link})"
                if include_desc and entry["desc"]:
                    line += f"\n  <details><summary>Description</summary>\n\n  {entry['desc']}\n  </details>"
                markdown_lines.append(line)
    
    result_md = "\n".join(markdown_lines)
    
    if output_file:
        Path(output_file).write_text(result_md, encoding='utf-8')
        print(f"Generated markdown saved to: {output_file}")
    else:
        print(result_md)

def main():
    parser = argparse.ArgumentParser(description='Generate markdown index from TransChinese API')
    parser.add_argument('--term', default="", help='Search term')
    parser.add_argument('--year', default="2024", help='Year to search')
    parser.add_argument('--domain', default="news.transchinese.org", help='Domain to search')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--description', '-d', action='store_true', help='Include foldable descriptions')
    
    args = parser.parse_args()
    
    fetch_and_generate_markdown(
        term=args.term,
        year=args.year,
        domain=args.domain,
        output_file=args.output,
        include_desc=args.description
    )

if __name__ == "__main__":
    main()
