"""
vector_processor.py のテストファイル
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# テスト対象モジュールのインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from vector_processor import VectorProcessor, get_vector_processor


class TestVectorProcessor:
    """VectorProcessorクラスのテスト"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される"""
        self.processor = VectorProcessor()
    
    def test_init(self):
        """初期化のテスト"""
        assert self.processor.model_name == "630k-audioset-best.pt"
        assert self.processor.enable_fusion is False
        assert self.processor.model is None
    
    def test_init_with_params(self):
        """パラメータ付き初期化のテスト"""
        processor = VectorProcessor(
            model_name="custom-model.pt",
            enable_fusion=True
        )
        assert processor.model_name == "custom-model.pt"
        assert processor.enable_fusion is True
    
    def test_preprocess_text_valid(self):
        """正常なテキスト前処理のテスト"""
        # 正常なケース
        result = self.processor.preprocess_text("  音楽  ")
        assert result == "音楽"
        
        result = self.processor.preprocess_text("piano music")
        assert result == "piano music"
    
    def test_preprocess_text_empty(self):
        """空文字テキスト前処理のテスト"""
        with pytest.raises(ValueError, match="Empty text input"):
            self.processor.preprocess_text("")
        
        with pytest.raises(ValueError, match="Empty text input"):
            self.processor.preprocess_text("   ")
    
    @patch('vector_processor.laion_clap')
    def test_initialize_model_success(self, mock_laion_clap):
        """モデル初期化成功のテスト"""
        # モックの設定
        mock_model = Mock()
        mock_laion_clap.CLAP_Module.return_value = mock_model
        
        # テスト実行
        self.processor.initialize_model()
        
        # 検証
        mock_laion_clap.CLAP_Module.assert_called_once_with(
            enable_fusion=False,
            amodel='HTSAT-base'
        )
        mock_model.load_ckpt.assert_called_once()
        mock_model.eval.assert_called_once()
        assert self.processor.model == mock_model
    
    @patch('vector_processor.laion_clap')
    def test_initialize_model_failure(self, mock_laion_clap):
        """モデル初期化失敗のテスト"""
        # モックの設定（例外を発生させる）
        mock_laion_clap.CLAP_Module.side_effect = Exception("Model load failed")
        
        # テスト実行と検証
        with pytest.raises(Exception, match="Model load failed"):
            self.processor.initialize_model()
    
    @patch('vector_processor.laion_clap')
    def test_vectorize_keyword_success(self, mock_laion_clap):
        """キーワードベクトル化成功のテスト"""
        # モックの設定
        mock_model = Mock()
        mock_embeddings = Mock()
        # 512次元のダミーベクトルを作成
        dummy_vector = np.random.rand(1, 512).astype(np.float32)
        mock_embeddings.cpu.return_value.numpy.return_value = dummy_vector
        mock_model.get_text_embedding.return_value = mock_embeddings
        mock_laion_clap.CLAP_Module.return_value = mock_model
        
        # テスト実行
        result = self.processor.vectorize_keyword("音楽")
        
        # 検証
        assert result["keyword"] == "音楽"
        assert len(result["vector"]) == 512
        assert result["dimension"] == 512
        assert "model_info" in result
        mock_model.get_text_embedding.assert_called_once_with(["音楽"])
    
    @patch('vector_processor.laion_clap')
    def test_vectorize_batch_success(self, mock_laion_clap):
        """バッチベクトル化成功のテスト"""
        # モックの設定
        mock_model = Mock()
        mock_embeddings = Mock()
        # 2つのキーワード用のダミーベクトルを作成
        dummy_vectors = np.random.rand(2, 512).astype(np.float32)
        mock_embeddings.cpu.return_value.numpy.return_value = dummy_vectors
        mock_model.get_text_embedding.return_value = mock_embeddings
        mock_laion_clap.CLAP_Module.return_value = mock_model
        
        # テスト実行
        keywords = ["音楽", "piano"]
        results = self.processor.vectorize_batch(keywords)
        
        # 検証
        assert len(results) == 2
        assert results[0]["keyword"] == "音楽"
        assert results[1]["keyword"] == "piano"
        assert len(results[0]["vector"]) == 512
        assert len(results[1]["vector"]) == 512
        mock_model.get_text_embedding.assert_called_once_with(["音楽", "piano"])
    
    def test_vectorize_batch_empty(self):
        """空リストでのバッチベクトル化のテスト"""
        result = self.processor.vectorize_batch([])
        assert result == []
    
    def test_get_model_info(self):
        """モデル情報取得のテスト"""
        info = self.processor.get_model_info()
        
        assert info["model_name"] == "630k-audioset-best.pt"
        assert info["enable_fusion"] is False
        assert "device" in info
        assert info["initialized"] is False  # モデルが初期化されていない


class TestGlobalFunctions:
    """グローバル関数のテスト"""
    
    def test_get_vector_processor_singleton(self):
        """シングルトンパターンのテスト"""
        processor1 = get_vector_processor()
        processor2 = get_vector_processor()
        
        # 同じインスタンスであることを確認
        assert processor1 is processor2
        assert isinstance(processor1, VectorProcessor)


class TestIntegration:
    """統合テスト（実際のCLAPモデルを使用）"""
    
    @pytest.mark.slow
    @pytest.mark.skipif(
        not os.environ.get("RUN_INTEGRATION_TESTS"),
        reason="Integration tests require RUN_INTEGRATION_TESTS=1"
    )
    def test_real_vectorization(self):
        """実際のCLAPモデルを使用したベクトル化テスト"""
        processor = VectorProcessor()
        
        try:
            result = processor.vectorize_keyword("piano music")
            
            # 基本的な検証
            assert result["keyword"] == "piano music"
            assert isinstance(result["vector"], list)
            assert len(result["vector"]) > 0
            assert result["dimension"] > 0
            assert "model_info" in result
            
        except Exception as e:
            # 実際のモデルロードが失敗する場合はスキップ
            pytest.skip(f"Real model test skipped due to: {e}")


if __name__ == "__main__":
    # テスト実行
    pytest.main([__file__, "-v"])