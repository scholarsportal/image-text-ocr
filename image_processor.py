import re
import requests
import torch
import conversion_utils as cu
import time
import asyncio
from got_ocr import predict


# Main function that processes the PDF and creates the Markdown output
def process_images(images, base_path):
  time_start = time.time()
  try:
    # Open output files to store responses
    latex_file = open(base_path + ".tex", "w")
    extracted_file = open(base_path + "_js.tex", "w")
    markdown_file = open(base_path + ".md", 'w')
    html_file = open(base_path + ".html", "w")
    html_file.write("<!DOCTYPE html><html><body>")
    js_file = open(base_path + "_js.html", "w")
    # Process each page asynchronously
    print(f"Processing {len(images)} pages for {base_path} ...")
    latex_text, js_text, latex_extracted = asyncio.run(process_pages(images))

    # Finalize LaTeX doc
    latex_text += "\n\\end{document}"
    latex_extracted += "\n\\end{document}"

    print("Converting output formats...")
    # Write to file
    latex_file.write(f"{latex_text}\n")
    latex_file.close()
    extracted_file.write(f"{latex_extracted}\n")
    extracted_file.close()

    # JavaScript-rendered
    js_file.write(f"{cu.html_template(js_text)}")
    js_file.close()

    # Markdown
    try:
      markdown_text = cu.latex_to_markdown(latex_extracted)
      markdown_file.write(f"{markdown_text}\n")
    except Exception as e:
      print(f'An error occurred while converting LaTeX to MD:\n{e}')
    finally:
      if not markdown_file.closed:
        markdown_file.close()
    # HTML
    try:
      html_response = cu.latex_to_html(latex_text)
      html_file.write(f"{html_response}\n")
      html_file.write("</body></html>")
    except Exception as e:
      print(f'An error occurred while converting LaTeX to HTML:\n{e}')
    finally:
      if not html_file.closed:
        html_file.close()

    print(f"Output saved to {base_path}.*")

  except Exception as e:
    print(f"An error occurred: {e}")

  time_end = time.time()
  total_duration = time_end - time_start
  # total_minutes, total_seconds = divmod(total_duration, 60)
  print(f"{base_path} processing time: {time.strftime('%Mm %Ss', time.gmtime(total_duration))}")


async def process_pages(images):
  tasks = []
  latex_text = "\\begin{document}\n\\pagenumbering{arabic}\n"
  latex_extracted = "\\begin{document}\n\\pagenumbering{arabic}\n"
  js_text = ""
  for page_number, image in enumerate(images, start=1):
    tasks.append(process_page(page_number, image))
  responses = await asyncio.gather(*tasks)
  # Sort the responses by page_number to ensure correct order
  responses.sort(key=lambda x: x['page_number'])
  for result in responses:
    # Add page number and response to latex_text
    latex_response = result['latex']
    text_value = latex_response
    html_string = result["html"]
    # Extract the value of 'text' inside the rendered JavaScript block
    pattern = r'const text\s*=\s*"(.*?)\\n"\ '
    script_block = re.search(pattern, html_string, re.DOTALL)
    if script_block:
      text_value = script_block.group(1)
      text_value = text_value.replace('\\n"+\n"', '\n').replace('\\\\', '\\')
    latex_text += latex_response + "\n\n\\newpage\n\n"
    latex_extracted += text_value + "\n\n\\newpage\n\n"
    if js_text != "":
      js_text += " +\n"
    js_text += cu.to_js_string(text_value) + " + \"\\n\\n\""
  return latex_text, js_text, latex_extracted


# Define a semaphore to limit the number of concurrent tasks
# to the number of GPUs
n_gpus = torch.cuda.device_count()
sem = asyncio.Semaphore(n_gpus if n_gpus > 0 else 1)


async def process_page(page_number, image):
  async with sem:
    start_page = time.time()  # Start timer for the current page
    base64_img = cu.image_to_base64(image)
    response = await asyncio.to_thread(predict, base64_img)

    end_page = time.time()  # End timer for the current page
    print(f"Page {page_number} processed in {end_page - start_page:.1f}s")
    return {
        'page_number': page_number,
        'latex': response["output"],
        'html': response["html"]
    }


# Send a base64 image to the server and get the HTML response
def send_image_to_server(base64_img, page_number):
  server_url = "http://localhost:8000"
  payload = {"input": base64_img, "page": page_number}
  response = requests.post(f"{server_url}/predict", json=payload)
  if response.status_code == 200:
    try:
      outer_output = response.json().get("output")
      if isinstance(outer_output, dict) and "output" in outer_output:
        return outer_output["output"]
      return outer_output
    except KeyError:
      print("Error: 'output' key not found in response")
      return ""
  else:
    print(f"Error {response.status_code}: {response.text}")
    return ""
