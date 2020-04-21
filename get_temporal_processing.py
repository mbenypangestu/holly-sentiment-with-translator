from database.mongo_service import MongoService
from database.solr_service import SolrService
from services.location_service import LocationService
from services.hotel_service import HotelService
from services.review_service import ReviewService
from services.review_translated_service import ReviewTranslatedService
from services.sentiment_review_service import SentimentReviewService
from services.temporal_data_service import TemporalDataService
from sentiment.sentiment import SentimentAnalyzer

from mongoengine import connect
from pymongo import MongoClient
import time
from datetime import datetime
import json
import pprint
from googletrans import Translator

import copy


class TemporalProcessing(MongoService):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def __init__(self):
        super().__init__()
        self.temporaldata_service = TemporalDataService()
        self.sentimentreview_service = SentimentReviewService()
        self.hotel_service = HotelService()
        self.count = 1
        # self.start()

        test_hotel = self.hotel_service.get_by_hotellocationid("582990")
        self.calculate_sentiment_score(test_hotel)

    def start(self):
        location_service = LocationService()

        locations = location_service.get_locations_indonesia()

        for i, location in enumerate(locations):
            hotels = self.hotel_service.get_hotels_by_locationid(
                location['location_id'])

            for j, hotel in enumerate(hotels):
                print(self.count, "---------------------------------------------------------} ",
                      hotel['name'])
                self.calculate_sentiment_score(hotel)
                self.count += 1
            #     break
            # break

    def calculate_sentiment_score(self, hotel):
        datenow = datetime.now()

        sentiment_reviews = list(self.sentimentreview_service.get_review_group_hotel_date(
            hotel['location_id']))

        data_temp = None
        i = 0
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

            for s, subrating in enumerate(sentiment_review['subratings_normalized']):
                rating_rooms += subrating['rooms']
                rating_value += subrating['value']
                rating_sleep_quality += subrating['sleep_quality']
                rating_location += subrating['location']
                rating_cleanliness += subrating['cleanliness']
                rating_service += subrating['service']

            for v, vader in enumerate(sentiment_review['vader_sentiment']):
                vader_neg_hotel += vader['neg']
                vader_pos_hotel += vader['pos']
                vader_neu_hotel += vader['neu']
                vader_compound_hotel += vader['compound']

            for w, wordnet in enumerate(sentiment_review['wordnet_normalized']):
                wordnet_hotel += wordnet

            rating_rooms /= len(
                sentiment_review['subratings_normalized'])
            rating_value /= len(
                sentiment_review['subratings_normalized'])
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

            wordnet_hotel /= len(sentiment_review['wordnet_normalized'])

            print("\nITERASI ", i, "\n")

            now_value_month = sentiment_review['_id']['month']
            now_value_year = sentiment_review['_id']['year']

            try:
                next_value_month = sentiment_reviews[r+1]['_id']['month']
                next_value_year = sentiment_reviews[r+1]['_id']['year']
            except:
                next_value_month = datenow.month + 1
                next_value_year = datenow.year

            for year in range(now_value_year, next_value_year+1):
                for month in range(now_value_month, 13):
                    if next_value_month <= month and year == next_value_year:
                        print("Break month 1")
                        break

                    print("\nPERIODE :", month, "/", year)
                    print("-> next :", next_value_month,
                          "/", next_value_year)

                    if sentiment_review['_id']['month'] == month and sentiment_review['_id']['year'] == year:
                        print("--------------------------------> Changing")
                        data = {
                            "hotel_id": hotel['location_id'],
                            "month": month,
                            "year": year,
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
                            "cluster": 0,
                            "error_rate ": 0,
                            "created_at": datenow
                        }

                    data_temp = copy.deepcopy(data)
                    data_temp['month'] = month
                    data_temp['year'] = year

                    self.store_temporaldata(
                        data_temp, sentiment_review, hotel, year, month)

                    if month == datenow.month and year == datenow.year:
                        print("Break")
                        break

                now_value_month = 1
                if year == next_value_year:
                    print("Break year")
                    break

            i += 1

    def store_temporaldata(self, data_temp, sentiment_review, hotel, year, month):
        hotel_bydate = self.temporaldata_service.get_by_hotel_date(
            hotel['location_id'], year, month)

        if hotel_bydate == None:
            print("[", self.now, "]---> ", self.count, ".) Hotel ", hotel['name'], " : ",
                  sentiment_review['_id']['month'], "-", sentiment_review['_id']['year'])
            self.temporaldata_service.create(data_temp)
        else:
            print(
                "[", self.now, "]---> Data temporal hotel is already exist !")
            self.temporaldata_service.update_byid(
                hotel_bydate['_id'], data_temp)


if __name__ == "__main__":
    TemporalProcessing()
    # time.sleep(10000)
