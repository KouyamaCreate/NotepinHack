# クラウド上でdownload_plaudai_mp3.pyを無料・簡単に常時実行する手段案

## 1. GitHub Actionsを使った定期実行

### 概要
- GitHubリポジトリにdownload_plaudai_mp3.pyとrequirements.txtをアップロード
- plaudai_tokenstr.txtはGitHub Secretsとして登録
- `.github/workflows/`にYAMLワークフローを配置
- 例：15分ごと等のスケジュールで自動実行
- ダウンロードしたファイルはArtifactsとして取得可能
- 永続保存や外部ストレージ転送も拡張で対応可能

### 手順

1. **リポジトリにファイルを配置**
   - download_plaudai_mp3.py
   - requirements.txt（必要な場合）

2. **GitHub Secretsにplaudai_tokenstr.txtの内容を登録**
   - Settings > Secrets and variables > Actions > New repository secret
   - Name: `PLAUDAI_TOKENSTR`
   - Value: plaudai_tokenstr.txtの中身

3. **ワークフローファイル例（.github/workflows/plaudai_mp3.yml）**

   ```yaml
   name: Download PlaudAI MP3

   on:
     schedule:
       - cron: '*/15 * * * *'  # 15分ごとに実行
     workflow_dispatch:

   jobs:
     run-script:
       runs-on: ubuntu-latest
       steps:
         - name: Checkout repository
           uses: actions/checkout@v3

         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.10'

         - name: Install dependencies
           run: |
             pip install -r requirements.txt

         - name: Set up token
           run: echo "${{ secrets.PLAUDAI_TOKENSTR }}" > plaudai_tokenstr.txt

         - name: Run script
           run: python download_plaudai_mp3.py

         - name: Upload downloads as artifact
           uses: actions/upload-artifact@v3
           with:
             name: plaud_downloads
             path: plaud_downloads/
   ```

4. **Artifactsからダウンロードファイルを取得**
   - Actionsの実行履歴 > Run details > Artifactsから取得

5. **外部ストレージへ保存したい場合**
   - Google Drive, Dropbox, S3等のAPIトークンをSecretsに登録し、スクリプトでアップロード処理を追加

### メリット・デメリット

- ✅ 無料枠で十分
- ✅ セットアップが簡単
- ✅ 定期実行が柔軟
- ❌ 完全な常時実行（リアルタイム監視）は不可
- ❌ Artifactsの保存期間は90日（永続保存には外部ストレージ推奨）

---

## 2. その他の選択肢（簡易まとめ）

| 手段                | 無料枠 | 常時実行 | 難易度   | 備考                                       |
|---------------------|--------|----------|----------|---------------------------------------------|
| Google Colab        | ◯      | ×        | 易しい   | 最大12時間で切断。自動再開不可             |
| Render/Railway/Replit| △      | △        | 普通     | スリープや制限あり、Python常駐はやや複雑   |
| PythonAnywhere      | ◯      | ×        | 易しい   | 無料枠はWebアプリのみ、常時実行不可        |
| Fly.io              | ◯      | △        | 普通     | Docker化必須、無料枠で制限有                |

---

## 結論

GitHub Actionsによる定期実行＋Artifacts保存が、無料・簡単・確実な手段です。  
外部ストレージ連携も容易に追加できます。