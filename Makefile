.DEFAULT_GOAL := help

VENV        := .venv
PYTHON      := $(VENV)/bin/python3
DOCLING     := $(VENV)/bin/docling
OUTPUT_DIR  := output
SCRIPTS_DIR := scripts

.PHONY: help setup extract translate all batch list clean fclean re

help:
	@echo "PDF -> Markdown -> 対訳Markdown パイプライン"
	@echo ""
	@echo "  make setup                   初回セットアップ（依存関係インストール、無料）"
	@echo "  make extract PDF=x.pdf       PDF -> Markdown（Docling、無料・ローカル実行）"
	@echo "  make translate PDF=x.pdf     Markdown -> 対訳Markdown（DeepL無料枠、要APIキー）"
	@echo "  make all PDF=x.pdf           extract + translate をまとめて実行"
	@echo "  make batch DIR=folder        folder内の全PDFに対して make all を実行"
	@echo "  make list                    処理済みモジュール一覧を表示"
	@echo "  make clean MODULE=name       1モジュール分の出力を削除"
	@echo "  make fclean                  仮想環境を削除（やり直したいとき）"
	@echo ""
	@echo "出力は $(OUTPUT_DIR)/<モジュール名>/ 以下にモジュールごとにまとまります。"
	@echo "DeepL APIキー（無料枠で可）は、このディレクトリ直下の .env に DEEPL_API_KEY=... で置いてください。"

setup:
	@if command -v uv >/dev/null 2>&1; then \
		echo "== uv でセットアップ =="; \
		uv sync; \
	else \
		echo "== uv が見つからないので、標準の venv + pip でセットアップ =="; \
		python3 -m venv "$(VENV)"; \
		"$(PYTHON)" -m pip install --upgrade pip; \
		"$(PYTHON)" -m pip install -r requirements.txt; \
	fi
	@echo "setup完了。DeepL無料キーを使う場合は .env に DEEPL_API_KEY=... を書いてください"
	@echo "（https://www.deepl.com/ja/pro-api で無料登録できます。新規登録できない場合はREADMEの「限界」を参照）"

extract:
	@test -n "$(PDF)" || (echo "使い方: make extract PDF=path/to/file.pdf" >&2; exit 1)
	@test -f "$(PDF)" || (echo "error: ファイルが見つかりません: $(PDF)" >&2; exit 1)
	@test -x "$(DOCLING)" || (echo "error: セットアップが未実行です。先に 'make setup' を実行してください" >&2; exit 1)
	@name="$$(basename "$(PDF)" .pdf)"; \
	mkdir -p "$(OUTPUT_DIR)/$$name"; \
	echo "== PDF -> Markdown: $$name =="; \
	$(DOCLING) convert "$(PDF)" --to md --no-ocr --output "$(OUTPUT_DIR)/$$name"

translate:
	@test -n "$(PDF)" || (echo "使い方: make translate PDF=path/to/file.pdf" >&2; exit 1)
	@test -x "$(PYTHON)" || (echo "error: セットアップが未実行です。先に 'make setup' を実行してください" >&2; exit 1)
	@name="$$(basename "$(PDF)" .pdf)"; \
	src="$(OUTPUT_DIR)/$$name/$$name.md"; \
	test -f "$$src" || (echo "error: $$src が見つかりません。先に 'make extract PDF=$(PDF)' を実行してください" >&2; exit 1); \
	echo "== Markdown -> 対訳Markdown: $$name =="; \
	$(PYTHON) "$(SCRIPTS_DIR)/translate_parallel.py" "$$src"

all: extract translate

batch:
	@test -n "$(DIR)" || (echo "使い方: make batch DIR=path/to/pdf-folder" >&2; exit 1)
	@test -d "$(DIR)" || (echo "error: フォルダが見つかりません: $(DIR)" >&2; exit 1)
	@for f in "$(DIR)"/*.pdf; do \
		test -f "$$f" || continue; \
		echo "=== $$f ==="; \
		$(MAKE) --no-print-directory all PDF="$$f" || exit 1; \
	done

list:
	@ls -1 "$(OUTPUT_DIR)" 2>/dev/null || echo "（まだ何も処理されていません）"

clean:
	@test -n "$(MODULE)" || (echo "使い方: make clean MODULE=name" >&2; exit 1)
	rm -rf "$(OUTPUT_DIR)/$(MODULE)"

fclean:
	rm -rf $(VENV)

re: fclean setup
