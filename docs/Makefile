HISTORICAL := 1980-1999
RECENT := $(shell seq 2000 2024)
FETCH_SCRIPT := ../scripts/fetch_data.py
MARKDOWN_SCRIPT := ../scripts/json_to_markdown.py
README_SCRIPT := ../scripts/generate_readme.py
JSON_DIR := 新闻报道/json

all: fetch generate readme

# Fetch data targets
fetch: fetch_historical fetch_recent

fetch_historical: $(JSON_DIR)/historical.json

$(JSON_DIR)/historical.json:
	@mkdir -p 新闻报道 $(JSON_DIR)
	python $(FETCH_SCRIPT) \
		--years $(HISTORICAL) \
		--domains news.transchinese.org \
		--output $@ \
		--append

fetch_recent: $(RECENT:%=$(JSON_DIR)/%.json)

$(JSON_DIR)/%.json:
	@mkdir -p 新闻报道 $(JSON_DIR)
	python $(FETCH_SCRIPT) \
		--years $* \
		--domains news.transchinese.org \
		--output $@ \
		--append

# Generate markdown targets
generate: generate_historical generate_recent

generate_historical: 新闻报道/$(HISTORICAL).md

新闻报道/$(HISTORICAL).md: $(JSON_DIR)/historical.json
	python $(MARKDOWN_SCRIPT) \
		--input $< \
		--output 新闻报道/$(HISTORICAL).md \
		--description \
		--config 新闻报道/index_config.yml

generate_recent: $(RECENT:%=新闻报道/%.md)

新闻报道/%.md: $(JSON_DIR)/%.json
	@mkdir -p 新闻报道
	python $(MARKDOWN_SCRIPT) \
		--input $< \
		--output 新闻报道/$*.md \
		--description \
		--config 新闻报道/index_config.yml

readme: readme_with_desc readme_without_desc

新闻报道/README.md:
	python $(README_SCRIPT) 新闻报道

.PHONY: all fetch generate readme fetch_historical fetch_recent generate_historical generate_recent readme_with_desc readme_without_desc

clean:
	rm -rf 新闻报道/*.md $(JSON_DIR)