import os
import json
import requests
import cv2 as cv
import pywavefront
import numpy as np
import pandas as pd
from flask import Flask
from flask import jsonify
from flask import request

from model import Body3D 

app = Flask(__name__)

meter2inches = 39.3701
data_dir = os.path.join(os.getcwd(), 'data')
heroku_url = 'https://body-measurement-app.herokuapp.com/predict'
key_points_path = os.path.join(data_dir, os.listdir(data_dir)[0])

def preprocess_image(image):
    if image.shape[-1] == 1:
        return False
    else:
        image = cv.resize(image, (224, 224), cv.INTER_AREA)
        return image

def model_estimations(image):
    person = pywavefront.Wavefront(
        os.path.join(data_dir, key_points_path),
        create_materials=True,
        collect_faces=True
    )

    faces = np.array(person.mesh_list[0].faces)
    vertices = np.array(person.vertices)

    return faces, vertices

def scale_output(measurments):
    measurments = list(measurments)
    for i, measurment in enumerate(measurments):
        measurment = measurment * meter2inches
        measurments[i] = int(measurment)
    return measurments

@app.route("/predict", methods=['GET','POST'])
def predict():
    imagefile= request.files['image'].read()
    image = np.fromstring(imagefile, np.uint8)
    image = cv.imdecode(image,cv.IMREAD_COLOR) 
    
    processed_image = preprocess_image(image)
    faces, vertices = model_estimations(processed_image)

    body = Body3D(vertices, faces)

    measurments = body.getMeasurements()
    measurments = scale_output(measurments)
    height, chest_length, waist_length, hip_length, thigh_length, neck_length, neck_hip_length = measurments

    response = {
            'height'   : height,
            'chest'    : chest_length,
            'waist'    : waist_length,
            'hip'      : hip_length,
            'thigh'    : thigh_length,
            'neck'     : neck_length,
            'neck_hip' : neck_hip_length,

            }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host=heroku_url, port=5000, threaded=False, use_reloader=False)