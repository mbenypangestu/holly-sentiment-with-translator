from mongoengine import connect
from pymongo import MongoClient


class MongoService:
    host = "localhost"
    port = 27017
    client = None
    db = None
    topic = "hotel_reviews"

    def __init__(self):
        self.connect_mongo()

    def connect_mongo(self):
        try:
            self.client = MongoClient(host=self.host, port=self.port)
            self.db = self.client.holly_production

            print("Success connecting to mongodb !\n")

        except:
            print("Failed to connect mongo database !\n")
