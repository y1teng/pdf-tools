# pdf-tools

42の課題PDF（英語）を、対訳（英語＋日本語）Markdownの下訳にする、無料で完結するパイプライン。

```
PDF --[Docling（ローカル・無料）]--> Markdown --[DeepL（無料枠）]--> 対訳Markdown
```

- **Docling**: テキスト・見出し・表・図をPDFから抽出し、構造化されたMarkdownにする（ローカル実行、APIキー不要）
- **DeepL API（無料枠）**: 抽出したMarkdownを1行ずつ日本語に翻訳し、英語原文の下に挿入する

出来上がるのは**下訳**です。見出しの構造や注意書き・警告などの体裁は手直しが必要になることがあります（詳しくは[限界](#限界)を参照）。

## 必要なもの

- 空き容量 **約2GB**（`docling`がPyTorchなどの機械学習ライブラリに依存するため。GPU版を避けCPU版を使うよう設定済みですが、それでもこのくらいは必要です。42の校舎PCなど容量が厳しい環境では、`df -h ~` で空きを確認してから`make setup`してください）
- Python 3.12以上
- （あれば）[uv](https://docs.astral.sh/uv/) — `make setup`は`uv`があれば自動で使い、無ければ標準の`venv`+`pip`にフォールバックします。42の校舎PCなどで`uv`が入っていなくても、そのまま`make setup`を実行すればOKです
- DeepLの無料APIキー（[deepl.com/ja/pro-api](https://www.deepl.com/ja/pro-api) で無料登録。月50万文字まで無料）
  - ⚠️ **注意**: DeepL公式のプランページによると、「DeepL API Free」プランは現在**新規登録を停止している**可能性があります（2026-10-10時点、未確認情報含む）。既存のFreeキーを持っている人は引き続き使えるようですが、これから新しく登録しようとすると選べない場合があります。登録ページで実際にFreeプランが選べるか確認してください。選べない場合は[限界](#限界)を参照してください。

## 使い方（はじめての人向け）

例として、42のintraから `libft.pdf` をダウンロードして `~/Downloads/libft.pdf` に置いた、という想定で進めます。

**1. このリポジトリをクローンする**

```bash
git clone https://github.com/y1teng/pdf-tools.git
cd pdf-tools
```

**2. セットアップする**

```bash
make setup
```

初回は `docling` 一式（レイアウト認識モデルなど）をダウンロードするので、回線にもよりますが数分かかります。空き容量は2GBほど必要です（足りない場合は[限界](#限界)を参照）。

**3. DeepLの無料APIキーを `.env` に書く**

[deepl.com/ja/pro-api](https://www.deepl.com/ja/pro-api) で無料登録してキーを取得し（新規登録できない場合は[限界](#限界)を参照）、このディレクトリ直下に `.env` を作ります。

```bash
echo "DEEPL_API_KEY=ここに自分のキー" > .env
```

**4. PDFを指定して実行する**

ダウンロードした `libft.pdf` をそのまま指定します。移動は不要です。

```bash
make all PDF=$HOME/Downloads/libft.pdf
```

⚠️ `PDF=~/Downloads/...` のように `~`（チルダ）を使うと、展開されずそのままの文字列として渡ってしまい `ファイルが見つかりません` エラーになります。`$HOME` か、フルパスを使ってください。

**5. 出来上がったファイルを見る**

```
output/
  libft/
    libft.md          # Doclingが作ったMarkdown（英語のみ）
    libft (対訳).md    # DeepLが訳した英日対訳Markdown
```

`output/libft/libft (対訳).md` を開けば、英語の下に日本語訳が並んだMarkdownになっています。これはまだ**下訳**なので、見出しの体裁や注意書きの種類分けなどは手直しが必要なことがあります（詳しくは[限界](#限界)を参照）。

`output/`はこのリポジトリには含まれません（課題文そのものの再配布になるため、`.gitignore`で除外しています）。手元に生成されるだけです。

### その他のコマンド

他の課題PDFも同じ流れで `make all PDF=...` するだけですが、以下のコマンドも用意してあります。

```bash
make extract PDF=x.pdf     # 翻訳せず、PDF -> Markdownだけ行う
make translate PDF=x.pdf   # すでにextract済みのものだけ翻訳する
make batch DIR=folder      # folder内の全PDFに make all を実行
make list                  # 処理済みモジュール一覧
make clean MODULE=libft    # 1モジュール分の出力を削除
make fclean                # 仮想環境を削除してやり直す
```

## 限界

- **"No space left on device" で `make setup` が失敗する場合**: 容量が足りていません。まず `rm -rf .venv` して中途半端に入ったものを消し、`df -h ~` で空きを確認してください（目安として2GB以上）。
  - 42の校舎PCの場合、`/sgoinfre/$USER` または `/goinfre/$USER` が存在すれば、Doclingのモデルキャッシュ（数GB）を自動的にそちらへ逃がすようMakefileが作られています（`HF_HOME`を自動設定）。手動で何かする必要はありません。それでも足りない場合は、このリポジトリ自体を `/sgoinfre`（席をまたいで使える）や `/goinfre`（その席だけ）に置いて作業してみてください。
- **DeepLの無料キーが新規に作れない場合**: その場合は `make translate` の代わりに `make extract` だけを使い、出てきたMarkdown（英語のみ）を手元でClaude等のAIに「対訳にして」と頼むか、自分で訳してください。パイプラインの前半（PDF→Markdown）はDeepLキーが無くても無料のまま動きます。
- **OCRは既定でオフ**（`--no-ocr`）です。42の課題PDFは普通テキスト埋め込みで作られているため不要な上、OCRモデルのダウンロードが海外CDN経由で失敗することがあったためです。スキャン画像ベースのPDFを扱いたい場合はMakefileの`extract`から`--no-ocr`を外してください。
- DeepLは1行ずつ機械的に訳すだけなので、`[!TIP]` `[!NOTE]` `[!WARNING]` のような注意書きの種類分けや、章の区切り、用語の統一（既存の対訳ファイルとの訳語の揃え）まではやってくれません。そこは自分で直すか、Claude CodeのようなAIに仕上げを頼むのがおすすめです。
- Doclingの構造抽出はきれいですが、ターミナル出力のような等幅フォントの文字列（特にアンダースコア `_` を含むもの）を稀に誤認識することがあります。コマンド例の文字が怪しいと思ったら、`pdftotext -layout`で元のPDFと見比べてください。
