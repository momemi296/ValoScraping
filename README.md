# ValoScraping
thespike.ggからスクレイピングを行うプログラムです。

## 環境構築
1. スクレイピングのために、seleniumをインストールしてください。
```
pip install selenium
```
2. windowsの場合、chromedriver.exeを実行するプログラムと同じディレクトリに配置してください。
以下のURLからダウンロードできます。
https://developer.chrome.com/docs/chromedriver/downloads?hl=ja

## 使い方
1. event_url_getter.pyを実行します。このプログラムは過去のイベントの結果が載っているページのURLを取得することができます。
2. event_url_chooser.pyを実行します。特定のイベントのみを取得することができます。
3. match_url_getter.pyを実行します。イベントで行われた試合(match)のurlを取得します。
4. match_result_getter.pyを実行します。試合結果をjsonl形式で取得します。

取得したURLや試合結果などは、output_filesディレクトリ以下に出力されます。