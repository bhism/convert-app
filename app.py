from flask import Flask, request, send_file, jsonify
from PIL import Image
import io
import zipfile
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

@app.route('/warmup', methods=['GET'])
def warmup():
    return "Warmed up!", 200


@app.route('/convert', methods=['POST'])
def convert_images():
    if 'images' not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist('images')
    target_format = request.form.get('format')

    # Pillow uses 'JPEG' instead of 'JPG'
    if target_format == 'jpg':
        target_format = 'jpeg'

    if target_format not in ['jpeg', 'png', 'gif', 'bmp', 'webp']:
        return jsonify({"error": "Unsupported format"}), 400

    converted_images = []

    for file in files:
        # Open the uploaded image
        img = Image.open(file)
        img = img.convert("RGB") if target_format in ['jpeg', 'bmp'] else img

        # Save the converted image to a BytesIO object (in-memory)
        img_io = io.BytesIO()
        img.save(img_io, format=target_format.upper())
        img_io.seek(0)  # Move pointer back to start of file
        converted_images.append(img_io)

    # If it's just one image, send the image directly
    if len(converted_images) == 1:
        return send_file(converted_images[0], as_attachment=True, download_name=f"converted_image.{target_format}")

    # If multiple images, zip them in-memory and send the zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for i, img_io in enumerate(converted_images):
            # Save each image as a file in the zip
            zipf.writestr(f"converted_image_{i + 1}.{target_format}", img_io.getvalue())

    zip_buffer.seek(0)

    return send_file(zip_buffer, as_attachment=True, download_name="converted_images.zip", mimetype='application/zip')


if __name__ == '__main__':
    app.run(debug=True)
