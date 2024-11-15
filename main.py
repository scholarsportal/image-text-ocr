import sys
from file_processor import process_file

if __name__ == "__main__":
  # Ensure proper usage
  if len(sys.argv) != 2:
    print("Usage: python main.py <path_to_pdf>")
    sys.exit(1)

  inputfile_path = sys.argv[1]

  # Process the PDF and save the HTML output
  process_file(inputfile_path)
