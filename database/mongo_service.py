from mongoengine import connect
from pymongo import MongoClient
from datetime import datetime


class MongoService:
    host = "localhost"
    port = 27017
    client = None
    db = None
    topic = "hotel_reviews"
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def __init__(self):
        self.connect_mongo()

    def connect_mongo(self):
        try:
            self.client = MongoClient(host=self.host, port=self.port)
            self.db = self.client.holly_dev

            print("[", self.now, "]---> Success connecting to database!")
        except:
            print("[", self.now, "]---> Failed to connect database!")
