#!/bin/bash
set -e

# ニコニ・コモンズベクトル検索システム セットアップスクリプト

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
    echo -e "${BLUE}[SETUP]${NC} $1"
}

# 必要なツールのチェック
check_dependencies() {
    log "必要なツールをチェックしています..."
    
    # Node.js
    if ! command -v node &> /dev/null; then
        error "Node.js がインストールされていません。https://nodejs.org からインストールしてください"
    fi
    
    local node_version=$(node --version | sed 's/v//')
    local required_version="18.0.0"
    if ! printf '%s\n%s' "$required_version" "$node_version" | sort -V -C; then
        error "Node.js v18以上が必要です。現在のバージョン: v$node_version"
    fi
    
    # Python
    if ! command -v python3 &> /dev/null; then
        error "Python3 がインストールされていません"
    fi
    
    local python_version=$(python3 --version | awk '{print $2}')
    local required_python="3.11.0"
    if ! printf '%s\n%s' "$required_python" "$python_version" | sort -V -C; then
        error "Python 3.11以上が必要です。現在のバージョン: $python_version"
    fi
    
    # Git
    if ! command -v git &> /dev/null; then
        error "Git がインストールされていません"
    fi
    
    log "すべての必要なツールが揃っています"
}

# CLI ツールのインストール
install_cli_tools() {
    log "CLI ツールをインストールしています..."
    
    # Railway CLI
    if ! command -v railway &> /dev/null; then
        info "Railway CLI をインストールしています..."
        npm install -g @railway/cli
    else
        log "Railway CLI は既にインストールされています"
    fi
    
    # Vercel CLI
    if ! command -v vercel &> /dev/null; then
        info "Vercel CLI をインストールしています..."
        npm install -g vercel
    else
        log "Vercel CLI は既にインストールされています"
    fi
    
    log "CLI ツールのインストールが完了しました"
}

# 環境変数テンプレートの作成
create_env_template() {
    log "環境変数テンプレートを作成しています..."
    
    # バックエンド用
    cat > "${PROJECT_ROOT}/backend/.env.template" << 'EOF'
# Qdrant Cloud 設定
QDRANT_URL=https://your-cluster-url.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key

# アプリケーション設定
ENVIRONMENT=development
PORT=8000

# CORS設定（開発時）
CORS_ORIGINS=http://localhost:5173,https://your-frontend-domain.vercel.app
EOF

    # フロントエンド用
    cat > "${PROJECT_ROOT}/frontend/.env.template" << 'EOF'
# バックエンドAPI URL
VITE_API_URL=http://localhost:8000

# 本番環境では Railway の URL に変更
# VITE_API_URL=https://your-backend-app.railway.app
EOF

    log "環境変数テンプレートを作成しました"
    warn "実際の値を設定するため、.env.template を .env にコピーして編集してください"
}

# プロジェクト依存関係のインストール
install_dependencies() {
    log "プロジェクト依存関係をインストールしています..."
    
    # フロントエンド（存在する場合）
    if [ -f "${PROJECT_ROOT}/frontend/package.json" ]; then
        info "フロントエンド依存関係をインストール中..."
        cd "${PROJECT_ROOT}/frontend"
        npm install
    else
        warn "frontend/package.json が見つかりません。フロントエンドが実装されたら npm install を実行してください"
    fi
    
    # バックエンド（存在する場合）
    if [ -f "${PROJECT_ROOT}/backend/requirements.txt" ]; then
        info "バックエンド依存関係をインストール中..."
        cd "${PROJECT_ROOT}/backend"
        
        # 仮想環境の作成・アクティベート
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        
        log "バックエンド依存関係のインストールが完了しました"
        info "バックエンドを開発する際は: cd backend && source venv/bin/activate"
    else
        warn "backend/requirements.txt が見つかりません。バックエンドが実装されたら依存関係をインストールしてください"
    fi
    
    cd "${PROJECT_ROOT}"
}

# セットアップ完了メッセージ
show_next_steps() {
    echo ""
    log "🎉 セットアップが完了しました！"
    echo ""
    echo "次のステップ:"
    echo ""
    echo "1. Qdrant Cloud アカウントを作成:"
    echo "   https://cloud.qdrant.io"
    echo ""
    echo "2. Railway アカウントを作成・ログイン:"
    echo "   https://railway.app"
    echo "   railway login"
    echo ""
    echo "3. Vercel アカウントを作成・ログイン:"
    echo "   https://vercel.com"
    echo "   vercel login"
    echo ""
    echo "4. 環境変数を設定:"
    echo "   - backend/.env.template を backend/.env にコピーして編集"
    echo "   - frontend/.env.template を frontend/.env にコピーして編集"
    echo ""
    echo "5. デプロイ:"
    echo "   ./infrastructure/scripts/deploy.sh"
    echo ""
    echo "詳細な手順は infrastructure/DEPLOYMENT.md を参照してください"
}

# メイン処理
main() {
    info "ニコニ・コモンズベクトル検索システム セットアップを開始します"
    echo ""
    
    check_dependencies
    install_cli_tools
    create_env_template
    install_dependencies
    show_next_steps
}

# スクリプト実行
main "$@"