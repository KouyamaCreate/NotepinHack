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

## プライベートリポジトリで必要なファイルだけを同期しながら安全に自動実行する方法

### 1. 必要なファイルだけ同期する方針

- download_plaudai_mp3.py
- requirements.txt（必要な場合）

### 2. アップストリームから必要なファイルのみ自動取得するワークフロー例

`.github/workflows/sync_selected_files.yml` を作成し、以下のようにすることで、元リポジトリの`download_plaudai_mp3.py`および`requirements.txt`のみを定期的に取得・上書きできます。

```yaml
name: Sync selected files from upstream

on:
  schedule:
    - cron: '0 3 * * *'   # 毎日午前3時（JST12時）に実行
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout self
        uses: actions/checkout@v3

      - name: Fetch selected files from upstream
        run: |
          git clone --depth=1 https://github.com/original-owner/original-repo.git upstream-tmp
          cp upstream-tmp/download_plaudai_mp3.py ./download_plaudai_mp3.py
          if [ -f upstream-tmp/requirements.txt ]; then cp upstream-tmp/requirements.txt ./requirements.txt; fi

      - name: Commit and push if changed
        run: |
          git config --global user.name 'github-actions[bot]'
          git config --global user.email 'github-actions[bot]@users.noreply.github.com'
          git add download_plaudai_mp3.py requirements.txt || true
          git diff --cached --quiet || git commit -m "Sync selected files from upstream"
          git push origin HEAD:main
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

#### ポイント
- git cloneで一時ディレクトリにupstreamを取得し、必要なファイルのみを上書き
- ファイルが変更されていればcommitしてpush
- 不要なファイルや競合の心配がない

---

## 補足：他者の公開Gitリポジトリを個人・社内用に完全コピー（Fork）したい場合

### 結論（最もシンプルな方法）

**branchも含めて完全コピーしたい場合は、`--mirror`オプション付きでclone→pushするだけでOK**

```sh
git clone --mirror https://github.com/${user-or-org}/${repo-fork-from}.git
git push  --mirror https://github.com/${user-or-org}/${repo-fork-to}.git
```

- これで全てのブランチやタグ、refsも含めて丸ごとコピーされる
- Fork先をプライベートにすれば、個人利用や社内限定利用が可能

### 注意点

- Fork先リポジトリのGitHub Actionsは、Settingsから必ず無効化しておく  
  （Fork元のワークフローファイルが自動で起動してしまう場合があるため）

### 参考

- 通常のGitHubの「Fork」機能はmainブランチのみ・PR履歴付きのコピー
- `--mirror`は全てのブランチ・タグ・refsを完全複製したい場合に推奨

---

この手順により、ブランチ構成や履歴を含めて安全にプライベートリポジトリへコピーし、必要なファイルだけを残して同期・自動実行の運用が可能です。