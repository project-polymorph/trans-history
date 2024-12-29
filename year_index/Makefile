HISTORICAL := 1980-1999
RECENT := $(shell seq 2000 2024)
SCRIPT := ../scripts/generate_index.py
README_SCRIPT := ../scripts/generate_readme.py

all: historical recent readme

historical: index_with_desc/historical index_without_desc/historical

index_with_desc/historical:
	@mkdir -p index_with_desc
	python $(SCRIPT) --years $(HISTORICAL) -d --output index_with_desc/$(HISTORICAL).md

index_without_desc/historical:
	@mkdir -p index_without_desc
	python $(SCRIPT) --years $(HISTORICAL) --output index_without_desc/$(HISTORICAL).md

recent: $(RECENT:%=index_with_desc/%) $(RECENT:%=index_without_desc/%)

index_with_desc/%: 
	@mkdir -p index_with_desc
	python $(SCRIPT) --years $* -d --output index_with_desc/$*.md

index_without_desc/%: 
	@mkdir -p index_without_desc
	python $(SCRIPT) --years $* --output index_without_desc/$*.md

readme: readme_with_desc readme_without_desc

readme_with_desc:
	python $(README_SCRIPT) index_with_desc

readme_without_desc:
	python $(README_SCRIPT) index_without_desc

.PHONY: all historical recent readme readme_with_desc readme_without_desc

clean:
	rm -rf index_with_desc
	rm -rf index_without_desc
	rm -f */README.md