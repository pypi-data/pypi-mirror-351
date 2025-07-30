# Capricorn_AI/models.py
"""
Loader functions for pre-trained Keras models.
"""
import os
from tensorflow.keras.models import load_model as keras_load_model

# Point at our package’s keras_models/ folder, not the old top-level models/
default_models_dir = os.path.join(
    os.path.dirname(__file__),
    'ai_models'
)

# Map model keys to filenames
enabled_models = {
    'capricorn0.1': 'Capricorn0.1.keras',
    # extend with {'densenet121': 'densenet121.h5', ...} as needed
}

def list_models():
    """Return available model keys."""
    return list(enabled_models.keys())

def get_model_path(name):
    """Compute full file path for a given model name."""
    if name not in enabled_models:
        raise ValueError(
            f"Model '{name}' not found. Available: {list_models()}"
        )
    return os.path.join(default_models_dir, enabled_models[name])

def load_model(name):
    """Load and return the Keras model for the given name."""
    path = get_model_path(name)
    return keras_load_model(path)
