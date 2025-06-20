#!/bin/bash
set -e

# ニコニ・コモンズベクトル検索システム デプロイスクリプト

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

info() {
    echo -e "${BLUE}[DEPLOY]${NC} $1"
}

# 前提条件のチェック
check_prerequisites() {
    log "デプロイ前のチェックを実行しています..."
    
    # Railway CLI
    if ! command -v railway &> /dev/null; then
        error "Railway CLI がインストールされていません。./scripts/setup.sh を実行してください"
    fi
    
    # Vercel CLI
    if ! command -v vercel &> /dev/null; then
        error "Vercel CLI がインストールされていません。./scripts/setup.sh を実行してください"
    fi
    
    # Railway ログイン確認
    if ! railway whoami &> /dev/null; then
        error "Railway にログインしていません。'railway login' を実行してください"
    fi
    
    # Vercel ログイン確認
    if ! vercel whoami &> /dev/null; then
        error "Vercel にログインしていません。'vercel login' を実行してください"
    fi
    
    log "前提条件のチェックが完了しました"
}

# バックエンドのデプロイ（Railway）
deploy_backend() {
    log "バックエンドを Railway にデプロイしています..."
    
    cd "${PROJECT_ROOT}"
    
    # Railway プロジェクトの初期化（必要に応じて）
    if [ ! -f "${PROJECT_ROOT}/.railway/project.json" ]; then
        info "Railway プロジェクトを初期化しています..."
        railway init
    fi
    
    # 環境変数の確認
    info "必要な環境変数が設定されているか確認してください:"
    echo "  - QDRANT_URL"
    echo "  - QDRANT_API_KEY"
    echo "  - ENVIRONMENT"
    
    read -p "環境変数は設定済みですか？ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        info "Railway の環境変数を設定してください:"
        echo "  railway variables set QDRANT_URL=\"your-qdrant-url\""
        echo "  railway variables set QDRANT_API_KEY=\"your-api-key\""
        echo "  railway variables set ENVIRONMENT=\"production\""
        exit 0
    fi
    
    # デプロイ実行
    info "Railway にデプロイ中..."
    railway up
    
    # デプロイされたURLを取得
    BACKEND_URL=$(railway status --json | jq -r '.deployments[0].url' 2>/dev/null || echo "")
    
    if [ -n "$BACKEND_URL" ]; then
        log "バックエンドのデプロイが完了しました: $BACKEND_URL"
        echo "$BACKEND_URL" > "${PROJECT_ROOT}/.railway_url"
    else
        warn "バックエンドURLを自動取得できませんでした。Railway ダッシュボードで確認してください"
    fi
}

# フロントエンドのデプロイ（Vercel）
deploy_frontend() {
    log "フロントエンドを Vercel にデプロイしています..."
    
    cd "${PROJECT_ROOT}/frontend"
    
    # バックエンドURLの設定
    if [ -f "${PROJECT_ROOT}/.railway_url" ]; then
        BACKEND_URL=$(cat "${PROJECT_ROOT}/.railway_url")
        info "バックエンドURL: $BACKEND_URL"
        
        # Vercel環境変数に設定
        vercel env add VITE_API_URL production "$BACKEND_URL" || warn "環境変数の設定をスキップしました（既に設定済みの可能性があります）"
    else
        warn "バックエンドURLが見つかりません。手動で VITE_API_URL を設定してください"
    fi
    
    # 依存関係のインストール
    if [ -f "package.json" ]; then
        info "依存関係をインストール中..."
        npm install
        
        # ビルドテスト
        info "ビルドテストを実行中..."
        npm run build
    else
        error "frontend/package.json が見つかりません。フロントエンドが実装されていません"
    fi
    
    # Vercel にデプロイ
    info "Vercel にデプロイ中..."
    vercel --prod
    
    log "フロントエンドのデプロイが完了しました"
}

# デプロイ結果の表示
show_deployment_info() {
    log "🎉 デプロイが完了しました！"
    echo ""
    
    # Railway URL
    if [ -f "${PROJECT_ROOT}/.railway_url" ]; then
        BACKEND_URL=$(cat "${PROJECT_ROOT}/.railway_url")
        echo "バックエンドAPI: $BACKEND_URL"
    fi
    
    # Vercel URL は vercel コマンドの出力から確認
    echo "フロントエンド: Vercel ダッシュボードで URL を確認してください"
    echo ""
    
    echo "次のステップ:"
    echo "1. 両方のサービスが正常に動作することを確認"
    echo "2. バックエンドの /health エンドポイントをテスト"
    echo "3. フロントエンドからバックエンドAPIへの接続をテスト"
    echo ""
    echo "問題がある場合は infrastructure/DEPLOYMENT.md のトラブルシューティングを参照してください"
}

# ヘルプメッセージ
show_help() {
    echo "使用方法: $0 [オプション]"
    echo ""
    echo "オプション:"
    echo "  --backend-only    バックエンドのみデプロイ"
    echo "  --frontend-only   フロントエンドのみデプロイ"
    echo "  --help           このヘルプを表示"
    echo ""
    echo "例:"
    echo "  $0                    # 全体をデプロイ"
    echo "  $0 --backend-only     # バックエンドのみデプロイ"
    echo "  $0 --frontend-only    # フロントエンドのみデプロイ"
}

# メイン処理
main() {
    case "${1:-}" in
        --help)
            show_help
            exit 0
            ;;
        --backend-only)
            info "バックエンドのみをデプロイします"
            check_prerequisites
            deploy_backend
            ;;
        --frontend-only)
            info "フロントエンドのみをデプロイします"
            check_prerequisites
            deploy_frontend
            ;;
        "")
            info "ニコニ・コモンズベクトル検索システム デプロイを開始します"
            check_prerequisites
            deploy_backend
            deploy_frontend
            show_deployment_info
            ;;
        *)
            error "不明なオプション: $1"
            show_help
            exit 1
            ;;
    esac
}

# スクリプト実行
main "$@"