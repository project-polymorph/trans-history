YEARS := $(shell seq 1999 2024)
SCRIPT := ../scripts/generate_index.py

all: $(YEARS:%=index_with_desc/%) $(YEARS:%=index_without_desc/%)

index_with_desc/%: 
	@mkdir -p index_with_desc
	python $(SCRIPT) --year $* -d --output index_with_desc/$*.md

index_without_desc/%: 
	@mkdir -p index_without_desc
	python $(SCRIPT) --year $* --output index_without_desc/$*.md

.PHONY: all
