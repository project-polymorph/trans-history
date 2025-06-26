#!/bin/bash

# Exit on any error
set -e
export OPENAI_TEMPERATURE=0.7

python .github/scripts/toc/independence_info.py
cp independence_repo.json results/independence_repo.json

python analysis/download.py

echo "Download complete."

# Create results directory if it doesn't exist
mkdir -p results

# Process each search_index.yml file
for index_file in index/*/search_index.yml; do
    # Extract the [name] part from the path
    name=$(basename $(dirname "$index_file"))
    
    # Create output path
    output_file="results/${name}_analysis.yml"
    
    echo "Processing $name..."
    python .github/scripts/file/analysis_search_index.py \
        -i "$index_file" \
        -o "$output_file"
    python analysis/basic_report.py \
        -i "$output_file" \
        -o "results/basic_report/${name}.md"
done

echo "Analysis complete. Results saved in results/"

python analysis/merge_index.py

echo "Merge complete. Results saved in index/combined_index.yml"
