import requests
import json
import os
import yaml
from urllib.parse import urljoin

def download_search_index(entry):
    # Create base directory if it doesn't exist
    base_dir = "index"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Create subdirectory using the name
    name_dir = os.path.join(base_dir, entry['name'])
    if not os.path.exists(name_dir):
        os.makedirs(name_dir)
    
    # Construct the search_index.yml URL
    url = urljoin(entry['url'], 'search_index.yml')
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse YAML content
        yaml_content = yaml.safe_load(response.text)
        
        # Save to file
        output_path = os.path.join(name_dir, "search_index.yml")
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_content, f, allow_unicode=True)
            
        print(f"Successfully downloaded search index for {entry['name']}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading search index for {entry['name']} from {url}: {e}")
    except yaml.YAMLError as e:
        print(f"Error parsing YAML for {entry['name']}: {e}")

def main():
    # Read the JSON file
    try:
        with open('results/independence_repo.json', 'r', encoding='utf-8') as f:
            entries = json.load(f)
            
        # Download search index for each entry
        for entry in entries:
            download_search_index(entry)
            
    except FileNotFoundError:
        print("independence_repo.json file not found")
    except json.JSONDecodeError:
        print("Error decoding independence_repo.json")

if __name__ == "__main__":
    main()