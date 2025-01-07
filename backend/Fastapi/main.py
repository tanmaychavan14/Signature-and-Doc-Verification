from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
import shutil
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import sys

model = load_model('models/signature_model.h5')


# Create temp directory for uploaded images
temp_dir = "temp_signatures"
os.makedirs(temp_dir, exist_ok=True)

app = FastAPI()

def verify_signature(original_signature_path, verification_signature_path):
    # Load and preprocess original signature
    original_signature = cv2.imread(original_signature_path)
    original_signature = cv2.resize(original_signature, (100, 100)).astype('float32') / 255.0

    # Load and preprocess verification signature
    verification_signature = cv2.imread(verification_signature_path)
    verification_signature = cv2.resize(verification_signature, (100, 100)).astype('float32') / 255.0

    # Add batch dimension
    original_signature = np.expand_dims(original_signature, axis=0)
    verification_signature = np.expand_dims(verification_signature, axis=0)

    # Predict using the model
    prediction = model.predict([original_signature, verification_signature])
    
    # Determine result
    result = "Genuine" if prediction[0][0] < 0.5 else "Forged"
    return result
@app.post("/verify-signature/")
async def verify_signature_endpoint(original_signature: UploadFile = File(...), verification_signature: UploadFile = File(...)):
    # Create dynamic file paths based on upload
    original_path = os.path.join(temp_dir, original_signature.filename)
    verification_path = os.path.join(temp_dir, verification_signature.filename)

    with open(original_path, "wb") as f:
        shutil.copyfileobj(original_signature.file, f)

    with open(verification_path, "wb") as f:
        shutil.copyfileobj(verification_signature.file, f)

    # Call the signature verification function
    result = verify_signature(original_path, verification_path)

    # Cleanup temporary files
    os.remove(original_path)
    os.remove(verification_path)

    # Return the result
    return JSONResponse(content={"result": result})
