import requests
import json


response = requests.get('mongodb+srv://teadao:Teadao2021%40@serverlessinstance0.onlly.mongodb.net/twittertool?retryWrites=true&w=majority')

print(response.json())