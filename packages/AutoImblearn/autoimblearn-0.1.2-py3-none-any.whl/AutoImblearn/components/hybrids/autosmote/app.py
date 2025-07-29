import os
import shutil
import re

from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

from autosmote.classifiers import get_clf
from autosmote.rl.training import train

app = Flask(__name__)

params = {}

class Arguments:
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)

@app.route("/health", methods=["GET"])
def health():
    return "OK", 200

# POST function to set training parameters
@app.route('/set', methods=['POST'])
def set_params():
    """ Set training parameters """
    data = request.get_json()
    global params
    for key, value in data.items():
        params[key] = value
    if 'metric' not in params or 'dataset' not in params:
        raise Exception("data not complete, need to include metric and dataset")

    return jsonify(params), 201

# GET function to retrieve all books
@app.route('/results/<dataset_name>', methods=['GET'])
def get_result(dataset_name: str):
    """ Train the auto-sklearn and return the result in json format """
    global params
    args = Arguments(params)

    X_train = pd.read_csv(os.path.join("/data/interim", args.data_names[0])).to_numpy()
    y_train = pd.read_csv(os.path.join("/data/interim", args.data_names[1])).to_numpy().ravel()
    X_test = pd.read_csv(os.path.join("/data/interim", args.data_names[2])).to_numpy()
    y_test = pd.read_csv(os.path.join("/data/interim", args.data_names[3])).to_numpy().ravel()
    print("loading finished")

    # Select training validation data
    size = X_train.shape[0]
    indices = [i for i in range(size)]
    np.random.shuffle(indices)

    val_idx, train_idx = indices[:int(size * args.val_ratio)], \
                         indices[int(size * args.val_ratio):]

    train_X, val_X = X_train[train_idx], X_train[val_idx]
    train_y, val_y = y_train[train_idx], y_train[val_idx]

    clf = get_clf(args.clf)

    # Search space for ratios
    args.ratio_map = [0.0, 0.25, 0.5, 0.75, 1.0]
    print("finished parameter setting")

    # Start training
    score = train(args, train_X, train_y, val_X, val_y, X_test, y_test, clf)
    print("finished training")

    # print("Results:", args.dataset, score)
    result = score

    return jsonify({"result": result}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)