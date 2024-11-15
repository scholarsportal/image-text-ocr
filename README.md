# Image-text OCR

This is a project to use Vision-text models to recognize the text in pdf files. Currently, only GOT_OCR2.0 is supported. The goal of this project is to extract the text from the images and then convert it into a formatted text file (LaTeX, HTML, Markdown).

## Requirements

- Python 3.10+
- Pytorch 2.4+

## Usage

1. Create a python virtual environment: `python -m venv venv`
1. Install the required packages: `pip install -r requirements.txt`
1. Start the server: `python server.py`
1. Process a file: `python main.py docs/test1.pdf`

The converted files will be saved in the `docs` directory.
