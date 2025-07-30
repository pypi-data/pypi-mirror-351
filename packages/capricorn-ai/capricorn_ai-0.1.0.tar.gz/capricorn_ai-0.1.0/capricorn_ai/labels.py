# Capricorn_AI/labels.py

# PathMNIST: labels 0..8
path_labels = [
    "adipose",
    "background",
    "debris",
    "lymphocytes",
    "mucus",
    "smooth muscle",
    "normal colon mucosa",
    "cancer-associated stroma",
    "colorectal adenocarcinoma epithelium"
]

# DermaMNIST: labels 9..15
derma_labels = [
    "actinic keratoses/IEC",
    "basal cell carcinoma",
    "benign keratosis-like lesions",
    "dermatofibroma",
    "melanoma",
    "melanocytic nevi",
    "vascular lesions"
]

# BloodMNIST: labels 16..23
blood_labels = [
    "basophil",
    "eosinophil",
    "erythroblast",
    "immature granulocytes",
    "lymphocyte",
    "monocyte",
    "neutrophil",
    "platelet"
]

# Full list & count
ALL_LABELS = path_labels + derma_labels + blood_labels
NUM_CLASSES = len(ALL_LABELS)
