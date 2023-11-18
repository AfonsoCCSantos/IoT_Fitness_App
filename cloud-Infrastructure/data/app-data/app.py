# Local imports
import datetime

# Third part imports
from flask import Flask
from flask import request
import pandas as pd
import joblib
import gzip
import json

from modules.functions import get_model_response


app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health():
    """Return service health"""
    return 'ok'


@app.route('/predict', methods=['POST'])
def predict():
    feature_dict = request.get_json()
    if not feature_dict:
        return {
            'error': 'Body is empty.'
        }, 500
    
    try:
        data = []
        model_name = feature_dict[0]['model']
        model = joblib.load('model/' + model_name + '.dat.gz')
        data.append(feature_dict[1])
        response = get_model_response(data, model)
    except ValueError as e:
        return {'error': str(e).split('\n')[-1].strip()}, 500

    return response, 200

@app.route('/training', methods=['POST'])
def training():
    feature_dict = request.get_json()
    if not feature_dict:
        return {
            'error': 'Body is empty.'
        }, 500
    return "a", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0')
