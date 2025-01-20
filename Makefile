.PHONY: build clean

docs/新闻报道:
	mkdir -p docs/新闻报道
	cd docs && python ../scripts/generate_index.py --config news_query.json --state .news_index_state.json

docs/学术研究:
	mkdir -p docs/学术研究
	cd docs && python ../scripts/generate_index.py --config paper_query.json --state .paper_index_state.json	

clean:
	rm -rf docs/新闻报道
	rm -rf docs/学术研究