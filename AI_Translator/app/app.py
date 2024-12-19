from flask import Flask, render_template, request, flash
import requests

app = Flask(__name__, static_folder="static", template_folder="templates")


API_URL = "http://127.0.0.1:8000"


@app.route("/", methods=["GET", "POST"])
def index():
    languages = []
    translated_text = None
    original_text = None
    source_lang = None
    target_lang = None

    # Fetch supported languages
    try:
        response = requests.get(f"{API_URL}/languages")
        response.raise_for_status()
        languages = response.json()
    except requests.exceptions.RequestException:
        flash("Could not fetch supported languages. Please try again later.")

    # Handle POST request
    if request.method == "POST":
        text = request.form.get("text")
        source_lang = request.form.get("source_lang")
        target_lang = request.form.get("target_lang")

        if not text or not target_lang:
            flash("Please provide text and target language!")
        else:
            payload = {
                "text": text,
                "source_lang": source_lang if source_lang else None,
                "target_lang": target_lang,
            }
            try:
                response = requests.post(f"{API_URL}/translate", json=payload)
                response.raise_for_status()
                result = response.json()
                original_text = result["original_text"]
                translated_text = result["translated_text"]
                source_lang = result["source_language"]
                target_lang = result["target_language"]
            except requests.exceptions.RequestException as e:
                flash(f"Error communicating with the backend: {str(e)}")

    return render_template(
        "index.html",
        languages=languages,
        original_text=original_text,
        translated_text=translated_text,
        source_lang=source_lang,
        target_lang=target_lang,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
