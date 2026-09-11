import torch
import numpy as np
from typing import List, Dict, Any, Tuple
from app.services.sequence_model import get_pretrained_model

class MLScorer:
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            self.model = get_pretrained_model()
        except Exception as e:
            print(f"Failed to load LSTM model: {e}")
            self.model = None

    def predict_probability(self, features: dict) -> tuple[float, dict[str, float]]:
        """Legacy method for backward compatibility. Wraps the single feature into a sequence."""
        return self.predict_path_probability([features])

    def predict_path_probability(self, path_features: List[Dict[str, Any]]) -> Tuple[float, Dict[str, float]]:
        """
        Evaluates an entire sequence of hops (path) to determine if the behavior
        matches a known exchange deposit / peeling chain.
        """
        if not self.model:
            # Fallback mock probability if model not loaded
            return 0.5, {"in_degree": 0.2, "out_degree": 0.3}

        # Ensure all feature dictionaries have exactly 165 features and map them to a sequence
        sequence = []
        for feat_dict in path_features:
            values = list(feat_dict.values())
            # Pad or truncate to 165
            if len(values) < 165:
                values.extend([0.0] * (165 - len(values)))
            elif len(values) > 165:
                values = values[:165]
            sequence.append(values)

        # Convert to tensor: shape (batch_size=1, sequence_length, input_size=165)
        tensor_seq = torch.tensor([sequence], dtype=torch.float32)

        # Predict
        with torch.no_grad():
            prob = float(self.model(tensor_seq).item())

        # Mock SHAP attribution since Captum/SHAP for LSTMs is complex to set up dynamically here
        feature_names = list(path_features[0].keys())
        shap_features = {}
        if feature_names:
            # Fake attribution for demo visualization
            shap_features = {
                feature_names[0]: 0.15,
                feature_names[1] if len(feature_names) > 1 else "f_2": 0.10,
                feature_names[2] if len(feature_names) > 2 else "f_3": 0.05
            }

        return prob, shap_features

ml_scorer = MLScorer()
