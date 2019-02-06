from flask import Flask, jsonify, request
import json
from flask_cors import CORS
import numpy as np
import pandas as pd
import non_deep_classifiers

import numpy as np

app = Flask(__name__)
CORS(app)

@app.route('/euclidean', methods=['POST'])
def euclidean():
  realvec = json.loads(request.form['timing_matrix_registered'])
  currvec = json.loads(request.form['timing_matrix_current'])
  real = pd.DataFrame(realvec)
  current = pd.DataFrame(currvec)

  classifier = non_deep_classifiers.Euclidean()
  classifier.train(real)

  return jsonify({"real": realvec, "current": currvec, "distance": classifier.get_euclidean_distance(current)})

@app.route('/scaledmanhattan', methods=['POST'])
def scaledmanhattan():
  realvec = json.loads(request.form['timing_matrix_registered'])
  currvec = json.loads(request.form['timing_matrix_current'])
  real = pd.DataFrame(realvec)
  current = pd.DataFrame(currvec)

  classifier = non_deep_classifiers.ScaledManhattan()
  classifier.train(real)

  return jsonify({"real": realvec, "current": currvec, "distance": classifier.get_scaled_manhattan_distance(current)})