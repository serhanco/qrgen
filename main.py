from flask import Flask, request, send_file, render_template_string
import qrcode
from PIL import Image, ImageDraw
import requests
from io import BytesIO
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>QR Code Generator</title>
</head>
<body>
    <h2>QR Code Generator with Logo</h2>
    <form action="/" method="post">
        <label for="param">Enter parameter:</label>
        <input type="text" id="param" name="param" required>
        <input type="submit" value="Generate QR Code">
    </form>
    {% if image_url %}
        <h3>Download your QR Code:</h3>
        <a href="{{ image_url }}" download>Click here to download</a>
        <br><br>
        <img src="{{ image_url }}" width="300">
    {% endif %}
</body>
</html>
"""

def download_logo(url):
    """Download the logo from the given URL."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    image = Image.open(BytesIO(response.content))
    return image.convert('RGBA')

def generate_qr_with_logo(url, logo_url):
    """Generate a QR code with a centered logo."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    qr_img = qr_img.convert('RGBA')

    logo = download_logo(logo_url)
    logo = logo.resize((150, 150))

    pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)
    qr_img.paste(logo, pos, logo)

    output_path = "static/qr_code.png"
    qr_img.save(output_path)
    return output_path

@app.route("/", methods=["GET", "POST"])
def home():
    image_url = None
    if request.method == "POST":
        param = request.form.get("param", "").strip()
        if param:
            base_url = "https://www.medicaltravel.net/contact-us/"
            logo_url = "https://www.medicaltravel.ch/wp-content/uploads/sites/18/2019/06/2.jpg"
            qr_url = f"{base_url}?param={param}"
            output_path = generate_qr_with_logo(qr_url, logo_url)
            image_url = f"/{output_path}"

    return render_template_string(HTML_TEMPLATE, image_url=image_url)

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    app.run(host="0.0.0.0", port=5000)
