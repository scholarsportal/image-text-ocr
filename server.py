import json
import os
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModel, AutoTokenizer
import torch
from PIL import Image
from io import BytesIO
import base64
import tempfile


class RequestModel(BaseModel):
  input: str  # Base64 encoded image
  page: int = 1  # Default to page 1 if not provided


# Initialize FastAPI app
app = FastAPI()

tokenizer = None
model = None


@app.on_event("startup")
async def load_model():
  global tokenizer, model
  tokenizer = AutoTokenizer.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True)
  model = AutoModel.from_pretrained('ucaslcl/GOT-OCR2_0',
                                    trust_remote_code=True,
                                    low_cpu_mem_usage=True,
                                    device_map='cuda',
                                    use_safetensors=True,
                                    pad_token_id=tokenizer.pad_token_id)
  # Check if CUDA is available and how many GPUs there are
  if torch.cuda.is_available():
    n_gpus = torch.cuda.device_count()
    if n_gpus > 1:
      # If multiple GPUs are available, use DataParallel to distribute across GPUs
      model = torch.nn.DataParallel(model)
    model = model.eval().cuda()  # Use the GPUs
  else:
    model = model.eval()  # Fallback to CPU if CUDA is not available


@app.post("/predict")
async def predict(request: RequestModel):
  image_base64 = request.input
  page = request.page
  # Decode the base64 string into bytes
  img_bytes = base64.b64decode(image_base64)
  img = Image.open(BytesIO(img_bytes))
  # Create a temporary file to save the image
  with tempfile.NamedTemporaryFile(suffix='.jpg', delete=True) as temp_file:
    img.save(temp_file.name)
    # Uncomment the next line if you want to save the image for debugging purposes
    # img.save(os.path.join(".", f"raw_{page}.jpg"))
    output = model.chat(tokenizer, temp_file.name, ocr_type='format')
  # Return the model output as a JSON response
  return {"output": output}


# Run the FastAPI app using Uvicorn
if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=8000)
