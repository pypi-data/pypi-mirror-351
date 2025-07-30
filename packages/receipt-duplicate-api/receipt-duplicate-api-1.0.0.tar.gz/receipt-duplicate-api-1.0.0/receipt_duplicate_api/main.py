"""
Production-Ready FastAPI Application for Duplicate Receipt Detection
- Uses NLP, Hashing, and CNNs for text and image deduplication
- Structured and modular for future extensibility
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List
from sentence_transformers import SentenceTransformer, util
from fastapi.responses import HTMLResponse
from PIL import Image
import imagehash
import hashlib
import numpy as np
import io
import torch
from torchvision import models, transforms
import logging
from config import AppConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Receipt Duplicate Detection API", version="1.0.0")

# Load NLP model
text_model = SentenceTransformer(AppConfig.TEXT_MODEL_NAME)

# Load CNN model
cnn_model = models.mobilenet_v2(pretrained=True)
cnn_model.classifier = torch.nn.Identity()
cnn_model.eval()
transform = transforms.Compose([
    transforms.Resize(AppConfig.IMAGE_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(AppConfig.IMAGE_MEAN, AppConfig.IMAGE_STD)
])

# In-memory stores (replace with DB in production)
existing_receipts_texts = []
existing_receipts_embeddings = []
existing_receipts_hashes = set()
existing_image_hashes = set()
existing_image_embeddings = []

class Receipt(BaseModel):
    vendor: str
    amount: str
    date: str
    receipt_number: str
    payment_method: str

def preprocess_receipt(receipt: Receipt) -> str:
    return f"{receipt.vendor.lower().strip()} {receipt.amount.strip()} {receipt.date.strip()} {receipt.receipt_number.lower().strip()} {receipt.payment_method.lower().strip()}"

def generate_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def is_text_duplicate(new_text: str, new_hash: str, threshold: float = AppConfig.TEXT_SIMILARITY_THRESHOLD) -> bool:
    if new_hash in existing_receipts_hashes:
        return True
    if not existing_receipts_embeddings:
        return False
    new_embedding = text_model.encode(new_text, convert_to_tensor=True)
    similarity_scores = util.cos_sim(new_embedding, existing_receipts_embeddings)
    max_similarity = similarity_scores.max().item()
    return max_similarity > threshold

def get_image_hashes(image: Image.Image):
    return {
        'ahash': str(imagehash.average_hash(image)),
        'phash': str(imagehash.phash(image)),
        'dhash': str(imagehash.dhash(image)),
        'whash': str(imagehash.whash(image))
    }

def get_image_embedding(image: Image.Image):
    img_tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        embedding = cnn_model(img_tensor).squeeze().numpy()
    return embedding

def is_image_duplicate(image: Image.Image, embedding_threshold: float = AppConfig.IMAGE_SIMILARITY_THRESHOLD) -> bool:
    new_hashes = get_image_hashes(image)
    hash_tuple = tuple(new_hashes.values())
    if hash_tuple in existing_image_hashes:
        return True

    new_embedding = get_image_embedding(image)
    if not existing_image_embeddings:
        return False

    similarities = [np.dot(new_embedding, emb) / (np.linalg.norm(new_embedding) * np.linalg.norm(emb)) for emb in existing_image_embeddings]
    return max(similarities) > embedding_threshold

@app.post("/submit-receipt")
async def submit_receipt(receipt: Receipt):
    try:
        processed_text = preprocess_receipt(receipt)
        receipt_hash = generate_hash(processed_text)

        if is_text_duplicate(processed_text, receipt_hash):
            return {"status": "duplicate", "message": "This receipt appears to be a duplicate (text-based)."}

        new_embedding = text_model.encode(processed_text, convert_to_tensor=True)
        existing_receipts_texts.append(processed_text)
        existing_receipts_embeddings.append(new_embedding)
        existing_receipts_hashes.add(receipt_hash)

        logger.info("Receipt stored successfully")
        return {"status": "success", "message": "Receipt submitted successfully (text-based)."}

    except Exception as e:
        logger.error(f"Error processing receipt: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/submit-image")
async def submit_image(file: UploadFile = File(...)):
    try:
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file")

    try:
        if is_image_duplicate(image):
            return {"status": "duplicate", "message": "This image appears to be a duplicate."}

        new_hashes = get_image_hashes(image)
        existing_image_hashes.add(tuple(new_hashes.values()))
        embedding = get_image_embedding(image)
        existing_image_embeddings.append(embedding)

        logger.info("Image stored successfully")
        return {"status": "success", "message": "Image submitted successfully."}

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
async def index():
    with open("templates/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/receipts")
def get_receipts():
    return {"receipts": existing_receipts_texts}
