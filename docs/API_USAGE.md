# NiconiCommonsVecSearch API 使用方法

## 概要

NiconiCommonsVecSearch APIは、キーワードをCLAPモデルでベクトル化するRESTful APIです。テキストキーワードを音楽・音声との類似性を表現する高次元ベクトルに変換します。

## ベースURL

- **開発環境**: `http://localhost:8000`
- **本番環境**: `https://your-railway-app.railway.app`

## 認証

現在のバージョンでは認証は不要です。

## エンドポイント一覧

### 1. ヘルスチェック

APIの稼働状況を確認します。

```http
GET /health
```

**レスポンス例:**
```json
{
  "status": "healthy",
  "timestamp": 1703123456.789,
  "model_status": {
    "model_name": "630k-audioset-best.pt",
    "enable_fusion": false,
    "device": "cpu",
    "initialized": true
  }
}
```

### 2. 単一キーワードのベクトル化

1つのキーワードをベクトル化します。

```http
POST /api/vectorize
```

**リクエストボディ:**
```json
{
  "keyword": "ピアノ音楽"
}
```

**レスポンス例:**
```json
{
  "keyword": "ピアノ音楽",
  "vector": [0.123, -0.456, 0.789, ...],
  "dimension": 512,
  "processing_time": 0.234,
  "model_info": {
    "model_name": "630k-audioset-best.pt",
    "enable_fusion": false,
    "device": "cpu"
  }
}
```

### 3. 複数キーワードの一括ベクトル化

複数のキーワードを一度にベクトル化します（最大100件）。

```http
POST /api/vectorize/batch
```

**リクエストボディ:**
```json
{
  "keywords": ["ピアノ", "ギター", "ドラム", "バイオリン"]
}
```

**レスポンス例:**
```json
{
  "results": [
    {
      "keyword": "ピアノ",
      "vector": [0.123, -0.456, ...],
      "dimension": 512,
      "processing_time": 0.058,
      "model_info": {...}
    },
    ...
  ],
  "total_count": 4,
  "processing_time": 0.234
}
```

### 4. モデル情報取得

使用中のCLAPモデルの情報を取得します。

```http
GET /api/model/info
```

**レスポンス例:**
```json
{
  "model_name": "630k-audioset-best.pt",
  "enable_fusion": false,
  "device": "cpu",
  "initialized": true
}
```

## 使用例

### cURLでの使用例

```bash
# ヘルスチェック
curl -X GET "http://localhost:8000/health"

# 単一キーワードのベクトル化
curl -X POST "http://localhost:8000/api/vectorize" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "jazz piano"}'

# バッチベクトル化
curl -X POST "http://localhost:8000/api/vectorize/batch" \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["jazz", "rock", "classical"]}'
```

### JavaScriptでの使用例

```javascript
// 単一キーワードのベクトル化
async function vectorizeKeyword(keyword) {
  const response = await fetch('http://localhost:8000/api/vectorize', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ keyword }),
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}

// 使用例
vectorizeKeyword('acoustic guitar')
  .then(result => {
    console.log('Keyword:', result.keyword);
    console.log('Vector dimension:', result.dimension);
    console.log('Processing time:', result.processing_time);
  })
  .catch(error => console.error('Error:', error));
```

### Pythonでの使用例

```python
import requests
import json

# APIクライアントクラス
class VectorizeClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def vectorize(self, keyword):
        """単一キーワードのベクトル化"""
        response = requests.post(
            f"{self.base_url}/api/vectorize",
            json={"keyword": keyword}
        )
        response.raise_for_status()
        return response.json()
    
    def vectorize_batch(self, keywords):
        """バッチベクトル化"""
        response = requests.post(
            f"{self.base_url}/api/vectorize/batch",
            json={"keywords": keywords}
        )
        response.raise_for_status()
        return response.json()

# 使用例
client = VectorizeClient()

# 単一キーワード
result = client.vectorize("classical music")
print(f"Vector dimension: {result['dimension']}")

# バッチ処理
batch_result = client.vectorize_batch(["piano", "guitar", "drums"])
print(f"Processed {batch_result['total_count']} keywords")
```

## フロントエンド統合

### React.jsでの統合例

```jsx
import React, { useState } from 'react';

const VectorizeComponent = () => {
  const [keyword, setKeyword] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleVectorize = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/vectorize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keyword }),
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="text"
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        placeholder="キーワードを入力"
      />
      <button onClick={handleVectorize} disabled={loading}>
        {loading ? 'Processing...' : 'ベクトル化'}
      </button>
      
      {result && (
        <div>
          <h3>結果</h3>
          <p>キーワード: {result.keyword}</p>
          <p>ベクトル次元: {result.dimension}</p>
          <p>処理時間: {result.processing_time}秒</p>
        </div>
      )}
    </div>
  );
};

export default VectorizeComponent;
```

### Vue.jsでの統合例

```vue
<template>
  <div>
    <input
      v-model="keyword"
      placeholder="キーワードを入力"
      @keyup.enter="vectorize"
    />
    <button @click="vectorize" :disabled="loading">
      {{ loading ? 'Processing...' : 'ベクトル化' }}
    </button>
    
    <div v-if="result">
      <h3>結果</h3>
      <p>キーワード: {{ result.keyword }}</p>
      <p>ベクトル次元: {{ result.dimension }}</p>
      <p>処理時間: {{ result.processing_time }}秒</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      keyword: '',
      result: null,
      loading: false,
    };
  },
  methods: {
    async vectorize() {
      this.loading = true;
      try {
        const response = await fetch('/api/vectorize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ keyword: this.keyword }),
        });
        
        this.result = await response.json();
      } catch (error) {
        console.error('Error:', error);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
```

## エラーハンドリング

### HTTPステータスコード

- `200`: 成功
- `400`: 不正なリクエスト（空のキーワードなど）
- `500`: サーバー内部エラー
- `503`: サービス利用不可（モデル初期化失敗など）

### エラーレスポンス例

```json
{
  "detail": "Empty text input"
}
```

## 制限事項

- キーワードの最大長: 1000文字
- バッチ処理の最大件数: 100件
- レート制限: 現在は未実装（将来的に追加予定）

## パフォーマンス

### コールドスタート問題
- **初回起動時**: CLAPモデルのダウンロード・ロードのため1-2分かかる場合があります
- **サーバーレス環境**: アイドル時間後の再起動で同様の遅延が発生する可能性があります

### 通常時のパフォーマンス
- **ウォームアップ後**: 100-500ms程度
- **バッチ処理**: 単一処理より効率的
- **2回目以降のリクエスト**: モデルがメモリに常駐するため高速

### 改善策
- サーバー起動時に自動ウォームアップを実行
- 本番環境では常時稼働またはkeep-alive設定を推奨
- 初回リクエスト時のタイムアウト設定を十分に長く設定

### Railway Free プランでの対策
1. **GitHub Actions**: 定期的なpingで自動keep-alive（無料）
2. **UptimeRobot**: 外部監視サービスで5分間隔ping（無料プランあり）
3. **Cron-job.org**: 定期実行サービス（無料）
4. **自前スクリプト**: VPS等から定期ping実行

```bash
# 簡単なcurlスクリプト例（crontabで定期実行）
*/10 * * * * curl -s https://your-app.railway.app/health > /dev/null
```

## 自動生成API仕様書

FastAPIの自動生成機能により、インタラクティブなAPI仕様書が利用できます：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## サポート

- GitHub Issues: [プロジェクトのIssuesページ](https://github.com/txkodo/NiconiCommonsVecSearch/issues)
- 実装に関する質問や不具合報告をお待ちしています