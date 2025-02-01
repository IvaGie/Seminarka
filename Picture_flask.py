from flask import Flask, render_template, send_file, redirect, url_for
import imageio.v2 as imageio
import numpy as np
import os

app = Flask(__name__)

# Cesta k obrázku
img_path = 'static/original_image.jpg'

# Funkce pro zpracování obrázků
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
    increase = img_array * percent_lighter
    lightened = np.clip(img_array + increase, 0, 255)
    return lightened.astype(np.uint8)

def convert_to_darker(img_array, percent_darker):
    increase = img_array * percent_darker
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

# Domovská stránka s tlačítky
@app.route('/')
def index():
    return render_template('index.html')

# Funkce pro každé tlačítko
@app.route('/negative')
def negative():
    img_array = imageio.imread(img_path)
    negative_picture = convert_to_negativ(img_array)
    output_path = 'static/negative_image.jpg'
    imageio.imwrite(output_path, negative_picture)
    return send_file(output_path, mimetype='image/jpeg')

@app.route('/+')
def percent_lighter():
   percent = 0
   return percent_lighter + 0,5

@app.route('/-')
def percent_darker():
   percent = 0
   return percent_darker - 0,5
@app.route('/lighter')
def lighter():
    img_array = imageio.imread(img_path)
    lighter_picture = convert_to_lighter(img_array)
    output_path = 'static/lighter_image.jpg'
    imageio.imwrite(output_path, lighter_picture)
    return send_file(output_path, mimetype='image/jpeg')

@app.route('/darker')
def darker():
    img_array = imageio.imread(img_path)
    darker_picture = convert_to_darker(img_array)
    output_path = 'static/darker_image.jpg'
    imageio.imwrite(output_path, darker_picture)
    return send_file(output_path, mimetype='image/jpeg')

@app.route('/smaller')
def smaller():
    img_array = imageio.imread(img_path)
    smaller_picture = make_smaller(img_array)
    output_path = 'static/smaller_image.jpg'
    imageio.imwrite(output_path, smaller_picture)
    return send_file(output_path, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True)
