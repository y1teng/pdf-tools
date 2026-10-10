# pdf-tools

42の課題PDF（英語）を、対訳（英語＋日本語）Markdownの下訳にする、無料で完結するパイプライン。

```
PDF --[Docling（ローカル・無料）]--> Markdown --[DeepL（無料枠）]--> 対訳Markdown
```

- **Docling**: テキスト・見出し・表・図をPDFから抽出し、構造化されたMarkdownにする（ローカル実行、APIキー不要）
- **DeepL API（無料枠）**: 抽出したMarkdownを1行ずつ日本語に翻訳し、英語原文の下に挿入する

出来上がるのは**下訳**です。見出しの構造や注意書き・警告などの体裁は手直しが必要になることがあります（詳しくは[限界](#限界)を参照）。

## 必要なもの

- Python 3.12以上
- [uv](https://docs.astral.sh/uv/)（`pip install uv` または各OSのインストーラで導入）
- DeepLの無料APIキー（[deepl.com/ja/pro-api](https://www.deepl.com/ja/pro-api) で無料登録。月50万文字まで無料）
  - ⚠️ **注意**: DeepL公式のプランページによると、「DeepL API Free」プランは現在**新規登録を停止している**可能性があります（2026-10-10時点、未確認情報含む）。既存のFreeキーを持っている人は引き続き使えるようですが、これから新しく登録しようとすると選べない場合があります。登録ページで実際にFreeプランが選べるか確認してください。選べない場合は[限界](#限界)を参照してください。

## セットアップ

```bash
git clone https://github.com/y1teng/pdf-tools.git
cd pdf-tools
make setup
```

`make setup` は初回に `docling` 一式（レイアウト認識モデルなど）をダウンロードします。回線にもよりますが数分かかることがあります。

次に、このディレクトリ直下に `.env` ファイルを作り、DeepLの無料APIキーを書いてください。

```bash
echo "DEEPL_API_KEY=ここに自分のキー" > .env
```

（DeepLキーを用意しない場合でも `make extract` だけなら動きます。翻訳なしのMarkdown下訳だけで良い人はそれでも十分です。）

## 使い方

```bash
make extract PDF=path/to/課題.pdf     # PDF -> Markdown（無料・ローカル）
make translate PDF=path/to/課題.pdf   # Markdown -> 対訳Markdown（DeepL無料枠）
make all PDF=path/to/課題.pdf         # 上の2つをまとめて実行
make batch DIR=path/to/フォルダ       # フォルダ内の全PDFに make all を実行
make list                             # 処理済みモジュール一覧
make clean MODULE=名前                # 1モジュール分の出力を削除
make fclean                           # 仮想環境を削除してやり直す
```

出力は `output/<モジュール名>/` 以下にまとまります。

```
output/
  Python Module 05 bis/
    Python Module 05 bis.md          # Doclingの生成物
    Python Module 05 bis (対訳).md    # DeepL翻訳済みの下訳
```

`output/`はこのリポジトリには含まれません（課題文そのものの再配布になるため、`.gitignore`で除外しています）。手元に生成されるだけです。

## 限界

- **DeepLの無料キーが新規に作れない場合**: その場合は `make translate` の代わりに `make extract` だけを使い、出てきたMarkdown（英語のみ）を手元でClaude等のAIに「対訳にして」と頼むか、自分で訳してください。パイプラインの前半（PDF→Markdown）はDeepLキーが無くても無料のまま動きます。
- **OCRは既定でオフ**（`--no-ocr`）です。42の課題PDFは普通テキスト埋め込みで作られているため不要な上、OCRモデルのダウンロードが海外CDN経由で失敗することがあったためです。スキャン画像ベースのPDFを扱いたい場合はMakefileの`extract`から`--no-ocr`を外してください。
- DeepLは1行ずつ機械的に訳すだけなので、`[!TIP]` `[!NOTE]` `[!WARNING]` のような注意書きの種類分けや、章の区切り、用語の統一（既存の対訳ファイルとの訳語の揃え）まではやってくれません。そこは自分で直すか、Claude CodeのようなAIに仕上げを頼むのがおすすめです。
- Doclingの構造抽出はきれいですが、ターミナル出力のような等幅フォントの文字列（特にアンダースコア `_` を含むもの）を稀に誤認識することがあります。コマンド例の文字が怪しいと思ったら、`pdftotext -layout`で元のPDFと見比べてください。
