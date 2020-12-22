# Machine Learning Re-ranking

## Introduction
This is the machine learning micro-service, which is responsible for re-ranking places based on their popularity on Twitter

## Code flow
* accept POST requests from the web clients side (query, user location, and places)
* the function **build_dataset()** is called with the following parameteres:
  - documents : JSON that contains the places resulting from the elastic search
  - user_location : [longitude, latitude]
  - query : the inputed query
  - collection: tweets collection
* the **rereank()** function is called with the following parameters:
  - loaded_model: the machine learning model (loaded from main)
  - data : the dataset returned from **build_dataset()**
  this function takes the dataset and reranks the documents and finally returns the results in json format
* return re-ranked places 



## Usage

#### to build the docker image:

- run the command `docker build -t ml_service:latest`
  - the `-t` is used to set the a TAG for the docker image

#### to run the service without the docker:

- run the command `python ml_service.py`

#### to use the service:

- send a POST request to the service containing query, user location, and places
- example of the passed data:
```javascript
    { 
      "query" : "starbucks",
      "lat" : 40.224,
      "lon" : -70.345,
      "places" : [
                    {"_source":{
                            "location" : { "lat" : 41.35, "lon" : -71},
                            "name" : "starbucks"
                              }}
                              ....
                  ]
    }
```

