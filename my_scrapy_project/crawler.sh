#!/bin/bash

SEED_FILE=$1   # First argument: Seed file containing initial URLs or keywords
NUM_PAGES=$2   # Second argument: Maximum number of articles to scrape
HOPS_AWAY=$3   # Third argument: Maximum depth for crawling internal links
OUTPUT_DIR=$4  # Fourth argument: Output directory for storing results

# Ensure the output directory exists
mkdir -p "$OUTPUT_DIR"

# Set Scrapy environment variables
export PYTHONPATH=$(pwd)  # Ensure Python can locate the Scrapy project
export SCRAPY_SETTINGS_MODULE=my_scrapy_project.settings  # Specify Scrapy settings module
export NUM_PAGES=$NUM_PAGES  # Pass the article limit dynamically
export HOPS_AWAY=$HOPS_AWAY  # Pass the depth limit dynamically

# Run Scrapy crawler with the provided arguments
scrapy crawl natural_disasters \
    -a seed_file="$SEED_FILE" \
    -a num_pages="$NUM_PAGES" \
    -a hops_away="$HOPS_AWAY" \
    -a output_dir="$OUTPUT_DIR"
