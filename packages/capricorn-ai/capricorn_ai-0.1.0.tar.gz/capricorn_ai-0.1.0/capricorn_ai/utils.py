# Capricorn_AI/utils.py
"""
Utility functions for image loading, preprocessing, and prediction.
"""
import numpy as np # type: ignore
from PIL import Image # type: ignore

from .models import load_model as _load_model
from .labels import ALL_LABELS, path_labels, derma_labels, blood_labels


def load_image(path, target_size=(224, 224)):
    """Load an image file and return as a NumPy array."""
    img = Image.open(path).convert('RGB')
    img = img.resize(target_size)
    return np.array(img)


def preprocess_input(img_array, model_name='capricorn0.1'):
    """Preprocess array based on model architecture requirements."""
    # Normalize to [0,1]
    img = img_array.astype('float32') / 255.0
    # expand dims for batch
    return np.expand_dims(img, axis=0)

def _categorize(label: str) -> str:
    if label in path_labels:
        return "Colon Histology"
    if label in derma_labels:
        return "Skin Bathology"
    if label in blood_labels:
        return "Blood Smear"
    return "Unknown"

def predict(
    model_name: str,
    image_array: np.ndarray,
    *,
    top_k: int | None = None,
    raw: bool = False,
    threshold: float = 0.75
) -> str | list[tuple[str, float]]:
    """
    By default returns a descriptive sentence:
      “I think this is <Category> – most likely <Label>! 
       I am <Confidence>% confident.”

    If raw=True, returns a list of (label, confidence) tuples
    (optionally truncated to top_k).

    If the top confidence is below `threshold`, returns:
      “This is unknown to me.”
    """
    model = _load_model(model_name)
    batch = preprocess_input(image_array, model_name)
    probs = model.predict(batch)[0]

    if probs.shape[0] != len(ALL_LABELS):
        raise ValueError(
            f"Expected {len(ALL_LABELS)} outputs, got {probs.shape[0]}"
        )

    # pair & sort
    labeled = sorted(
        zip(ALL_LABELS, probs),
        key=lambda x: x[1],
        reverse=True
    )

    # if user asked for raw tuples
    if raw:
        return labeled if top_k is None else labeled[:top_k]

    # otherwise build a human sentence
    top_label, top_conf = labeled[0]

    # fallback if we’re not confident enough
    if top_conf < threshold:
        return "This is unknown to me."

    category = _categorize(top_label)
    pct = top_conf * 100
    return (
        f"I think this is {category} – most likely "
        f"{top_label.title()}! I am {pct:.2f}% confident."
    )

def label_confidences(probs, labels=ALL_LABELS):
    """
    Given a 1D array of softmax probabilities (shape == NUM_CLASSES),
    return a list of (label, confidence) tuples sorted by confidence desc.
    """
    return sorted(zip(labels, probs), key=lambda x: x[1], reverse=True)
