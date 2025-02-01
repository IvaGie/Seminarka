from flask import Flask, render_template, jsonify, request
import imageio.v2 as imageio
import numpy as np
import os
import cv2
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
    if is_blackAndWhite(img_array) == False:
        increase = img_array * (percent_lighter / 100)
        lightened = np.clip(img_array + increase, 0, 255)
        return lightened.astype(np.uint8)

def convert_to_darker(img_array, percent_darker):
    if is_blackAndWhite(img_array) == False:
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




def highlight_edges(img_array):
    if len(img_array.shape) == 2:  # Jednokanálový obrázek (grayscale)
        gray_image = img_array
        return gray_image
    elif len(img_array.shape) == 3 and img_array.shape[2] == 3:  # Tříkanálový obrázek (RGB)
        gray_image = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        raise ValueError("Obrázek musí být buď jednokanálový (grayscale) nebo tříkanálový (RGB).")

    sobel_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)  # Detekce horizontálních hran
    sobel_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)  # Detekce vertikálních hran

    edges = cv2.magnitude(sobel_x, sobel_y)

    edges = cv2.convertScaleAbs(edges)
    return edges


def make_solarization(img_array, threshold=128):
    # Solarizace obrázku na základě prahu
    img_array = img_array.astype(np.float32)  # Převod na float32 pro manipulaci s hodnotami

    # Aplikace solarizace na každý pixel (kanály R, G, B)
    mask = img_array > threshold
    img_array[mask] = 255 - img_array[mask]  # Invertování hodnot, které jsou nad prahem

    img_array = np.clip(img_array, 0, 255)  # Zajištění, že hodnoty zůstanou v rozsahu 0-255
    return img_array.astype(np.uint8)  # Převod zpět na uint8 pro zobrazení obrázku



isEdges = 0
isSolarized = 0
isNegativ = 0
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/filter/edges', methods=['GET'])
def edges():    #hrany
    global isEdges
    if isEdges == 0:
        img_array = imageio.imread('static/uploads/current_image.jpg')
        edges_image = highlight_edges(img_array)
        output_path = 'static/uploads/current_image.jpg'
        imageio.imwrite(output_path, edges_image)
        isEdges = 1
        return jsonify({"image_url": f"/{output_path}"})
    else:
        print('Fitr uz byl pouzit')
        output_path = 'static/uploads/current_image.jpg'
        return jsonify({"image_url": f"/{output_path}"})


@app.route('/filter/solarization', methods=['GET'])
def solarization():
    global isSolarized
    if isSolarized == 0:
        img_array = imageio.imread('static/uploads/current_image.jpg')
        solarization_picture = make_solarization(img_array)
        output_path = 'static/uploads/current_image.jpg'
        imageio.imwrite(output_path, solarization_picture)
        isSolarized = 1
        return jsonify({"image_url": f"/{output_path}"})
    else:
        print('Fitr uz byl pouzit')
        output_path = 'static/uploads/current_image.jpg'
        return jsonify({"image_url": f"/{output_path}"})

# Routes for applying filters
@app.route('/filter/negative', methods=['GET'])
def negative():
    global isNegativ
    if isNegativ == 0:
        img_array = imageio.imread('static/uploads/current_image.jpg')
        negative_picture = convert_to_negativ(img_array)
        output_path = 'static/uploads/current_image.jpg'
        imageio.imwrite(output_path, negative_picture)
        isNegativ = 1
        return jsonify({"image_url": f"/{output_path}"})
    else:
        print('Fitr uz byl pouzit')
        output_path = 'static/uploads/current_image.jpg'
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
    # Načteme aktuální obrázek, který byl upravený (např. po aplikaci filtru)
    img_array = imageio.imread('static/uploads/current_image.jpg')  # Pracujeme s aktuálním obrázkem
    smaller_picture = make_smaller(img_array)  # Zmenšíme aktuální obrázek
    output_path = 'static/uploads/current_image.jpg'  # Přepíšeme aktuální obrázek zmenšeným obrázkem
    imageio.imwrite(output_path, smaller_picture)  # Uložíme zmenšený obrázek zpět na stejnou cestu
    return jsonify({"image_url": f"/{output_path}"})



# Route to reset the image to the original one (clear all filters)
@app.route('/filter/reset', methods=['GET'])
def reset():
    global isEdges, isSolarized, isNegativ
    # Reload the original image as the current image
    original_image_path = 'static/uploads/original_image.jpg'
    current_image_path = 'static/uploads/current_image.jpg'

    # Re-save the original image as current image to reset any applied filters
    imageio.imwrite(current_image_path, imageio.imread(original_image_path))
    isEdges = 0
    isSolarized = 0
    isNegativ = 0
    return jsonify({"image_url": f"/{current_image_path}"})


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
