#!/usr/bin/env python3
import pymongo
# import pandas as pd

# Connect to mongodb
client = pymongo.MongoClient("mongodb+srv://teadao:Teadao2021%40@serverlessinstance0.onlly.mongodb.net/twittertool?retryWrites=true&w=majority")
# myclient = MongoClient('mongodb+srv://teadao:Teadao2021%40@serverlessinstance0.onlly.mongodb.net/twittertool?retryWrites=true&w=majority')
# get database
# db = client.twittertool
db = client["twittertool"]
print(db)
# collection = db['tweet']
mycollection = db["tweet"]
print(mycollection)

one_record = mycollection.find_one()
print(one_record)
# Show database stats
all_record = mycollection.find()
print(all_record)

for row in all_record : 
    print(row )
list_cursor = list(all_record)
print(list_cursor) 
df = pd.DataFrame(list_cursor)
df.head()
# print(myclient.tweet)