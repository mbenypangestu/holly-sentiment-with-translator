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


class BaseVar:
    rating_rooms = 0
    rating_value = 0
    rating_sleep_quality = 0
    rating_location = 0
    rating_cleanliness = 0
    rating_service = 0

    len_rooms = 0
    len_value = 0
    len_sleep_quality = 0
    len_location = 0
    len_cleanliness = 0
    len_service = 0

    wordnet_hotel = 0

    vader_neg_hotel = 0
    vader_pos_hotel = 0
    vader_neu_hotel = 0
    vader_compound_hotel = 0


class TemporalProcessing(MongoService):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def __init__(self):
        super().__init__()
        self.temporaldata_service = TemporalDataService()
        self.sentimentreview_service = SentimentReviewService()
        self.hotel_service = HotelService()
        self.count = 1
        self.start()

    def start(self):
        location_service = LocationService()

        locations = location_service.get3_indonesia()

        for i, location in enumerate(locations):
            print("\n ", location['name'])
            hotels = self.hotel_service.get_hotels_by_locationid(
                location['location_id'])

            for j, hotel in enumerate(hotels):
                print("[", self.now, "]", j+1, ") ",
                      hotel['location_id'], " - ", hotel['name'])
                self.calculate_sentiment_score(hotel)
                self.count += 1
                j += 1

    def calculate_sentiment_score(self, hotel):
        datenow = datetime.now()

        sentiment_reviews = list(self.sentimentreview_service.get_review_group_hotel_date(
            hotel['location_id']))

        data_temp = None
        i = 0
        for r, sentiment_review in enumerate(sentiment_reviews):
            base_var = BaseVar()

            self.get_subratings(base_var, sentiment_review)
            self.get_vader_wordnet(base_var, sentiment_review)
            self.count_rating_review(base_var, sentiment_review)

            print("\n[", self.now, "] ITERATION ", i)
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
                        print("\n[", self.now, "] Break month 1")
                        break

                    print("\n[", self.now, "] PERIOD :",
                          month, "/", year)
                    print("[", self.now, "] --> next :", next_value_month,
                          "/", next_value_year)

                    if sentiment_review['_id']['month'] == month and sentiment_review['_id']['year'] == year:
                        print("[", self.now, "] -----------------> Changing")
                        data = self.is_data_change_inmonth(
                            base_var, sentiment_review, hotel, year, month)

                    data_temp = copy.deepcopy(data)
                    data_temp['month'] = month
                    data_temp['year'] = year

                    data_temp = self.is_from_last_month(data_temp, year, month)

                    self.store_temporaldata(
                        data_temp, sentiment_review, hotel, year, month)

                    if month == datenow.month and year == datenow.year:
                        print("\n[", self.now, "] BREAK")
                        break

                now_value_month = 1
                if year == next_value_year:
                    print("[", self.now, "] Break Year")
                    break

            i += 1

    def store_temporaldata(self, data_temp, sentiment_review, hotel, year, month):
        hotel_bydate = self.temporaldata_service.get_by_hotel_date(
            hotel['location_id'], year, month)

        if hotel_bydate == None:
            print("[", self.now, "]", self.count, ".) Hotel ", hotel['name'], " : ",
                  sentiment_review['_id']['month'], "-", sentiment_review['_id']['year'])
            self.temporaldata_service.create(data_temp)
        else:
            print(
                "[", self.now, "] Data temporal hotel is already exist !")
            self.temporaldata_service.update_byid(
                hotel_bydate['_id'], data_temp)

    def is_from_last_month(self, data_temp, year, month):
        last_month = month - 1
        last_year = year
        if month == 1:
            last_month = 12
            last_year = year - 1

        data_last_month = self.temporaldata_service.get_by_hotel_date(
            data_temp['hotel_id'], last_year, last_month)
        # pprint.pprint(data_last_month)

        if data_last_month != None:
            if data_temp['rating_rooms'] == 0:
                data_temp['rating_rooms'] = data_last_month['rating_rooms']
            if data_temp['rating_cleanliness'] == 0:
                data_temp['rating_cleanliness'] = data_last_month['rating_rooms']
            if data_temp['rating_location'] == 0:
                data_temp['rating_location'] = data_last_month['rating_location']
            if data_temp['rating_service'] == 0:
                data_temp['rating_service'] = data_last_month['rating_service']
            if data_temp['rating_sleep_quality'] == 0:
                data_temp['rating_sleep_quality'] = data_last_month['rating_sleep_quality']
            if data_temp['rating_value'] == 0:
                data_temp['rating_value'] = data_last_month['rating_value']

        return data_temp

    def get_subratings(self, base_var, sentiment_review):
        for s, subrating in enumerate(sentiment_review['subratings_normalized']):
            if subrating['rooms'] > 0:
                base_var.rating_rooms += subrating['rooms']
                base_var.len_rooms += 1

            if subrating['value'] > 0:
                base_var.rating_value += subrating['value']
                base_var.len_value += 1

            if subrating['sleep_quality'] > 0:
                base_var.rating_sleep_quality += subrating['sleep_quality']
                base_var.len_sleep_quality += 1

            if subrating['location'] > 0:
                base_var.rating_location += subrating['location']
                base_var.len_location += 1

            if subrating['cleanliness'] > 0:
                base_var.rating_cleanliness += subrating['cleanliness']
                base_var.len_cleanliness += 1

            if subrating['service'] > 0:
                base_var.rating_service += subrating['service']
                base_var.len_service += 1

    def get_vader_wordnet(self, base_var, sentiment_review):
        for v, vader in enumerate(sentiment_review['vader_sentiment']):
            base_var.vader_neg_hotel += vader['neg']
            base_var.vader_pos_hotel += vader['pos']
            base_var.vader_neu_hotel += vader['neu']
            base_var.vader_compound_hotel += vader['compound']

        for w, wordnet in enumerate(sentiment_review['wordnet_normalized']):
            base_var.wordnet_hotel += wordnet

    def count_rating_review(self, base_var, sentiment_review):
        if base_var.len_rooms > 0:
            base_var.rating_rooms /= base_var.len_rooms
        if base_var.len_value > 0:
            base_var.rating_value /= base_var.len_value
        if base_var.len_sleep_quality > 0:
            base_var.rating_sleep_quality /= base_var.len_sleep_quality
        if base_var.len_location > 0:
            base_var.rating_location /= base_var.len_location
        if base_var.len_cleanliness > 0:
            base_var.rating_cleanliness /= base_var.len_cleanliness
        if base_var.len_service > 0:
            base_var.rating_service /= base_var.len_service

        base_var.vader_neg_hotel /= len(
            sentiment_review['vader_sentiment'])
        base_var.vader_pos_hotel /= len(
            sentiment_review['vader_sentiment'])
        base_var.vader_neu_hotel /= len(
            sentiment_review['vader_sentiment'])
        base_var.vader_compound_hotel /= len(
            sentiment_review['vader_sentiment'])

        base_var.wordnet_hotel /= len(
            sentiment_review['wordnet_normalized'])

    def is_data_change_inmonth(self, base_var, sentiment_review, hotel, year, month):
        return {
            "hotel_id": hotel['location_id'],
            "month": month,
            "year": year,
            "location_id": sentiment_review['location_id'][0],
            "hotel": hotel,
            "rating_rooms": base_var.rating_rooms,
            "rating_value": base_var.rating_value,
            "rating_sleep_quality": base_var.rating_sleep_quality,
            "rating_location": base_var.rating_location,
            "rating_cleanliness": base_var.rating_cleanliness,
            "rating_service": base_var.rating_service,
            "wordnet_score": base_var.wordnet_hotel,
            "vader_neg_score": base_var.vader_neg_hotel,
            "vader_pos_score": base_var.vader_pos_hotel,
            "vader_neu_score": base_var.vader_neu_hotel,
            "vader_compound_score": base_var.vader_compound_hotel,
            "cluster": 0,
            "created_at": self.now
        }


if __name__ == "__main__":
    TemporalProcessing()
    # time.sleep(10000)
