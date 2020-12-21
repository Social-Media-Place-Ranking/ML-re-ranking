import os
import json
import pandas as pd
import pymongo
import haversine as hs
import numpy as np
import xgboost as xgb


def connect_mongodb(mongoDB_url, database_name, collection_name):
    """connect to the mongoDB 

    Args:
        mongoDB_url : mongoDB endpoint url
        database_name : database name
        collection_name : collection name

    Returns:
        the database collection object
    """

    # create mongodb client
    mongoDB_client = pymongo.MongoClient(mongoDB_url)

    # get the database
    tweets_database = mongoDB_client[database_name]

    # get the collection
    tweets_collection = tweets_database[collection_name]

    # return the collection object
    return tweets_collection


def find_tweets_near_place(coordinates, tweets_collection):
    """find the tweets within 100m radius from the passed coordinates

    Args:
       coordinates : lon,lat for the central point

    Returns:
        extracted info from the tweets
    """

    # define the body of the query
    myquery = [

        {"$geoNear": {

            "near": {"type": "Point", "coordinates": coordinates},
            "distanceField": "place.coordinates",
            "maxDistance": 100}}, {"$group": {

                "_id": None,
                "tweets_count": {"$sum": 1},
                "tweets_average_length": {"$avg": {"$strLenCP": "$tweet"}},
                "replies_count": {"$sum": "replies_count"},
                "retweets_count": {"$sum": "retweets_count"},
                "likes_count": {"$sum": "likes_count"},
                "popularity": {"$avg": "$popularity"},
                "hashtags": {"$sum": {"$size": "$hashtags"}},
                "mentions": {"$sum": {"$size": "$mentions"}}}}]

    # send the query and return the results
    return list(tweets_collection.aggregate(myquery))


def jaccard_similarity(list1, list2):
    s1 = set(list1)
    s2 = set(list2)
    return float(len(s1.intersection(s2)) / len(s1.union(s2)))


def build_dataset(documents, user_location, query, collection):

    # define the list result of the documents data
    documents_data = []
    # go over each document and gather its info
    for doc in documents:

        # slice the location of the document
        coordinates = list(doc['_source']['location'].values())

        # get the tweets
        tweets = find_tweets_near_place(coordinates, collection)

        # neglect the doc that don't have tweets
        if len(tweets):

            # get the document name
            document = doc['_source']['name']

            # find the jaccard similarity
            jaccard_entire = jaccard_similarity(
                query.split(" "), document.split(" "))

            # slice the first 3 characters and find the jaccard similaity
            sub_query = [word[:3] for word in query.split(" ")]
            sub_document = [word[:3] for word in document.split(" ")]

            sub_jaccard = jaccard_similarity(sub_query, sub_document)

            # check if the query and the document have the same prefix
            prefix_match = query[:3] == document[:3]

            # create two tuples of coordinates
            tweet_loc = (coordinates[0], coordinates[1])
            user_loc = (user_location[0], user_location[1])

            # get the distance between the user and the document(in meters)
            distance = hs.haversine(tweet_loc, user_loc)

            # define the dict for the document
            doc_data = {"query": query,
                        "document": document,
                        "location.lat": coordinates[0],
                        "location.lon": coordinates[1],
                        "query_length": len(query),
                        "document_length": len(doc['_source']['name']),
                        "jaccard_entire": jaccard_entire,
                        "sub_jaccard": sub_jaccard,
                        "prefix_match": prefix_match,
                        "elasticsearch_score": doc['_score'],
                        "distance": distance}

            # add the tweets info
            doc_data.update(tweets[0])

            # append the doc dict to the list result
            documents_data.append(doc_data)

    # return the documents data
    return pd.json_normalize(documents_data)


def feature_eng(data):

    data['prefix_match'] = data['prefix_match'].map({False: 0, True: 1})

    skewed_columns = ["elasticsearch_score", "distance",
                      "tweets_count", "tweets_average_length", "hashtags", "mentions"]

    for column in skewed_columns:
        data[column] = np.log((1 + data[column]))

    return data


def pred_rank(data, loaded_model):

    data_dmatrix = xgb.DMatrix(
        data.drop(['_id', 'query', 'document', 'location.lat', 'location.lon'], 1))

    pred_rank = loaded_model.predict(data_dmatrix)

    data["rank"] = pred_rank

    data = data.sort_values(by="rank", ascending=False)

    results = data[['document', 'location.lat', 'location.lon']]

    return results


def rerank(loaded_model, data, query_docs):
    # data feature Engineering
    data = feature_eng(data)

    results = pred_rank(data, loaded_model)

    return json.loads(results.to_json(orient='records'))
