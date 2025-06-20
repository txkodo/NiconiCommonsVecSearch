"""
NiconiCommonsVecSearch Backend API
キーワードベクトル化機能を提供するFastAPI アプリケーション
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import time
from contextlib import asynccontextmanager

from vector_processor import get_vector_processor, VectorProcessor

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# リクエスト・レスポンスモデル
class VectorizeRequest(BaseModel):
    """ベクトル化リクエストモデル"""
    keyword: str = Field(..., min_length=1, max_length=1000, description="ベクトル化するキーワード")


class BatchVectorizeRequest(BaseModel):
    """バッチベクトル化リクエストモデル"""
    keywords: List[str] = Field(..., min_items=1, max_items=100, description="ベクトル化するキーワードのリスト")


class VectorizeResponse(BaseModel):
    """ベクトル化レスポンスモデル"""
    keyword: str = Field(..., description="元のキーワード")
    vector: List[float] = Field(..., description="ベクトル表現")
    dimension: int = Field(..., description="ベクトルの次元数")
    processing_time: float = Field(..., description="処理時間（秒）")
    model_info: Dict[str, Any] = Field(..., description="モデル情報")


class BatchVectorizeResponse(BaseModel):
    """バッチベクトル化レスポンスモデル"""
    results: List[VectorizeResponse] = Field(..., description="ベクトル化結果のリスト")
    total_count: int = Field(..., description="処理された総数")
    processing_time: float = Field(..., description="総処理時間（秒）")


class HealthResponse(BaseModel):
    """ヘルスチェックレスポンスモデル"""
    status: str = Field(..., description="サービスステータス")
    timestamp: float = Field(..., description="タイムスタンプ")
    model_status: Dict[str, Any] = Field(..., description="モデルステータス")


# アプリケーション初期化
@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理"""
    # 起動時処理
    logger.info("🚀 Starting NiconiCommonsVecSearch Backend API...")
    
    # CLAPモデルの事前初期化でコールドスタート軽減
    try:
        logger.info("🔥 Pre-warming CLAP model to reduce cold start latency...")
        start_time = time.time()
        
        vector_processor = get_vector_processor()
        # 軽量なテストでモデルウォームアップ
        test_result = vector_processor.vectorize_keyword("warmup test")
        
        warmup_time = time.time() - start_time
        logger.info(f"✅ Model pre-warmed successfully in {warmup_time:.2f}s")
        logger.info(f"   Ready to serve requests with ~{test_result['dimension']}D vectors")
        
    except Exception as e:
        logger.warning(f"⚠️  Model pre-warming failed: {e}")
        logger.warning("   First API request will experience cold start delay")
    
    yield
    
    # 終了時処理
    logger.info("🛑 Shutting down NiconiCommonsVecSearch Backend API...")


# FastAPIアプリケーション作成
app = FastAPI(
    title="NiconiCommonsVecSearch API",
    description="ニコニ・コモンズ楽曲検索のためのキーワードベクトル化API",
    version="1.0.0",
    lifespan=lifespan
)

# CORSミドルウェア設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンを設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=Dict[str, str])
async def root():
    """ルートエンドポイント"""
    return {
        "message": "NiconiCommonsVecSearch Backend API",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """ヘルスチェックエンドポイント"""
    try:
        vector_processor = get_vector_processor()
        model_info = vector_processor.get_model_info()
        
        return HealthResponse(
            status="healthy",
            timestamp=time.time(),
            model_status=model_info
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/api/vectorize", response_model=VectorizeResponse)
async def vectorize_keyword(request: VectorizeRequest):
    """
    キーワードをベクトル化するエンドポイント
    
    Args:
        request: ベクトル化リクエスト
        
    Returns:
        ベクトル化結果
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received vectorization request for keyword: {request.keyword}")
        
        # ベクトル化処理
        vector_processor = get_vector_processor()
        result = vector_processor.vectorize_keyword(request.keyword)
        
        processing_time = time.time() - start_time
        
        response = VectorizeResponse(
            keyword=result["keyword"],
            vector=result["vector"],
            dimension=result["dimension"],
            processing_time=processing_time,
            model_info=result["model_info"]
        )
        
        logger.info(f"Successfully vectorized keyword in {processing_time:.3f}s")
        return response
        
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Vectorization failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/vectorize/batch", response_model=BatchVectorizeResponse)
async def vectorize_keywords_batch(request: BatchVectorizeRequest):
    """
    複数のキーワードを一括ベクトル化するエンドポイント
    
    Args:
        request: バッチベクトル化リクエスト
        
    Returns:
        バッチベクトル化結果
    """
    start_time = time.time()
    
    try:
        logger.info(f"Received batch vectorization request for {len(request.keywords)} keywords")
        
        # バッチベクトル化処理
        vector_processor = get_vector_processor()
        results = vector_processor.vectorize_batch(request.keywords)
        
        processing_time = time.time() - start_time
        
        # レスポンス変換
        vectorize_responses = []
        for result in results:
            vectorize_responses.append(VectorizeResponse(
                keyword=result["keyword"],
                vector=result["vector"],
                dimension=result["dimension"],
                processing_time=processing_time / len(results),  # 平均処理時間
                model_info=result["model_info"]
            ))
        
        response = BatchVectorizeResponse(
            results=vectorize_responses,
            total_count=len(vectorize_responses),
            processing_time=processing_time
        )
        
        logger.info(f"Successfully vectorized {len(results)} keywords in {processing_time:.3f}s")
        return response
        
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Batch vectorization failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/model/info", response_model=Dict[str, Any])
async def get_model_info():
    """
    モデル情報を取得するエンドポイント
    
    Returns:
        モデル情報
    """
    try:
        vector_processor = get_vector_processor()
        model_info = vector_processor.get_model_info()
        return model_info
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)