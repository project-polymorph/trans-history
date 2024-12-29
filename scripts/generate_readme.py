import os
import argparse
from pathlib import Path
import re
from datetime import datetime

def extract_year(filename):
    # Extract year from filename like 2024.md or containing 4 digits
    match = re.search(r'(\d{4})', filename)
    return int(match.group(1)) if match else None

def scan_directory(directory):
    # Scan directory for markdown files and group by year
    files_by_year = {}
    for file in Path(directory).glob('**/*.md'):
        if file.name == 'README.md':
            continue
        year = extract_year(file.name)
        if year:
            relative_path = file.relative_to(directory)
            files_by_year.setdefault(year, []).append(str(relative_path))
    return files_by_year

def generate_readme(target_dir):
    files_by_year = scan_directory(target_dir)
    now_str = datetime.now().strftime("%Y-%m-%d")
    
    # Define descriptions based on directory type
    is_with_desc = "with_desc" in str(target_dir)
    desc_text = "这是一个中文跨性别相关新闻、研究、政策等事件的时间线索引，收录了各个年份重要的社会、文化、政策变迁记录。"
    type_desc = "本索引包含详细事件描述，适合深入了解历史背景。" if is_with_desc else "本索引为简略版本，仅包含事件链接。"
    
    content = []
    # Add front matter
    content.extend([
        "---",
        'title: "华语跨性别历史时间线索引"',
        f'description: "{desc_text}"',
        f'date: "{now_str}"',
        "tags:",
        "  - 跨性别",
        "  - LGBTQ",
        "  - 性别友善",
        "  - 历史记录",
        "---\n"
    ])
    
    # Main content with descriptions
    content.append("# 跨性别时间线索引\n")
    content.append(f"{desc_text}\n")
    content.append(f"> {type_desc}\n")
    
    if not files_by_year:
        content.append("\n未找到包含年份的markdown文件。")
    else:
        # Generate year index
        content.append("\n## 年份索引\n")
        
        # Sort years in descending order
        for year in sorted(files_by_year.keys(), reverse=True):
            content.append(f"\n### {year}年\n")
            for file in sorted(files_by_year[year]):
                content.append(f"- [{file}]({file})")
    
    # Write to README.md in target directory
    readme_path = Path(target_dir) / "README.md"
    with open(readme_path, "w", encoding='utf-8') as f:
        f.write("\n".join(content))
    
    print(f"索引已生成到: {readme_path}")

def main():
    parser = argparse.ArgumentParser(description='生成markdown文件索引')
    parser.add_argument('directory', help='要扫描的目标目录')
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        print(f"错误: {args.directory} 不是有效目录")
        return
    
    generate_readme(args.directory)

if __name__ == "__main__":
    main()