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

from measurement import Body3D 

app = Flask(__name__)
data_dir = os.path.join(os.getcwd(), 'data')
heroku_url = 'https://body-measurement-app.herokuapp.com/predict'

def preprocess_image(image):
    if image.shape[-1] == 1:
        return False
    else:
        image = cv.resize(image, (224, 224), cv.INTER_AREA)
        return image

@app.route("/predict", methods=['GET','POST'])
def predict():
    dogimagefile= request.files['image'].read()
    # dogimage = np.fromstring(dogimagefile, np.uint8)
    # dogimage = cv.imdecode(dogimage,cv.IMREAD_COLOR) 
    
    # processed_image = preprocess_image(dogimage)

    person = pywavefront.Wavefront(
        os.path.join(data_dir, 'person.obj'),
        create_materials=True,
        collect_faces=True
    )
    faces = np.array(person.mesh_list[0].faces)
    vertices = np.array(person.vertices)

    body = Body3D(vertices, faces)

    height, chest_length, waist_length = body.getMeasurements()

    response = {
            'height': height,
            'chest' : chest_length,
            'waist' : waist_length
            }

    return jsonify(response)

if __name__ == '__main__':
    app.run(host=heroku_url, debug=True, port=5000, threaded=False, use_reloader=False)