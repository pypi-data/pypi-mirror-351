"""
File Processor GUI API version

Created by Christopher (Egrigor86)
"""
__version__ = "0.1.1"


import os
import json
import requests
from flask import Flask, render_template_string, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename

API_KEY = "ZdzJUQaEk1rpsryaEqFwKw"
fastapi_url = "http://1.158.11.6:5010"

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
FAILED_FOLDER = os.path.join(OUTPUT_FOLDER, "failed_files")
FIRST_OUTPUT_FOLDER = os.path.join(OUTPUT_FOLDER, "first_outputs")

for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, FAILED_FOLDER, FIRST_OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

app = Flask(__name__)

def load_config():
    default_config = {
        "prompt1": "",
        "prompt2": "",
        "selected_model": "",
        "history": {"prompt1": [], "prompt2": []}
    }
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
            for k in default_config:
                if k not in config:
                    config[k] = default_config[k]
            for k in default_config["history"]:
                if k not in config["history"]:
                    config["history"][k] = []
    else:
        config = default_config
    return config

def save_config(prompt1, prompt2, model_id=""):
    config = load_config()
    history = config.setdefault("history", {"prompt1": [], "prompt2": []})
    if prompt1 and prompt1 not in history["prompt1"]:
        history["prompt1"].append(prompt1)
    if prompt2 and prompt2 not in history["prompt2"]:
        history["prompt2"].append(prompt2)
    config["prompt1"] = prompt1
    config["prompt2"] = prompt2
    if model_id:
        config["selected_model"] = model_id
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

def get_models():
    try:
        headers = {"x-api-key": API_KEY}
        response = requests.get(f"{FASTAPI_URL}/models", headers=headers)
        response.raise_for_status()
        return response.json().get("models", [])
    except Exception as e:
        print(f"Model fetch error: {e}")
        return []

