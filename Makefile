.PHONY: build clean

build:
	make docs/新闻报道
	make docs/学术研究与调查报告
	make docs/政策法规
	make docs/综合索引

docs/新闻报道:
	mkdir -p docs/新闻报道
	cd docs && python ../scripts/generate_index.py --config news_query.json --state .news_index_state.json

docs/学术研究与调查报告:
	mkdir -p docs/学术研究与调查报告
	cd docs && python ../scripts/generate_index.py --config paper_query.json --state .paper_index_state.json	

docs/政策法规:
	cp -R templates/政策法规 docs/政策法规
	cd docs && python ../scripts/generate_index.py --config policy_query.json --state .policy_index_state.json

docs/综合索引:
	mkdir -p docs/综合索引
	cd docs && python ../scripts/generate_index.py --config total_query.json --state .total_index_state.json

clean:
	rm -rf docs/新闻报道
	rm -rf docs/学术研究与调查报告
	rm -rf docs/政策法规
	rm -f docs/.news_index_state.json
	rm -f docs/.paper_index_state.json
	rm -f docs/.policy_index_state.json
	rm -f docs/.total_index_state.json
