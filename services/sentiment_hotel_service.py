
import requests
import json
from datetime import datetime
from time import sleep

from mongoengine import connect
from pymongo import MongoClient

from database.mongo_service import MongoService


class SentimentHotelService(MongoService):
    def __init__(self):
        super().__init__()

    def get_all_sentiment_hotels(self):
        sentiment_reviews = self.db.sentiment_hotel.find()
        return sentiment_reviews

    def get_review_by_hotel_locid(self, hotel_id):
        sentiment_reviews = self.db.sentiment_hotel.find({
            'hotel_id': hotel_id
        })
        return sentiment_reviews

    def create(self, sentiment_hotel):
        try:
            result = (self.db.sentiment_hotel.insert_one(
                sentiment_hotel)).inserted_id
            print("Msg: Success saving data with id ",
                  result, "to sentiment hotel !")
        except:
            print("Err: Failed to save result sentiment hotel !")
