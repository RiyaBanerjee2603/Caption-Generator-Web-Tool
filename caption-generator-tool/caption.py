import os
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import google.generativeai as genai
from PIL import Image

# Setup Gemini API
genai.configure(api_key="AIzaSyBKffrmXiJf57T3B35lFuT73wfRSjWxwPE")  # Replace with your actual API key
model = genai.GenerativeModel("models/gemini-1.5-flash")

UPLOAD_FOLDER = "Images"

# Setup Flask to designate where uploaded images are temporarily stored
app = Flask(__name__)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

#Defining function to generate caption
def generate_caption(image_path):
    image = Image.open(image_path).convert("RGB")

    response = model.generate_content(
        [image, "Suggest a good caption for the image, taking into account what is in the image."]
    )

    return response.text.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    caption = ""
    error = ""

    if request.method == "POST":
        uploaded_file = request.files.get("file")

        if uploaded_file and uploaded_file.filename.lower().endswith((".jpg", ".jpeg", ".png")): #Only .jpg, .jpeg, and .png files are allowed
            filename = secure_filename(uploaded_file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            uploaded_file.save(filepath)

            try:
                caption = generate_caption(filepath)
                os.remove(filepath)  # Delete image after use
            except Exception as e:
                error = f"Error generating caption: {str(e)}"
                if os.path.exists(filepath):
                    os.remove(filepath)  # Ensure image is deleted even on failure
        else:
            error = "Please upload a JPG or PNG image."

    return render_template("index.html", caption=caption, error=error)

if __name__ == "__main__":
    app.run(debug=True)

