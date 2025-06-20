# ニコニ・コモンズ楽曲ベクトル検索システム

## プロジェクト概要

ニコニ・コモンズのBGM検索を改善するシステム。楽曲をCLAPでベクトル化し、類似楽曲検索やジャンル・雰囲気による検索を可能にする。

## システム構成

### バックエンド (Python)
1. **キーワードベクトル化機能**
   - キーワードをCLAPでベクトル変換
   - Python実行環境が必要

2. **ベクトル検索機能**
   - Qdrant APIを使用したベクトルデータベース検索
   - ベクトルとフラグを入力として類似楽曲を検索

3. **楽曲ベクトル化・更新機能**
   - 指定されたニコニ・コモンズ楽曲をCLAPでベクトル化
   - データベースを更新

4. **自動スクレイピング機能**
   - 毎日ニコニ・コモンズをスクレイピング
   - 新規楽曲を自動的にベクトル化・データベース更新
   - GitHub Actionsで実行

### フロントエンド (Svelte 5)
- キーワード入力による類似楽曲検索
- 検索結果表示項目：
  - タイトル
  - 再生時間
  - ニコニ・コモンズURL（楽曲再配信は規約違反のためリンクのみ）

### 開発者用ツール
- ニコニ・コモンズの全楽曲（ID 1〜最新）を一括でベクトル化・データベース更新

## ディレクトリ構成
```
/
├── frontend/    # Svelte 5フロントエンド
├── backend/     # Pythonバックエンド
└── tools/       # 開発者用ツール
```

## デプロイ
IaC（Infrastructure as Code）を使用してデプロイ

## 技術スタック
- バックエンド: Python, CLAP, Qdrant
- フロントエンド: Svelte 5
- CI/CD: GitHub Actions
- インフラ: IaC