def process_file_content(content, prompt, model_id):
    try:
        payload = {"model": model_id, "message": f"{prompt}\n{content}"}
        headers = {"x-api-key": API_KEY}
        response = requests.post(f"{FASTAPI_URL}/chat", json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        print(f"Processing error: {e}")
        return ""

@app.route("/", methods=["GET"])
def index():
    config = load_config()
    models = get_models()
    files = os.listdir(UPLOAD_FOLDER)
    processed_files = os.listdir(OUTPUT_FOLDER)
    first_pass_files = os.listdir(FIRST_OUTPUT_FOLDER)
    failed_log_exists = os.path.exists(os.path.join(FAILED_FOLDER, "failed_files.log"))

    return render_template_string(TEMPLATE,
        config=config,
        models=models,
        files=files,
        processed_files=processed_files,
        first_pass_files=first_pass_files,
        failed_log_exists=failed_log_exists,
        prompt1_history=config["history"]["prompt1"],
        prompt2_history=config["history"]["prompt2"],
        fastapi_url=FASTAPI_URL
    )

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return redirect(url_for("index"))
    file = request.files["file"]
    if file.filename:
        filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(filepath)
    return redirect(url_for("index"))

@app.route("/process_one", methods=["POST"])
def process_one():
    prompt1 = request.form["prompt1"]
    prompt2 = request.form["prompt2"]
    model_id = request.form["model_id"]
    selected_file = request.form["selected_file"]
    include_source = request.form.get("include_source") == "on"
    save_config(prompt1, prompt2, model_id)

    with open(os.path.join(UPLOAD_FOLDER, selected_file), "r", encoding="utf-8") as f:
        content = f.read()

    first_output = process_file_content(content, prompt1, model_id)
    combined = content + first_output if include_source else first_output
    second_output = process_file_content(combined, prompt2, model_id)

    return f"<h3>First Output:</h3><pre>{first_output}</pre><h3>Second Output:</h3><pre>{second_output}</pre><a href='/'>Back</a>"

@app.route("/process_all", methods=["POST"])
def process_all():
    prompt1 = request.form["prompt1"]
    prompt2 = request.form["prompt2"]
    model_id = request.form["model_id"]
    include_source = request.form.get("include_source") == "on"
    save_config(prompt1, prompt2, model_id)

    files = os.listdir(UPLOAD_FOLDER)
    for fname in files:
        path = os.path.join(UPLOAD_FOLDER, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            result1 = process_file_content(content, prompt1, model_id)
            combined = content + result1 if include_source else result1
            result2 = process_file_content(combined, prompt2, model_id)
            with open(os.path.join(FIRST_OUTPUT_FOLDER, f"first_output_{fname}"), "w", encoding="utf-8") as out1:
                out1.write(result1)
            with open(os.path.join(OUTPUT_FOLDER, f"processed_{fname}"), "w", encoding="utf-8") as out2:
                out2.write(result2)
        except Exception as e:
            with open(os.path.join(FAILED_FOLDER, "failed_files.log"), "a") as log:
                log.write(f"{fname} failed: {str(e)}\n")
    return redirect(url_for("index"))

@app.route("/save_config", methods=["POST"])
def save_cfg():
    prompt1 = request.form["prompt1"]
    prompt2 = request.form["prompt2"]
    model_id = request.form.get("model_id", "")
    save_config(prompt1, prompt2, model_id)
    return redirect(url_for("index"))

@app.route("/view_file")
def view_file():
    folder = request.args.get("folder")
    filename = request.args.get("file")
    path = os.path.join(folder, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        content = f"Failed to load file: {str(e)}"
    return f"<h2>{filename}</h2><pre>{content}</pre><a href='/'>Back</a>"

@app.route("/delete_file")
def delete_file():
    folder = request.args.get("folder")
    filename = request.args.get("file")
    try:
        os.remove(os.path.join(folder, filename))
    except Exception as e:
        print(f"Delete error: {e}")
    return redirect(url_for("index"))

@app.route("/rename_file", methods=["POST"])
def rename_file():
    folder = request.form["folder"]
    old_name = request.form["old_name"]
    new_name = request.form["new_name"]
    try:
        os.rename(os.path.join(folder, old_name), os.path.join(folder, new_name))
    except Exception as e:
        print(f"Rename error: {e}")
    return redirect(url_for("index"))

@app.route("/download_file")
def download_file():
    folder = request.args.get("folder")
    filename = request.args.get("file")
    return send_file(os.path.join(folder, filename), as_attachment=True)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>File Processor</title>
  <style>
    body { font-family: monospace; background: #111; color: #ddd; padding: 20px; }
    input, textarea, select, button { font-family: monospace; margin: 4px 0; }
    textarea { width: 100%; }
    a { color: #66f; text-decoration: none; margin-right: 10px; }
    a:hover { text-decoration: underline; }
    form.inline { display: inline-block; margin: 0 10px 10px 0; }
  </style>
</head>
<body>
<h1>File Processor</h1>
<p>Current API URL (from .env): <b>{{ fastapi_url }}</b></p>

<!-- Upload -->
<form method="post" action="/upload" enctype="multipart/form-data">
  <input type="file" name="file">
  <button type="submit">Upload</button>
</form>

<!-- Main Processing Form -->
<form method="post" action="/process_one">
  <label>Model:</label>
  <select name="model_id">
    {% for model in models %}
      <option value="{{ model }}" {% if model == config.selected_model %}selected{% endif %}>{{ model }}</option>
    {% endfor %}
  </select><br>

  <label>File to process:</label>
  <select name="selected_file">
    {% for f in files %}
      <option value="{{ f }}">{{ f }}</option>
    {% endfor %}
  </select><br>

  Include Source in Step 2: <input type="checkbox" name="include_source" checked><br>

  <label>Prompt 1:</label><br>
  <textarea name="prompt1" rows="4">{{ config.prompt1 }}</textarea><br>
  <select onchange="this.previousElementSibling.value=this.value">
    <option value="">Select past prompt 1</option>
    {% for p in prompt1_history %}<option value="{{ p }}">{{ p|truncate(80) }}</option>{% endfor %}
  </select><br>

  <label>Prompt 2:</label><br>
  <textarea name="prompt2" rows="4">{{ config.prompt2 }}</textarea><br>
  <select onchange="this.previousElementSibling.value=this.value">
    <option value="">Select past prompt 2</option>
    {% for p in prompt2_history %}<option value="{{ p }}">{{ p|truncate(80) }}</option>{% endfor %}
  </select><br>

  <button type="submit">Process Selected File</button>
</form>

<!-- Process All -->
<form method="post" action="/process_all">
  <input type="hidden" name="model_id" value="{{ config.selected_model }}">
  <input type="hidden" name="prompt1" value="{{ config.prompt1 }}">
  <input type="hidden" name="prompt2" value="{{ config.prompt2 }}">
  <input type="hidden" name="include_source" value="on">
  <button type="submit">Process All Files</button>
</form>

<!-- Save Config -->
<form method="post" action="/save_config" onsubmit="syncPrompts()">
  <input type="hidden" name="prompt1" id="hidden_prompt1">
  <input type="hidden" name="prompt2" id="hidden_prompt2">
  <input type="hidden" name="model_id" id="hidden_model_id">
  <button type="submit">Save Current Prompts & Model</button>
</form>

<script>
function syncPrompts() {
  document.getElementById("hidden_prompt1").value = document.querySelector("textarea[name='prompt1']").value;
  document.getElementById("hidden_prompt2").value = document.querySelector("textarea[name='prompt2']").value;
  document.getElementById("hidden_model_id").value = document.querySelector("select[name='model_id']").value;
}
</script>

<!-- Uploaded Files -->
<h3>Uploaded Files</h3>
<ul>
{% for f in files %}
  <li>
    {{ f }}
    <a href="/view_file?folder=uploads&file={{ f }}">view</a>
    <a href="/download_file?folder=uploads&file={{ f }}">download</a>
    <a href="/delete_file?folder=uploads&file={{ f }}">delete</a>
    <form method="post" action="/rename_file" class="inline">
      <input type="hidden" name="folder" value="uploads">
      <input type="hidden" name="old_name" value="{{ f }}">
      <input type="text" name="new_name" placeholder="rename to">
      <button type="submit">rename</button>
    </form>
  </li>
{% endfor %}
</ul>

<!-- Output Files -->
<h3>Processed Files</h3>
<ul>
{% for f in processed_files %}
  <li>
    {{ f }}
    <a href="/view_file?folder=outputs&file={{ f }}">view</a>
    <a href="/download_file?folder=outputs&file={{ f }}">download</a>
    <a href="/delete_file?folder=outputs&file={{ f }}">delete</a>
    <form method="post" action="/rename_file" class="inline">
      <input type="hidden" name="folder" value="outputs">
      <input type="hidden" name="old_name" value="{{ f }}">
      <input type="text" name="new_name" placeholder="rename to">
      <button type="submit">rename</button>
    </form>
  </li>
{% endfor %}
</ul>

<h3>First Pass Files</h3>
<ul>
{% for f in first_pass_files %}
  <li>
    {{ f }}
    <a href="/view_file?folder=outputs/first_outputs&file={{ f }}">view</a>
    <a href="/download_file?folder=outputs/first_outputs&file={{ f }}">download</a>
    <a href="/delete_file?folder=outputs/first_outputs&file={{ f }}">delete</a>
    <form method="post" action="/rename_file" class="inline">
      <input type="hidden" name="folder" value="outputs/first_outputs">
      <input type="hidden" name="old_name" value="{{ f }}">
      <input type="text" name="new_name" placeholder="rename to">
      <button type="submit">rename</button>
    </form>
  </li>
{% endfor %}
</ul>

{% if failed_log_exists %}
<h3>Failed Files Log</h3>
<ul>
  <li>
    failed_files.log
    <a href="/view_file?folder=outputs/failed_files&file=failed_files.log">view</a>
    <a href="/download_file?folder=outputs/failed_files&file=failed_files.log">download</a>
    <a href="/delete_file?folder=outputs/failed_files&file=failed_files.log">delete</a>
  </li>
</ul>
{% endif %}

</body>
</html>
"""

def main():
    app.run(debug=True, port=5200)

if __name__ == "__main__":
    main()

