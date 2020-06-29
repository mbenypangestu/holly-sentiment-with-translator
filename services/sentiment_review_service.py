
import requests
import json
from datetime import datetime
from time import sleep

from mongoengine import connect
from pymongo import MongoClient

from database.mongo_service import MongoService


class SentimentReviewService(MongoService):
    def __init__(self):
        super().__init__()

    def get_all_sentiment_reviews(self):
        sentiment_reviews = self.db.sentiment_review.find()
        return sentiment_reviews

    def get_review_by_hotel_locid(self, hotel_id):
        sentiment_reviews = self.db.sentiment_review.find({
            'hotel_id': hotel_id
        })
        return sentiment_reviews

    def get_maxmin_years_inhotel(self, hotel_id, sort):
        sentiment_review = self.db.sentiment_review.find_one({
            '$query': {'hotel_id': hotel_id},
            '$orderby': {'year': sort}
        })
        return sentiment_review['year']

    def is_sentimented_review_exist(self, review_id):
        return True if self.db.sentiment_review.find({review_id: review_id}).count() > 0 else False

    def get_review_group_hotel_date(self, hotel_id):
        sentiment_reviews = self.db.sentiment_review.aggregate([
            {
                "$match": {
                    "hotel_id": hotel_id
                }
            }, {
                "$group": {
                    "_id": {
                        "month": "$month",
                        "year": "$year",
                    },
                    "location_id": {"$push": "$location_id"},
                    "hotel_id": {"$push": "$hotel_id"},
                    "review_id": {"$push": "$review_id"},
                    "subratings_normalized": {"$push": "$subratings_normalized"},
                    "wordnet_sentiment": {"$push": "$wordnet_sentiment"},
                    "wordnet_normalized": {"$push": "$wordnet_normalized"},
                    "vader_sentiment": {"$push": "$vader_sentiment"},
                    "count": {"$sum": 1}
                },
            }, {
                "$sort": {
                    "_id.year": 1,
                    "_id.month": 1,
                }
            }
        ])
        return sentiment_reviews

    def create(self, sentiment_review):
        try:
            result = (self.db.sentiment_review.insert_one(
                sentiment_review)).inserted_id
            print("[", datetime.now(), "] Msg: Success saving data with id ",
                  result, "to sentiment review !")
        except:
            print(
                "[", datetime.now(), "] Err: Failed to save result sentiment review !")
