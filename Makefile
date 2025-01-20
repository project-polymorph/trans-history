.PHONY: build clean

build:
	make docs/新闻报道
	make docs/学术研究
	make docs/政策法规

docs/新闻报道:
	mkdir -p docs/新闻报道
	cd docs && python ../scripts/generate_index.py --config news_query.json --state .news_index_state.json

docs/学术研究:
	mkdir -p docs/学术研究
	cd docs && python ../scripts/generate_index.py --config paper_query.json --state .paper_index_state.json	

docs/政策法规:
	mkdir -p docs/政策法规
	cd docs && python ../scripts/generate_index.py --config policy_query.json --state .policy_index_state.json

clean:
	rm -rf docs/新闻报道
	rm -rf docs/学术研究
	rm -rf docs/政策法规
