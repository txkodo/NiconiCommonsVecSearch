#!/usr/bin/env python3
"""
サーバー起動時のウォームアップスクリプト
CLAPモデルを事前にロードしてコールドスタート問題を軽減
"""

import asyncio
import logging
import time
from vector_processor import get_vector_processor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def warmup_model():
    """モデルウォームアップ処理"""
    try:
        logger.info("🔥 Starting model warmup...")
        start_time = time.time()
        
        # VectorProcessorを取得・初期化
        processor = get_vector_processor()
        
        # テストベクトル化でモデルをウォームアップ
        test_result = processor.vectorize_keyword("test warmup")
        
        warmup_time = time.time() - start_time
        logger.info(f"✅ Model warmup completed in {warmup_time:.2f}s")
        logger.info(f"   Test vector dimension: {test_result['dimension']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Model warmup failed: {e}")
        return False


if __name__ == "__main__":
    # 同期実行
    import sys
    
    logger.info("Starting CLAP model warmup process...")
    success = asyncio.run(warmup_model())
    
    if success:
        logger.info("🎉 Warmup completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Warmup failed!")
        sys.exit(1)