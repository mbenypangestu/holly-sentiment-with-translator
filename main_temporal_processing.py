from translator.translator import LanguageTranslator
from database.mongo_service import MongoService
from database.solr_service import SolrService
from services.location_service import LocationService
from services.hotel_service import HotelService
from services.review_service import ReviewService
from services.review_translated_service import ReviewTranslatedService
from services.sentiment_review_service import SentimentReviewService
from services.sentiment_hotel_service import TemporalDataService
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
        location_service = LocationService()
        hotel_service = HotelService()

        locations = location_service.get_all_locations()

        for i, location in enumerate(locations):
            hotels = hotel_service.get_hotels_by_locationid(
                location['location_id'])

            for j, hotel in enumerate(hotels):
                self.calculate_sentiment_score(hotel)

                break
            break

    def calculate_sentiment_score(self, hotel):
        datenow = datetime.datetime.now()

        temporaldata_service = TemporalDataService()
        sentimentreview_service = SentimentReviewService()
        sentiment_reviews = sentimentreview_service.get_review_group_hotel_date(
            hotel['location_id'])

        for r, sentiment_review in enumerate(sentiment_reviews):
            rating_rooms = 0
            rating_value = 0
            rating_sleep_quality = 0
            rating_location = 0
            rating_cleanliness = 0
            rating_service = 0

            wordnet_hotel = 0

            vader_neg_hotel = 0
            vader_pos_hotel = 0
            vader_neu_hotel = 0
            vader_compound_hotel = 0

            try:
                for s, subrating in enumerate(sentiment_review['subratings_normalized']):
                    rating_rooms += subrating['rooms']
                    rating_value += subrating['value']
                    rating_sleep_quality += subrating['sleep_quality']
                    rating_location += subrating['location']
                    rating_cleanliness += subrating['cleanliness']
                    rating_service += subrating['service']

                for s, vader in enumerate(sentiment_review['vader_sentiment']):
                    vader_neg_hotel += vader['neg']
                    vader_pos_hotel += vader['pos']
                    vader_neu_hotel += vader['neu']
                    vader_compound_hotel += vader['compound']

                for s, wordnet in enumerate(sentiment_review['wordnet_sentiment']):
                    wordnet_hotel += wordnet

                rating_rooms /= len(sentiment_review['subratings_normalized'])
                rating_value /= len(sentiment_review['subratings_normalized'])
                rating_sleep_quality /= len(
                    sentiment_review['subratings_normalized'])
                rating_location /= len(
                    sentiment_review['subratings_normalized'])
                rating_cleanliness /= len(
                    sentiment_review['subratings_normalized'])
                rating_service /= len(
                    sentiment_review['subratings_normalized'])

                vader_neg_hotel /= len(sentiment_review['vader_sentiment'])
                vader_pos_hotel /= len(sentiment_review['vader_sentiment'])
                vader_neu_hotel /= len(sentiment_review['vader_sentiment'])
                vader_compound_hotel /= len(
                    sentiment_review['vader_sentiment'])

                wordnet_hotel /= len(sentiment_review['wordnet_sentiment'])

                data = {
                    "hotel_id": sentiment_review['_id']['hotel_id'],
                    "month": sentiment_review['_id']['month'],
                    "year": sentiment_review['_id']['year'],
                    "location_id": sentiment_review['location_id'][0],
                    "hotel": hotel,
                    "rating_rooms": rating_rooms,
                    "rating_value": rating_value,
                    "rating_sleep_quality": rating_sleep_quality,
                    "rating_location": rating_location,
                    "rating_cleanliness": rating_cleanliness,
                    "rating_service": rating_service,
                    "wordnet_score": wordnet_hotel,
                    "vader_neg_score": vader_neg_hotel,
                    "vader_pos_score": vader_pos_hotel,
                    "vader_neu_score": vader_neu_hotel,
                    "vader_compound_score": vader_compound_hotel,
                    "created_at": datenow
                }
                print(self.count, ".) Hotel ", hotel['name'], " : ",
                      sentiment_review['_id']['month'], "-", sentiment_review['_id']['year'])
                temporaldata_service.create(data)

                self.count += 1
            except Exception as err:
                print(str("-----> Error saving data sentiment hotel !"))
                print(str("-----> Err : ", err))
                continue


if __name__ == "__main__":
    Main()
    # time.sleep(10000)
