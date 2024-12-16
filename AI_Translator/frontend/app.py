from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__, static_folder='static', template_folder='templates')

app.secret_key = 'supersecretkey'  # Replace with a secure key

# Backend API URL
API_URL = "http://127.0.0.1:4001"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text = request.form.get("text")
        source_lang = request.form.get("source_lang")
        target_lang = request.form.get("target_lang")
        
        if not text or not target_lang:
            flash("Please provide text and target language!")
            return redirect(url_for("index"))

        # Call backend API for translation
        payload = {
            "text": text,
            "source_lang": source_lang if source_lang else None,
            "target_lang": target_lang
        }
        try:
            response = requests.post(f"{API_URL}/translate", json=payload)
            response.raise_for_status()
            result = response.json()
            return render_template(
                "result.html", 
                original_text=result["original_text"], 
                translated_text=result["translated_text"], 
                source_lang=result["source_language"], 
                target_lang=result["target_language"]
            )
        except requests.exceptions.RequestException as e:
            flash(f"Error communicating with the backend: {str(e)}")
            return redirect(url_for("index"))

    # Fetch supported languages
    try:
        languages = requests.get(f"{API_URL}/languages").json()
    except requests.exceptions.RequestException:
        languages = []
        flash("Could not fetch supported languages. Please try again later.")
    
    return render_template("index.html", languages=languages)

@app.route("/health")
def health():
    try:
        response = requests.get(f"{API_URL}/health")
        return response.json()
    except:
        return {"status": "unhealthy"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
