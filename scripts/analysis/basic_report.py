import yaml
from datetime import datetime
import argparse

def load_analysis_results(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def generate_markdown_report(input_file, output_file):
    # Load analysis results
    results = load_analysis_results(input_file)
    
    # Prepare markdown content
    markdown = [
        "# Search Index Analysis Report\n",
        "## Timeline Distribution",
        "",
        "| Year | Count |",
        "|------|-------|",
    ]
    
    # Add year connections
    for year, count in results['year_summary'].items():
        markdown.append(f"| {year} | {count} |")
    
    markdown.extend([
        "",
        "## Top Tags",
        "",
        "| Tag | Count |",
        "|-----|-------|",
    ])
    
    # Add top 20 tags, sorted by count
    sorted_tags = sorted(results['tag_summary'].items(), key=lambda item: item[1], reverse=True)
    for tag, count in sorted_tags[:50]:
        markdown.append(f"| {tag} | {count} |")
    
    markdown.extend([
        "",
        "## Regional Distribution",
        "",
        "| Region | Count | Percentage |",
        "|--------|-------|------------|",
    ])
    
    # Calculate total for percentages
    total_regions = sum(results['region_summary'].values())
    
    # Add region statistics, sorted by count
    sorted_regions = sorted(results['region_summary'].items(), key=lambda item: item[1], reverse=True)
    for region, count in sorted_regions:
        percentage = (count / total_regions) * 100
        markdown.append(f"| {region} | {count} | {percentage:.1f}% |")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Markdown report from analysis results')
    parser.add_argument('-i', '--input', required=True,
                        help='Input analysis YAML file path')
    parser.add_argument('-o', '--output', required=True,
                        help='Output Markdown file path')

    args = parser.parse_args()
    generate_markdown_report(args.input, args.output)
