# config.py

class AppConfig:
    TEXT_MODEL_NAME = 'all-MiniLM-L6-v2'
    TEXT_SIMILARITY_THRESHOLD = 0.95
    IMAGE_SIMILARITY_THRESHOLD = 0.95
    IMAGE_SIZE = (224, 224)
    IMAGE_MEAN = [0.485, 0.456, 0.406]
    IMAGE_STD = [0.229, 0.224, 0.225]
