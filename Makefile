.PHONY: build clean

docs/新闻报道:
	mkdir -p docs/新闻报道
	cd docs && python ../scripts/generate_index.py --config news_query.json --state .news_index_state.json

clean:
	rm -rf docs/新闻报道
