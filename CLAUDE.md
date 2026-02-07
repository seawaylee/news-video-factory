# CLAUDE.md - News Video Factory

## Build & Setup
- build: pip install -r requirements.txt
- install: pip install -r requirements.txt

## Run Commands
- generate: python3 main.py -t "{topic}"
- generate-skip: python3 main.py -t "{topic}" --skip-research
- clean: rm -rf "results/{topic}"

## Usage Examples
- Generate a video about DeepSeek: `CLAUDE generate -t "DeepSeek发布R1"`
- Generate without search (LLM only): `CLAUDE generate-skip -t "美股科技暴涨"`
- Clean up old results: `CLAUDE clean -t "美股科技暴涨"`
