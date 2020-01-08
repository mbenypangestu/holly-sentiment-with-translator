
import requests
import json
from datetime import datetime
from time import sleep

from mongoengine import connect
from pymongo import MongoClient

from database.mongo_service import MongoService


class ReviewTranslatedService(MongoService):
    def __init__(self):
        super().__init__()

    def get_all_sentiment_reviews(self):
        review_translateds = self.db.review_translated.find()
        return review_translateds

    def get_review_by_hotel_locid(self, hotel_id):
        review_translateds = self.db.review_translated.find({
            'hotel_id': hotel_id
        })
        return review_translateds

    def create(self, review_translated):
        try:
            result = self.db.review_translated.insert_one(
                review_translated).inserted_id
            print("Msg: Success saving data with id ",
                  result, "to Translated review !")
        except Exception as e:
            print("Err: Failed to save result Translated review !")
            print("------> ", e)
