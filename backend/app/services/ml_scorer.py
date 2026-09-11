import xgboost as xgb
import shap
import numpy as np

class MLScorer:
    def __init__(self):
        self.model = None
        self.explainer = None
        self._load_model()

    def _load_model(self):
        try:
            self.model = xgb.Booster()
            self.model.load_model("ml_artifacts/xgb_exchange_model.json")
        except Exception as e:
            print(f"Failed to load XGBoost model: {e}")
            self.model = None

    def predict_probability(self, features: dict) -> tuple[float, dict[str, float]]:
        if not self.model:
            # Fallback mock probability if model not loaded
            return 0.5, {"in_degree": 0.2, "out_degree": 0.3}

        # Convert features to DMatrix
        feature_names = list(features.keys())
        feature_values = [list(features.values())]
        dmatrix = xgb.DMatrix(feature_values, feature_names=feature_names)

        # Predict
        prob = float(self.model.predict(dmatrix)[0])

        # SHAP attribution
        try:
            if not self.explainer:
                self.explainer = shap.TreeExplainer(self.model)
            shap_values = self.explainer.shap_values(feature_values)
            
            # Map top 3 features
            top_indices = np.argsort(np.abs(shap_values[0]))[::-1][:3]
            shap_features = {feature_names[i]: float(shap_values[0][i]) for i in top_indices}
        except:
            shap_features = {}

        return prob, shap_features

ml_scorer = MLScorer()
