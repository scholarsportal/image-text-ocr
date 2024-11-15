import os
from PIL import Image
import base64
import io
import torch
from transformers import AutoModel, AutoTokenizer, logging
import tempfile

# Load the model and tokenizer outside of the function
global tokenizer, model
tokenizer = AutoTokenizer.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True)
# Set pad_token_id to eos_token_id if not already set
if tokenizer.pad_token_id is None:
  tokenizer.pad_token_id = tokenizer.eos_token_id
model = AutoModel.from_pretrained('ucaslcl/GOT-OCR2_0',
                                  trust_remote_code=True,
                                  low_cpu_mem_usage=True,
                                  device_map='cuda',
                                  use_safetensors=True,
                                  pad_token_id=tokenizer.pad_token_id)
# Check if CUDA is available and how many GPUs there are
if torch.cuda.is_available():
  # If multiple GPUs are available, use DataParallel
  n_gpus = torch.cuda.device_count()
  if n_gpus > 1:
    model = torch.nn.DataParallel(model)
  model = model.eval().cuda()  # Use the GPUs
else:
  model = model.eval()  # Fallback to CPU if CUDA is not available
logging.set_verbosity_error()



def predict(image_base64: str) -> dict:
  # Decode the base64 string into bytes
  img_bytes = base64.b64decode(image_base64)
  img = Image.open(io.BytesIO(img_bytes))

  # Create a temporary file to save the image
  with tempfile.NamedTemporaryFile(suffix='.jpg', delete=True) as temp_file:
    img.save(temp_file.name)
    # output = model.chat(tokenizer,
    #                     temp_file.name,
    #                     ocr_type='format',
    #                     render=True,
    #                     save_render_file="tmpfile")
    # # Read the content from the saved tmpfile
    # with open("tmpfile", "r") as f:
    #   rendered = f.read()
    # os.remove("tmpfile")
    output = model.chat(tokenizer,
                        temp_file.name,
                        ocr_type='format')
    rendered = ""

  return {'output': output, 'html': rendered}
