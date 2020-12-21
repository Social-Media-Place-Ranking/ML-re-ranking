# Machine Learning Re-ranking

## Introduction 
The code in this repository is basically implementing the result of the research that has been done in the [training repository](https://github.com/Social-Media-Place-Ranking/machine-learning-training).

This repository consists of: 
- Dockerfile 
- Mongodb Configuration
- ML Model
- Pipeline to execute the model

## How to use the code

The function **build_dataset()** is called with the following parameteres:
- documents : JSON that contains the places resulting from the elastic search
- user_location : [longitude, latitude]
- query : the inputed query
- collection: tweets collection
