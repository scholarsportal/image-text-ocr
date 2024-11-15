import json
import pypandoc
import re
from io import BytesIO
import base64


# Convert a page to a base64 encoded image
def image_to_base64(image):
  buffered = BytesIO()
  image.save(buffered, format="JPEG")
  img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
  return img_str

def to_js_string(latex_string):
  # Use json.dumps to escape the string for JavaScript
  js_string = json.dumps(latex_string)
  return js_string


def html_template(js_string):
  mathpix_result = f"""
<!DOCTYPE html>
<html lang="en" data-lt-installed="true">
<head>
  <meta charset="UTF-8">
  <title>LaTeX render with mathpix</title>
  <script>
    const text = {js_string}
  </script>
  <style>
    #content {{
      max-width: 800px;
      margin: auto;
    }}
  </style>
  <script>
    let script = document.createElement('script');
    script.src = "https://cdn.jsdelivr.net/npm/mathpix-markdown-it@1.3.6/es5/bundle.js";
    document.head.append(script);
    script.onload = function() {{
      const isLoaded = window.loadMathJax();
      if (isLoaded) {{
        console.log('Styles loaded!')
      }}
      const el = window.document.getElementById('content-text');
      if (el) {{
        const options = {{
          htmlTags: true
        }};
        const html = window.render(text, options);
        el.outerHTML = html;
      }}
    }};
  </script>
</head>
<body>
  <div id="content"><div id="content-text"></div></div>
</body>
</html>
"""
  return mathpix_result


# Convert LaTeX to Markdown
def latex_to_markdown(latex_string):
  latex_string = re.sub(r'\\title\{\s*([^}]*)\s*\}', r'## \1', latex_string, flags=re.DOTALL)
  markdown_string = pypandoc.convert_text(latex_string, 'md', format='latex')
  markdown_string = markdown_string.replace(r'\#', '#')
  return markdown_string


# Convert LaTeX to HTML
def latex_to_html(latex_string):
  latex_string = re.sub(r'\\title\{\s*([^}]*)\s*\}', r'\1\n\n', latex_string, flags=re.DOTALL)
  html_string = pypandoc.convert_text(latex_string, 'html', format='latex')
  return html_string
