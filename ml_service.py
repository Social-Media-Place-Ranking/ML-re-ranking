"""
Import Necessary Libraries 
"""
from flask import Flask, request, jsonify 
import os

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

    if request.method =="POST":
        return (request.json)

"""
Flask App Entry Point (Main)
"""
if __name__ == "__main__":
    #load model at app launch
    port = int(os.environ.get('PORT',5000))
    app.run(debug=True, use_reloader=False,host='0.0.0.0', port =port)
