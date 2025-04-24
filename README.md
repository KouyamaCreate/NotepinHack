# NotepinHack - Plaud.ai 録音データ自動ダウンロードシステム

## 概要

Plaud.aiの録音データを自動でダウンロードするPythonスクリプト群です。  
Googleログイン済みのChrome環境から認証トークン（tokenstr）を取得し、そのトークンを使ってAPI経由で録音データを取得・保存します。

---

## セットアップ・利用手順

### 1. 事前準備：ChromeでGoogleログイン

- 普段使っているChromeブラウザで、Plaud.aiにGoogleログインしておいてください。

### 2. Chromeのユーザディレクトリ・プロファイルディレクトリの取得

- Chromeのユーザデータディレクトリとプロファイルディレクトリを特定します。
    - 例（Macの場合）:  
      - ユーザデータディレクトリ:  
        `/Users/あなたのユーザー名/Library/Application Support/Google/Chrome`
      - プロファイルディレクトリ（通常は "Default" や "Profile 1" など）:  
        `Default` または `Profile 1` など

- 上記2つを`.env`ファイルに記載してください。  
  例:
  ```
  CHROME_USER_DATA_DIR=/Users/あなたのユーザー名/Library/Application Support/Google/Chrome
  CHROME_PROFILE_DIRECTORY=Default
  ```

### 3. 認証トークンの取得

- ターミナルで以下を実行し、Googleログイン済みのChromeプロファイルでPlaud.aiのtokenstrを取得します。
  ```
  python save_plaudai_cookies.py
  ```
  - 指示通りに手動でログイン操作を行い、完了後にEnterキーを押してください。
  - `plaudai_tokenstr.txt` が生成されます。

### 4. 録音データのダウンロード

- 普段の利用時は以下のスクリプトを実行してください。
  ```
  python download_plaudai_mp3.py
  ```
  - 本日分の録音データが `plaud_downloads/` ディレクトリに自動保存されます。

---

## 注意事項

- `.env`, `plaudai_tokenstr.txt` は機密情報を含むため、**絶対に公開リポジトリに含めないでください**（`.gitignore`で除外済み）。
- Chromeのユーザデータディレクトリ・プロファイルディレクトリはご自身の環境に合わせて正しく設定してください。
- Python 3.8以上、selenium, dotenv, requestsパッケージが必要です。  
  必要な場合は以下でインストールしてください:
  ```
  pip install selenium python-dotenv requests
  ```

---

## ファイル説明

- `save_plaudai_cookies.py` : tokenstr取得用スクリプト（cookieは保存しません）
- `download_plaudai_mp3.py` : 録音データのダウンロードスクリプト
- `.env` : Chromeプロファイル情報を記載
- `plaudai_tokenstr.txt` : 認証トークン（自動生成）
- `plaud_downloads/` : ダウンロード先ディレクトリ

---

## トラブルシュート

- tokenstrが取得できない場合、Chromeプロファイル指定やログイン状態を再確認してください。
- Plaud.aiの仕様変更等により動作しなくなる場合があります。