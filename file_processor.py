from pdf2image import convert_from_path
from PIL import Image
from image_processor import process_images
import os

def process_file(inputfile_path):
  root, ext = os.path.splitext(inputfile_path)
  images = []
  # If inputfile_path ends with .jpg, load the image from file
  if ext == ".jpg":
    images = [Image.open(inputfile_path)]
  elif ext == ".pdf":
    print("Converting PDF pages to images...")
    images = convert_from_path(inputfile_path)
  if len(images) >= 1:
    process_images(images, root)
  else:
    print("No images found to process.")
