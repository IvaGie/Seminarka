import time

from flask import Flask, render_template, send_file, jsonify, request
import imageio.v2 as imageio
import numpy as np
import os

app = Flask(__name__)

# Define the paths to the original and current images
uploads_dir = 'static/uploads'
os.makedirs(uploads_dir, exist_ok=True)


# Image processing functions
def is_blackAndWhite(img_array):
    if len(img_array.shape) == 2:
        return True
    if img_array.shape[2] == 3:
        if np.all(img_array[:, :, 0] == img_array[:, :, 1]) and np.all(img_array[:, :, 1] == img_array[:, :, 2]):
            return True
    return False


def convert_to_negativ(img_array):
    return 255 - img_array


def convert_to_lighter(img_array, percent_lighter):
    increase = img_array * (percent_lighter / 100)
    lightened = np.clip(img_array + increase, 0, 255)
    return lightened.astype(np.uint8)


def convert_to_darker(img_array, percent_darker):
    increase = img_array * (percent_darker / 100)
    darkened = np.clip(img_array - increase, 0, 255)
    return darkened.astype(np.uint8)


def make_smaller(img_array):
    if is_blackAndWhite(img_array):
        return img_array[::2, ::2]
    else:
        red_channel = img_array[::2, ::2, 0]
        green_channel = img_array[::2, ::2, 1]
        blue_channel = img_array[::2, ::2, 2]
        return np.stack([red_channel, green_channel, blue_channel], axis=-1)




@app.route('/')
def index():
    return render_template('index.html')


# Routes for applying filters
@app.route('/filter/negative', methods=['GET'])
def negative():
    img_array = imageio.imread('static/uploads/original_image.jpg')
    negative_picture = convert_to_negativ(img_array)
    output_path = 'static/uploads/negative_image.jpg'
    imageio.imwrite(output_path, negative_picture)
    return jsonify({"image_url": f"/{output_path}"})


@app.route('/filter/lighter', methods=['GET'])
def lighter():
    intensity = float(request.args.get('percent', 20))  # default is 20%
    img_array = imageio.imread('static/uploads/current_image.jpg')  # Always work with the current image
    lighter_picture = convert_to_lighter(img_array, intensity)

    # Save the modified image as the current image
    output_path = 'static/uploads/current_image.jpg'
    imageio.imwrite(output_path, lighter_picture)

    return jsonify({"image_url": f"/{output_path}"})


@app.route('/filter/darker', methods=['GET'])
def darker():
    intensity = float(request.args.get('percent', 20))  # default is 20%
    img_array = imageio.imread('static/uploads/current_image.jpg')  # Always work with the current image
    darker_picture = convert_to_darker(img_array, intensity)

    # Save the modified image as the current image
    output_path = 'static/uploads/current_image.jpg'
    imageio.imwrite(output_path, darker_picture)

    return jsonify({"image_url": f"/{output_path}"})


@app.route('/filter/smaller', methods=['GET'])
def smaller():
    img_array = imageio.imread('static/uploads/original_image.jpg')
    smaller_picture = make_smaller(img_array)
    output_path = 'static/uploads/smaller_image_' + str(int(time.time())) + '.jpg'
    imageio.imwrite(output_path, smaller_picture)
    return jsonify({"image_url": f"/{output_path}"})


@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "No file selected"})

    # Save original image as the base
    original_image_path = os.path.join(uploads_dir, 'original_image.jpg')
    file.save(original_image_path)

    # Set the current image as the original image for initial view
    current_image_path = os.path.join(uploads_dir, 'current_image.jpg')
    imageio.imwrite(current_image_path, imageio.imread(original_image_path))

    return jsonify({
        "original_image": f"/static/uploads/original_image.jpg",
        "current_image": f"/static/uploads/current_image.jpg"
    })



if __name__ == '__main__':
    app.run(debug=True)
