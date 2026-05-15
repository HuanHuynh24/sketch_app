import logging
import pickle
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)

MODEL_FILENAME = "xgboost_admission_2026.pkl"
DEFAULT_PROBABILITY = 85.5


class AIPredictorService:
    def __init__(self, model_path: Path | None = None):
        self.model_path = model_path or (
            Path(__file__).resolve().parent.parent
            / "ml_models"
            / MODEL_FILENAME
        )
        self.model = self._load_model()

    def _load_model(self) -> Any | None:
        try:
            with self.model_path.open("rb") as model_file:
                return pickle.load(model_file)
        except FileNotFoundError:
            logger.warning("Admission model file not found: %s", self.model_path)
        except Exception:
            logger.exception("Cannot load admission model: %s", self.model_path)

        return None

    def predict_admission(self, features: dict) -> dict:
        if self.model is None:
            return {"error": "AI Model is not loaded"}

        try:
            import pandas as pd
        except ImportError:
            return {"error": "pandas is required to run admission prediction"}

        try:
            df_features = pd.DataFrame([features])
            prediction = self.model.predict(df_features)[0]
        except Exception:
            logger.exception("Admission prediction failed")
            return {"error": "Admission prediction failed"}

        return {
            "predicted_score_2026": round(float(prediction), 2),
            "probability": DEFAULT_PROBABILITY,
            "model_used": "XGBoost",
        }


ai_predictor = AIPredictorService()
