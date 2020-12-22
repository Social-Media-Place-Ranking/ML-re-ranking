"""
Import Necessary Libraries
"""
from flask import Flask, request, jsonify
import os
import json
import ranking
import pickle


app = Flask(__name__)

"""
Flask App Routes
"""


@app.route("/")
def welcome():
    return config.get("WELCOMING")


@app.route("/re-rank", methods=["POST","GET"])
def get_es_results():
    """Post Method to rerank the data from es

    Returns:
        [Json]: Re-Ranked Locations
    """

    if request.method == "POST":
        payload = json.loads(request.get_json())
        query = payload.get("query")
        docs = payload.get("places")
        user_location = [float(payload.get("lat")), float(payload.get("lon"))]
        data = ranking.build_dataset(docs,user_location,query,tweets_collection )
        return (jsonify(ranking.rerank(model,data)))
    else:
        return config.get("WELCOMING")

"""
Flask App Entry Point (Main)
"""
if __name__ == "__main__":
    # load model at app launch
    model = pickle.load(open('model.sav', 'rb'))
    with open("config.json") as json_file:
        # append the json file, to get all of them in on json variable
        config = json.load(json_file)
    # connect to the database
    tweets_collection = ranking.connect_mongodb(config.get("MONGO_URL"), config.get("DB_NAME"), config.get("COL_NAME"))
    port = int(os.environ.get('PORT',5000))
    app.run(debug=True, use_reloader=False,host='0.0.0.0', port =port)
