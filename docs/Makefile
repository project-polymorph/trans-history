HISTORICAL := 1980-1999
RECENT := $(shell seq 2000 2024)
SCRIPT := ../scripts/generate_index.py
README_SCRIPT := ../scripts/generate_readme.py

all: historical recent 新闻报道/README.md

historical: 新闻报道/historical 

新闻报道/historical:
	@mkdir -p 新闻报道
	python $(SCRIPT) --years $(HISTORICAL) -d --output 新闻报道/$(HISTORICAL).md --config 新闻报道/index_config.yml

recent: $(RECENT:%=新闻报道/%) $(RECENT:%=index_without_desc/%)

新闻报道/%: 
	@mkdir -p 新闻报道
	python $(SCRIPT) --years $* -d --output 新闻报道/$*.md --config 新闻报道/index_config.yml

readme: readme_with_desc readme_without_desc

新闻报道/README.md:
	python $(README_SCRIPT) 新闻报道

.PHONY: all historical recent readme readme_with_desc readme_without_desc

clean:
	rm -rf 新闻报道/*.md