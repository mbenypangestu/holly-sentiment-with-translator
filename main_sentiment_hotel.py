from translator.translator import LanguageTranslator
from database.mongo_service import MongoService
from database.solr_service import SolrService
from services.location_service import LocationService
from services.hotel_service import HotelService
from services.review_service import ReviewService
from services.review_translated_service import ReviewTranslatedService
from services.sentiment_review_service import SentimentReviewService
from services.sentiment_hotel_service import SentimentHotelService
from sentiment.sentiment import SentimentAnalyzer

from mongoengine import connect
from pymongo import MongoClient
import time
import datetime
import json
import pprint
from googletrans import Translator


class Main(MongoService):
    def __init__(self):
        super().__init__()

        self.count = 1
        self.start()

    def start(self):
        datenow = datetime.datetime.now()

        location_service = LocationService()
        hotel_service = HotelService()

        sentiment_analyzer = SentimentAnalyzer()
        sentimenthotel_service = SentimentHotelService()

        locations = location_service.get_all_locations()

        for i, location in enumerate(locations):
            hotels = hotel_service.get_hotels_by_locationid(
                location['location_id'])

            for j, hotel in enumerate(hotels):
                hotel_sentiment_score = self.calculate_sentiment_score(hotel)

                print(self.count, ".) Hotel ", hotel['name'], " :")
                pprint.pprint(hotel_sentiment_score)
                self.count += 1

                try:
                    data = {
                        "hotel": hotel,
                        "location_id": location['location_id'],
                        "hotel_id": hotel['location_id'],
                        "wordnet_hotel": hotel_sentiment_score['wordnet_hotel'],
                        "vader_neg_hotel": hotel_sentiment_score['vader_neg_hotel'],
                        "vader_pos_hotel": hotel_sentiment_score['vader_pos_hotel'],
                        "vader_neu_hotel": hotel_sentiment_score['vader_neu_hotel'],
                        "vader_compound_hotel": hotel_sentiment_score['vader_compound_hotel'],
                        "created_at": datenow
                    }
                    sentimenthotel_service.create(data)
                except Exception as err:
                    print(str("-----> Error saving data sentiment hotel !"))
                    print(str("-----> Err : ", err))
                    continue

    def calculate_sentiment_score(self, hotel, month, year):
        sentimentreview_service = SentimentReviewService()

        wordnet_hotel = 0
        vader_neg_hotel = 0
        vader_pos_hotel = 0
        vader_neu_hotel = 0
        vader_compound_hotel = 0

        sentiment_reviews = sentimentreview_service.get_review_by_hotel_locid(
            hotel['location_id'])

        for r, sentiment_review in enumerate(sentiment_reviews):
            wordnet_hotel += float(sentiment_review['wordnet_sentiment'])
            vader_neg_hotel += float(
                sentiment_review['vader_sentiment']['neg'])
            vader_pos_hotel += float(
                sentiment_review['vader_sentiment']['pos'])
            vader_neu_hotel += float(
                sentiment_review['vader_sentiment']['neu'])
            vader_compound_hotel += float(
                sentiment_review['vader_sentiment']['compound'])

        if sentiment_reviews.count() > 0:
            avg_wordnet_hotel = wordnet_hotel / sentiment_reviews.count()
            avg_vader_neg_hotel = vader_neg_hotel / sentiment_reviews.count()
            avg_vader_pos_hotel = vader_pos_hotel / sentiment_reviews.count()
            avg_vader_neu_hotel = vader_neu_hotel / sentiment_reviews.count()
            avg_vader_compound_hotel = vader_compound_hotel/sentiment_reviews.count()
        else:
            avg_wordnet_hotel = 0
            avg_vader_neg_hotel = 0
            avg_vader_pos_hotel = 0
            avg_vader_neu_hotel = 0
            avg_vader_compound_hotel = 0

        sentiment_score = {
            'wordnet_hotel': avg_wordnet_hotel,
            'vader_neg_hotel': avg_vader_neg_hotel,
            'vader_pos_hotel': avg_vader_pos_hotel,
            'vader_neu_hotel': avg_vader_neu_hotel,
            'vader_compound_hotel': avg_vader_compound_hotel,
        }

        return sentiment_score


if __name__ == "__main__":
    Main()
    # time.sleep(10000)
