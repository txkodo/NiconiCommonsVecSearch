# デプロイメントガイド

ニコニ・コモンズベクトル検索システムのデプロイ手順書

## 構成概要

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Vercel      │    │    Railway      │    │  Qdrant Cloud   │
│   (Frontend)    │────│  (Backend API)  │────│  (Free Tier)    │
│   Svelte 5      │    │    Python       │    │  Vector DB      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 前提条件

### 必要なアカウント
- [GitHub](https://github.com) アカウント
- [Railway](https://railway.app) アカウント
- [Vercel](https://vercel.com) アカウント  
- [Qdrant Cloud](https://cloud.qdrant.io) アカウント

### 必要なツール
- Node.js 18以上
- Python 3.11以上
- Git
- Railway CLI
- Vercel CLI

```bash
# CLIツールのインストール
npm install -g @railway/cli
npm install -g vercel
```

## セットアップ手順

### 1. リポジトリのクローン・セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/txkodo/NiconiCommonsVecSearch.git
cd NiconiCommonsVecSearch

# セットアップスクリプトを実行（作成予定）
./infrastructure/scripts/setup.sh
```

### 2. Qdrant Cloudの設定

1. [Qdrant Cloud](https://cloud.qdrant.io) にログイン
2. 新しいクラスター作成（Free Tierを選択）
3. API KeyとCluster URLを取得
4. 環境変数として保存

### 3. Railwayの設定

```bash
# Railwayにログイン
railway login

# プロジェクト作成
railway init

# 環境変数設定
railway variables set QDRANT_URL="your-qdrant-url"
railway variables set QDRANT_API_KEY="your-api-key"
railway variables set ENVIRONMENT="production"
```

### 4. Vercelの設定

```bash
# Vercelにログイン
vercel login

# プロジェクト作成・設定
vercel

# 環境変数設定
vercel env add VITE_API_URL
# Railwayのバックエンドエンドポイントを入力
```

## デプロイ手順

### 自動デプロイ（推奨）

```bash
# 全体デプロイスクリプト実行
./infrastructure/scripts/deploy.sh
```

### 手動デプロイ

#### バックエンド（Railway）

```bash
# バックエンドディレクトリに移動
cd backend

# Railwayにデプロイ
railway up
```

#### フロントエンド（Vercel）

```bash
# フロントエンドディレクトリに移動
cd frontend

# 依存関係インストール
npm install

# Vercelにデプロイ
vercel --prod
```

## CI/CD設定

GitHub Actionsを使用した自動デプロイ設定

### 必要なシークレット設定

GitHub リポジトリの Settings > Secrets で以下を設定：

```
RAILWAY_TOKEN          # Railway API Token
VERCEL_TOKEN          # Vercel API Token
VERCEL_ORG_ID         # Vercel Organization ID
VERCEL_PROJECT_ID     # Vercel Project ID
QDRANT_URL            # Qdrant Cluster URL
QDRANT_API_KEY        # Qdrant API Key
```

### 自動デプロイトリガー

- `main` ブランチへのプッシュ
- 手動実行（workflow_dispatch）

## 環境変数一覧

### バックエンド（Railway）
```
QDRANT_URL            # Qdrant Cloud Cluster URL
QDRANT_API_KEY        # Qdrant Cloud API Key
ENVIRONMENT           # production/development
PORT                  # 8000（Railwayが自動設定）
```

### フロントエンド（Vercel）
```
VITE_API_URL          # バックエンドAPIのURL
```

## トラブルシューティング

### よくある問題

1. **Railway デプロイエラー**
   - Dockerfileの構文確認
   - 環境変数の設定確認
   - ログの確認: `railway logs`

2. **Vercel ビルドエラー**
   - Node.js バージョン確認
   - 依存関係の確認: `npm install`
   - 環境変数の設定確認

3. **Qdrant 接続エラー**
   - API Key・URL の確認
   - ネットワーク接続の確認
   - Qdrant Cloud ダッシュボードでクラスター状態確認

### ログ確認方法

```bash
# Railway ログ
railway logs

# Vercel デプロイログ
vercel logs [deployment-url]

# ローカル開発
# バックエンド
cd backend && python -m uvicorn main:app --reload

# フロントエンド  
cd frontend && npm run dev
```

## 料金・制限事項

### 無料プラン制限
- **Railway**: 500時間/月、共有CPU、512MB RAM
- **Vercel**: 100GB帯域幅/月、Function実行時間10秒
- **Qdrant Cloud**: 1GB ストレージ、1万ベクトル

### スケーリング時の考慮点
- 制限を超える場合は有料プランへの移行を検討
- バックエンドの負荷分散が必要な場合は複数Railway deployments
- 大量データの場合はQdrant Self-hosted への移行

## 次のステップ

1. モニタリング・ログ設定の改善
2. バックアップ・復旧手順の整備
3. パフォーマンス最適化
4. セキュリティ強化（CORS、レート制限など）