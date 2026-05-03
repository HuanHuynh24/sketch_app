import os
import xgboost as xgb
# import lightgbm as lgb  # Mở comment nếu bạn dùng thêm LightGBM
import pandas as pd

class AIPredictorService:
    def __init__(self):
        self.model_path = os.path.join(
            os.path.dirname(__file__), 
            "../ml_models/xgboost_admission_2026.pkl" # Đổi tên file này cho khớp với file thật của bạn
        )
        self.model = self._load_model()

    def _load_model(self):
        try:
            # Load mô hình XGBoost (hoặc thay bằng LightGBM tùy bạn)
            with open(self.model_path, 'rb') as f:
                import pickle
                model = pickle.load(f)
            return model
        except FileNotFoundError:
            print(f"Cảnh báo: Không tìm thấy file model tại {self.model_path}")
            return None

    def predict_admission(self, features: dict) -> dict:
        if not self.model:
            return {"error": "AI Model is not loaded"}

        # Biến đổi dict thành DataFrame để đưa vào model
        df_features = pd.DataFrame([features])
        
        # Chạy dự đoán (code này có thể tùy chỉnh theo cấu trúc file train của bạn)
        prediction = self.model.predict(df_features)[0]
        
        # Giả lập trả về tỷ lệ đỗ (bạn có thể thay bằng hàm predict_proba nếu có)
        return {
            "predicted_score_2026": round(float(prediction), 2),
            "probability": 85.5, 
            "model_used": "XGBoost"
        }

# Khởi tạo instance (Singleton) để dùng chung
ai_predictor = AIPredictorService()