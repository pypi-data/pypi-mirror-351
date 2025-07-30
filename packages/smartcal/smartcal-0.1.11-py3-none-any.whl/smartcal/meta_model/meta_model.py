import joblib
import pandas as pd
import numpy as np
import importlib.resources as pkg_resources
from pathlib import Path

from smartcal.meta_model.meta_model_base import BaseMetaModel
from smartcal.config.configuration_manager.configuration_manager import ConfigurationManager

try:
    import smartcal.config.resources.models as model_pkg
except ImportError:
    model_pkg = None


config_manager = ConfigurationManager()

class MetaModel(BaseMetaModel):
    """
    MetaModel loads and uses a metric-specific model and label encoder to predict the best calibration method(s)
    for a given set of input features. It supports dynamic loading of models from a package resource directory.
    """
    def __init__(self, metric: str = config_manager.metric, top_n: int = config_manager.k_recommendations):
        """
        Initialize the MetaModel with a specific metric and number of top recommendations.

        :param metric: The calibration metric to use (e.g., 'ECE', 'MCE', etc.)
        :param top_n: Number of top models to return (default from config).
        """
        super().__init__(metric=metric, top_n=top_n)
        self._model_package = model_pkg
        self.model_path = self._get_metric_model_path()
        self.label_encoder_path = self._get_metric_label_encoder_path()
        self.model = self._load_component(self.model_path)
        self.label_encoder = self._load_component(self.label_encoder_path)

    def _get_model_pkg_base_path(self):
        """
        Get the base filesystem path for the models package.
        :return: Path to the models package directory.
        :raises ImportError: If the models package is not available.
        """
        if self._model_package is None:
            raise ImportError("model_pkg is not available. The models package could not be imported.")
        return model_pkg.__path__[0]

    def _get_metric_model_path(self) -> str:
        """
        Construct the path to the metric-specific model file.
        :return: Path to the model file for the selected metric.
        """
        base_path = self._get_model_pkg_base_path()
        return f"{base_path}/{self.metric}/AdaBoost.joblib"

    def _get_metric_label_encoder_path(self) -> str:
        """
        Construct the path to the metric-specific label encoder file.
        :return: Path to the label encoder file for the selected metric.
        """
        base_path = self._get_model_pkg_base_path()
        return f"{base_path}/{self.metric}/label_encoder.joblib"

    def _load_component(self, path):
        """
        Load a serialized component (model or encoder) from the given path using joblib.
        :param path: Path to the .joblib file.
        :return: Loaded Python object or None if not found or error.
        """
        if path is None or self._model_package is None:
            return None
        try:
            print(f"Loading component from path: {path}")
            filename = Path(path).name
            subdir = Path(path).parent.name
            resource = pkg_resources.files(self._model_package).joinpath(subdir, filename)
            if not resource.exists():
                return None
            with pkg_resources.as_file(resource) as f:
                return joblib.load(f)
        except Exception:
            return None

    def predict_best_model(self, input_features: dict) -> list:
        """
        Predict the best calibration models for the given input features.
        :param input_features: Dictionary of input features for the meta model.
        :return: List of (class_name, normalized_probability) tuples for the top recommendations.
        """
        X_input = pd.DataFrame([input_features])
        y_proba = self.model.predict_proba(X_input)[0]
        if self.label_encoder is not None:
            class_names = self.label_encoder.classes_
        elif hasattr(self.model, 'classes_'):
            class_names = self.model.classes_
        else:
            class_names = np.arange(len(y_proba))
        return self._select_and_normalize(y_proba, class_names)