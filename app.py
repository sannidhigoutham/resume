import os
import fitz  # PyMuPDF
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
print("API KEY:", os.getenv("OPENAI_API_KEY"))
print("BASE URL:", os.getenv("OPENAI_API_BASE"))
app = Flask(__name__)
os.makedirs("uploads", exist_ok=True)

# ✅ Configure client for OpenRouter explicitly
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

@app.route("/upload", methods=["POST"])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    pdf = request.files['file']
    filename = pdf.filename
    file_path = os.path.join("uploads", filename)
    pdf.save(file_path)

    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()

    prompt = f"""
Extract a list of programming languages, frameworks, and technologies from the resume text below.
Only return a JSON array of skill names.
Resume text:
{text}
"""

    try:
        response = client.chat.completions.create(
    model="mistralai/mistral-7b-instruct",  # ✅ Correct model ID
    messages=[{"role": "user", "content": prompt}]
)

        content = response.choices[0].message.content.strip()
        skills = json.loads(content)

        return jsonify({"skills": skills})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)


#     python -m venv venv
# venv\Scripts\activate
# python app.py