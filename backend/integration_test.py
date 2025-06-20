#!/usr/bin/env python3
"""
実際のCLAPモデルを使用した統合テスト
"""

import os
import sys
import time

def test_real_clap_integration():
    """実際のCLAPモデルを使用したベクトル化テスト"""
    print("=== CLAP Integration Test ===")
    
    try:
        # vector_processorをインポート
        from vector_processor import VectorProcessor
        
        print("✓ VectorProcessor imported successfully")
        
        # プロセッサーを初期化
        processor = VectorProcessor()
        print("✓ VectorProcessor initialized")
        
        # テストキーワード
        test_keyword = "piano music"
        print(f"Testing keyword: '{test_keyword}'")
        
        # ベクトル化実行
        start_time = time.time()
        result = processor.vectorize_keyword(test_keyword)
        processing_time = time.time() - start_time
        
        print(f"✓ Vectorization completed in {processing_time:.3f}s")
        print(f"  - Keyword: {result['keyword']}")
        print(f"  - Vector dimension: {result['dimension']}")
        print(f"  - Vector preview: {result['vector'][:5]}...")
        print(f"  - Model info: {result['model_info']}")
        
        # バッチテスト
        batch_keywords = ["guitar", "drums", "violin"]
        print(f"\nTesting batch vectorization: {batch_keywords}")
        
        start_time = time.time()
        batch_results = processor.vectorize_batch(batch_keywords)
        batch_time = time.time() - start_time
        
        print(f"✓ Batch vectorization completed in {batch_time:.3f}s")
        print(f"  - Processed {len(batch_results)} keywords")
        for i, result in enumerate(batch_results):
            print(f"  - {i+1}. {result['keyword']}: {result['dimension']}D vector")
        
        print("\n🎉 All integration tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_real_clap_integration()
    sys.exit(0 if success else 1)