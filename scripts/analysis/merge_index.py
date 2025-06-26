import yaml
import json
import os
from pathlib import Path

# Load independence_repo.json
with open('independence_repo.json', 'r', encoding='utf-8') as f:
    repos = json.load(f)

# Create URL mapping
url_mapping = {repo['name']: repo['url'] for repo in repos}

# Initialize combined data
combined_data = {}

# Process each YAML file
index_dir = Path('index')
for yaml_file in index_dir.glob('*/search_index.yml'):
    # Get repo name from parent directory
    repo_name = yaml_file.parent.name
    print(f"Processing {repo_name}")
    base_url = url_mapping.get(repo_name, '')
    
    # Load YAML content
    with open(yaml_file, 'r', encoding='utf-8') as f:
        try:
            data = yaml.safe_load(f)
            new_data = {}
            if data:
                # Add base URL to each entry's link if it's '[Unknown link(update needed'
                for key, value in data.items():
                    # if key contains .md, remove it
                    if '.md' in key:
                        key = key.replace('.md', '')
                    
                    # update key
                    new_key = f"{base_url}/{key}"
                    new_data[new_key] = value
                # Merge into combined data
                combined_data.update(new_data)
        except yaml.YAMLError as e:
            print(f"Error processing {yaml_file}: {e}")

# Save combined data
output_path = 'index/combined_index.yml'
with open(output_path, 'w', encoding='utf-8') as f:
    yaml.dump(combined_data, f, allow_unicode=True, sort_keys=False)

print(f"Combined index saved to {output_path}")
print(f"Total entries: {len(combined_data)}")
