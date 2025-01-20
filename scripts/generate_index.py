#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
from pathlib import Path
from datetime import datetime
import argparse
from typing import Dict, List

from fetch_data import fetch_data
from json_to_markdown_index import generate_markdown_from_json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NewsIndexGenerator:
    def __init__(self, config_path: str, state_file: str = ".news_index_state.json"):
        self.config_path = config_path
        self.state_file = state_file
        self.config = self._load_config()
        self.state = self._load_state()
    
    def _generate_markdown_only(self, target: Dict):
        """Generate markdown from existing JSON file without fetching new data"""
        output_json = target["output_json"]
        output_markdown = target["output_markdown"]
        
        if not Path(output_json).exists():
            logger.warning(f"JSON file not found: {output_json}, skipping markdown generation")
            return False
        
        try:
            logger.info(f"Generating markdown from existing JSON: {output_json}")
            generate_markdown_from_json(
                input_json=output_json,
                output_markdown=output_markdown,
                template_path=target.get("template_path", "templates/新闻报道/新闻索引.template.md"),
                include_desc=target.get("include_description", True)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to generate markdown for {output_json}: {e}")
            return False
    
    def _load_config(self) -> Dict:
        """Load the configuration file"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_state(self) -> Dict:
        """Load or initialize the state file"""
        if Path(self.state_file).exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"queries": {}, "last_update": None}
    
    def _save_state(self):
        """Save the current state"""
        self.state["last_update"] = datetime.now().isoformat()
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def _should_update_query(self, query: Dict, query_hash: str) -> bool:
        """Check if a query needs to be updated based on its update interval"""
        if query_hash not in self.state["queries"]:
            return True
        
        last_update = datetime.fromisoformat(self.state["queries"][query_hash]["last_update"])
        update_interval = query.get("update_interval_hours", 24)
        
        return (datetime.now() - last_update).total_seconds() > update_interval * 3600
    
    def _fetch_data_for_target(self, target: Dict) -> bool:
        """Fetch data for a single target configuration"""
        output_json = target["output_json"]
        output_markdown = target["output_markdown"]
        
        # Create output directory if it doesn't exist
        Path(output_json).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize the output data structure
        output_data = {"metadata": [], "items": []}
        
        updated = False
        for query in target["queries"]:
            query_hash = f"{output_json}:{query['description']}"
            
            if not self._should_update_query(query, query_hash):
                logger.info(f"Skipping query {query['description']}: Up to date")
                continue
            
            # Fetch data
            logger.info(f"Fetching data for query: {query['description']}")
            all_data = []
            for domain in query["domains"]:
                for year in query["years"]:
                    data = fetch_data(
                        term=query.get("term", ""),
                        year=year,
                        domain=domain,
                        exclude_url_reg=query.get("exclude_url_reg")
                    )
                    all_data.extend(data)
            
            # Prepare metadata
            new_metadata = {
                "query_term": query.get("term", ""),
                "years": query["years"],
                "domains": query["domains"],
                "fetch_time": datetime.now().isoformat(),
                "description": query["description"],
                "exclude_url_reg": query.get("exclude_url_reg")
            }
            
            # Update output data
            output_data["metadata"].append(new_metadata)
            output_data["items"].extend(all_data)
            
            # Update state
            self.state["queries"][query_hash] = {
                "last_update": datetime.now().isoformat(),
                "output_path": output_json
            }
            
            updated = True
            logger.info(f"Fetched {len(all_data)} items for {query['description']}")
        
        if updated:
            # Save the combined data to JSON file
            Path(output_json).write_text(
                json.dumps(output_data, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
            
            # Generate markdown
            generate_markdown_from_json(
                input_json=output_json,
                output_markdown=output_markdown,
                template_path=target.get("template_path", "templates/新闻报道/新闻索引.template.md"),
                include_desc=target.get("include_description", True)
            )
        
        return updated
    
    def generate(self, force: bool = False, markdown_only: bool = False):
        """Generate all indexes based on configuration"""
        if markdown_only:
            logger.info("Generating markdown files from existing JSON files...")
            for target in self.config["targets"]:
                self._generate_markdown_only(target)
            return
        
        if force:
            self.state = {"queries": {}, "last_update": None}
        
        updated = False
        for target in self.config["targets"]:
            if self._fetch_data_for_target(target):
                updated = True
        
        if updated:
            self._save_state()
        else:
            logger.info("All targets are up to date")

def main():
    parser = argparse.ArgumentParser(description='Generate news indexes based on configuration file')
    parser.add_argument('--config', default='news_query.json', help='Path to configuration file')
    parser.add_argument('--state', default='.news_index_state.json', help='Path to state file')
    parser.add_argument('--force', action='store_true', help='Force update all targets')
    parser.add_argument('--markdown-only', action='store_true', 
                       help='Only generate markdown files from existing JSON files without fetching new data')
    
    args = parser.parse_args()
    
    generator = NewsIndexGenerator(args.config, args.state)
    generator.generate(args.force, args.markdown_only)

if __name__ == "__main__":
    main() 