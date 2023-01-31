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

# one_record = mycollection.find_one()
# print(one_record)
# Show database stats
# all_record = mycollection.find()
# print(all_record)

# for row in all_record({"hashtag": "Array"}): 
#     print(row)
x = mycollection.find_one()
# myquery = {"hashtags": "Array"}

# mydoc=mycollection.find(myquery)

# for row in mydoc :
#     print(row)

for x in mycollection.find({}, {"hashtags" :" Array"}) :
 print(x)
     
# list_cursor = list(all_record)
# for row in all_record.find({}, {"hashtag":"Array"}): 
#     print(row)
# df = pd.DataFrame(list_cursor)
# df.head()
# print(myclient.tweet)