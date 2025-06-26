import os
import fitz  # PyMuPDF
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load environment variables
load_dotenv()

# Setup Flask app
app = Flask(__name__)
os.makedirs("uploads", exist_ok=True)

# ✅ OpenRouter setup
api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL")

if not api_key or not base_url:
    raise ValueError("OPENROUTER_API_KEY or OPENROUTER_BASE_URL not set in .env")

client = OpenAI(
    api_key=api_key,
    base_url=base_url  # ✅ Note: OpenAI Python SDK uses `base_url`
)

@app.route("/upload", methods=["POST"])
def upload_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    pdf = request.files['file']
    filename = pdf.filename
    file_path = os.path.join("uploads", filename)
    pdf.save(file_path)

    # Extract text from PDF
    doc = fitz.open(file_path)
    text = "".join([page.get_text() for page in doc])

    prompt = f"""
Extract a list of programming languages, frameworks, and technologies from the resume text below.
Only return a JSON array of skill names.
Resume text:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="openrouter/mistralai/mistral-7b",  # ✅ Correct OpenRouter model ID
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.choices[0].message.content.strip()
        skills = json.loads(content)

        return jsonify({"skills": skills})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)