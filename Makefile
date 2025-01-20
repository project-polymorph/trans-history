.PHONY: build clean

build:
	cd docs && python ../scripts/generate_index.py

clean:
	rm -rf docs/新闻报道/*
