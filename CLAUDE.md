# 開発フロー

## 標準的な開発手順

1. **mainブランチを最新に更新**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **新しいブランチを作成**
   ```bash
   git checkout -b feature/issue-{issue番号}
   ```

3. **開発作業を実行**
   - 必要なファイルの作成・編集
   - テストの実行
   - リントチェック

4. **変更をコミット**
   ```bash
   git add .
   git commit -m "適切なコミットメッセージ"
   ```

5. **ブランチをプッシュ**
   ```bash
   git push -u origin feature/issue-{issue番号}
   ```

6. **プルリクエストを作成**
   ```bash
   gh pr create --title "タイトル" --body "説明"
   ```

7. **対応したissueを閉じる**
   ```bash
   gh issue close {issue番号} --comment "完了コメント"
   ```

## プロジェクト固有の情報

### ディレクトリ構成
- `frontend/` - Svelte 5フロントエンド
- `backend/` - Pythonバックエンド  
- `tools/` - 開発者用ツール
- `.github/` - GitHub設定・ワークフロー

### 技術スタック
- バックエンド: Python, CLAP, Qdrant
- フロントエンド: Svelte 5
- CI/CD: GitHub Actions
- インフラ: IaC

### 開発時の注意点
- 楽曲の再配信は規約違反のため、ニコニ・コモンズへのリンクのみ提供
- CLAP による音楽ベクトル化処理はリソース集約的
- Qdrant データベースへの接続設定が必要