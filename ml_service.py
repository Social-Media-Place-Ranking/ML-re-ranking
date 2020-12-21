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
    return "ML Service"


@app.route("/re-rank", methods=["POST"])
def get_es_results():
    """Post Method to rerank the data from es

    Returns:
        [Json]: Re-Ranked Locations
    """

    if request.method == "POST":
        query = request.args.get("query")
        docs = json.loads(request.get_json())
        user_location = [float(request.args.get("lat")), float(request.args.get("lon"))]
        data = ranking.build_dataset(docs,user_location,query,tweets_collection )
        
        return (jsonify(ranking.rerank(model,data, docs)))


"""
Flask App Entry Point (Main)
"""
if __name__ == "__main__":
    # load model at app launch
    model = pickle.load(open('model.sav', 'rb'))
    # define the mongoDB endpoint
    with open("config.json") as json_file:
        # append the json file, to get all of them in on json variable
        config = json.load(json_file)
    # connect to the database
    tweets_collection = ranking.connect_mongodb(config.get("MONGO_URL"), config.get("DB_NAME"), config.get("COL_NAME"))
    port = int(os.environ.get('PORT',5000))
    app.run(debug=True, use_reloader=False,host='0.0.0.0', port =port)
