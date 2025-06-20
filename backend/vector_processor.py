"""
キーワードベクトル化機能
CLAPモデルを使用してテキストキーワードをベクトル表現に変換する
"""

import logging
from typing import List, Optional, Dict, Any
import numpy as np
import torch
import laion_clap
from pathlib import Path

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorProcessor:
    """CLAPを使用したキーワードベクトル化プロセッサー"""
    
    def __init__(self, model_name: str = "630k-audioset-best.pt", enable_fusion: bool = False):
        """
        VectorProcessorを初期化
        
        Args:
            model_name: CLAPモデル名
            enable_fusion: fusion機能の有効化
        """
        self.model_name = model_name
        self.enable_fusion = enable_fusion
        self.model: Optional[laion_clap.CLAP_Module] = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
    def initialize_model(self) -> None:
        """CLAPモデルを初期化・ロード"""
        try:
            logger.info("Initializing CLAP model...")
            
            # CLAPモデルの初期化
            self.model = laion_clap.CLAP_Module(
                enable_fusion=self.enable_fusion,
                amodel='HTSAT-base'  # オーディオモデル
            )
            
            # 事前訓練済みモデルのロード
            self.model.load_ckpt()  # デフォルトのcheckpointをロード
            self.model.eval()  # 評価モードに設定
            
            logger.info("CLAP model initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize CLAP model: {e}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """
        テキストの前処理
        
        Args:
            text: 入力テキスト
            
        Returns:
            前処理されたテキスト
        """
        # 基本的な前処理
        text = text.strip()
        if not text:
            raise ValueError("Empty text input")
        
        # CLAPは日本語にも対応しているため、特別な前処理は不要
        return text
    
    def vectorize_keyword(self, keyword: str) -> Dict[str, Any]:
        """
        キーワードをベクトル化
        
        Args:
            keyword: ベクトル化するキーワード
            
        Returns:
            ベクトル化結果の辞書
        """
        if self.model is None:
            self.initialize_model()
        
        try:
            # テキスト前処理
            processed_text = self.preprocess_text(keyword)
            logger.info(f"Vectorizing keyword: {processed_text}")
            
            # テキストエンベディングを取得
            with torch.no_grad():
                text_embeddings = self.model.get_text_embedding([processed_text])
                
            # NumPy配列に変換
            vector = text_embeddings.cpu().numpy().flatten()
            
            result = {
                "keyword": processed_text,
                "vector": vector.tolist(),
                "dimension": len(vector),
                "model_info": {
                    "model_name": self.model_name,
                    "enable_fusion": self.enable_fusion,
                    "device": str(self.device)
                }
            }
            
            logger.info(f"Successfully vectorized keyword. Dimension: {len(vector)}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to vectorize keyword '{keyword}': {e}")
            raise
    
    def vectorize_batch(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        複数のキーワードを一括ベクトル化
        
        Args:
            keywords: ベクトル化するキーワードのリスト
            
        Returns:
            ベクトル化結果のリスト
        """
        if self.model is None:
            self.initialize_model()
        
        if not keywords:
            return []
        
        try:
            # 前処理
            processed_texts = [self.preprocess_text(keyword) for keyword in keywords]
            logger.info(f"Batch vectorizing {len(processed_texts)} keywords")
            
            # バッチでテキストエンベディングを取得
            with torch.no_grad():
                text_embeddings = self.model.get_text_embedding(processed_texts)
                
            # NumPy配列に変換
            vectors = text_embeddings.cpu().numpy()
            
            results = []
            for i, (keyword, processed_text) in enumerate(zip(keywords, processed_texts)):
                vector = vectors[i].flatten()
                result = {
                    "keyword": processed_text,
                    "vector": vector.tolist(),
                    "dimension": len(vector),
                    "model_info": {
                        "model_name": self.model_name,
                        "enable_fusion": self.enable_fusion,
                        "device": str(self.device)
                    }
                }
                results.append(result)
            
            logger.info(f"Successfully vectorized {len(results)} keywords")
            return results
            
        except Exception as e:
            logger.error(f"Failed to batch vectorize keywords: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        モデル情報を取得
        
        Returns:
            モデル情報の辞書
        """
        return {
            "model_name": self.model_name,
            "enable_fusion": self.enable_fusion,
            "device": str(self.device),
            "initialized": self.model is not None
        }


# グローバルインスタンス（シングルトンパターン）
_vector_processor: Optional[VectorProcessor] = None


def get_vector_processor() -> VectorProcessor:
    """
    VectorProcessorのシングルトンインスタンスを取得
    
    Returns:
        VectorProcessorインスタンス
    """
    global _vector_processor
    if _vector_processor is None:
        _vector_processor = VectorProcessor()
    return _vector_processor