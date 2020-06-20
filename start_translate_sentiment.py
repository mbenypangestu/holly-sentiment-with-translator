from translator.translator import LanguageTranslator
from database.mongo_service import MongoService
from database.solr_service import SolrService
from services.location_service import LocationService
from services.hotel_service import HotelService
from services.review_service import ReviewService
from services.sentiment_review_service import SentimentReviewService
from services.review_translated_service import ReviewTranslatedService
from sentiment.sentiment import SentimentAnalyzer
from translator.translator import LanguageTranslator

from mongoengine import connect
from pymongo import MongoClient
import time
from datetime import datetime
import dateutil
import json
import pprint
from googletrans import Translator


class SentimentAggregation(MongoService):
    def __init__(self):
        super().__init__()
        self.start()

    def start(self):
        datenow = datetime.now()

        sentimentreview_service = SentimentReviewService()
        sentiment_analyzer = SentimentAnalyzer()

        location_service = LocationService()
        hotel_service = HotelService()
        reviewtranslated_service = ReviewTranslatedService()
        review_service = ReviewService()

        language_translator = LanguageTranslator()

        locations = location_service.get_spesific_loc_indonesia()

        for i, location in enumerate(locations):
            hotels = hotel_service.get_hotels_by_locationid(
                location['location_id'])

            for j, hotel in enumerate(hotels):
                sentimentreviews_on_hotel = sentimentreview_service.get_review_by_hotel_locid(
                    hotel['location_id'])

                with self.client.start_session() as session:
                    reviews = review_service.get_review_by_hotel_locationid(
                        hotel['location_id'])
                    print(reviews.count())

                    if reviews.count() > 0:
                        print(
                            "[", datetime.now(), "] Data reviews on this hotel is available ...")

                        if sentimentreviews_on_hotel.count() == reviews.count():
                            print(
                                "[", datetime.now(), "] Complete saving this hotel's review  ...")
                        else:
                            for r, review in enumerate(self.db.review.find(
                                    {'location_id': hotel['location_id']}, no_cursor_timeout=True, session=session)):
                                try:
                                    isexist_review = any(x['review_id'] == review['id']
                                                         for x in sentimentreviews_on_hotel)
                                    if not isexist_review:
                                        print("\n[", datetime.now(),
                                              "] Next review .....")

                                        text_translated = review['text']
                                        if review['lang'] != "en":
                                            text_translated = language_translator.translate_yandex(
                                                review['text'])
                                            print("[", datetime.now(), "] Review :",
                                                  review['text'])
                                            print(
                                                "[", datetime.now(), "] Review translated :", text_translated)

                                        text_to_sentiment = text_translated

                                        vader = sentiment_analyzer.get_vader(
                                            text_to_sentiment)
                                        wordnet = sentiment_analyzer.get_sentiwordnet(
                                            text_to_sentiment)

                                        subratings = self.map_subratings(
                                            review)
                                        subratings_normalized = self.normalize_subratings(
                                            subratings)

                                        date_publish = dateutil.parser.parse(
                                            review['published_date'])

                                        data = {
                                            "hotel": hotel,
                                            "publish_date": review['published_date'],
                                            "month": date_publish.month,
                                            "year": date_publish.year,
                                            "location_id": location['location_id'],
                                            "hotel_id": hotel['location_id'],
                                            "review_id": review['id'],
                                            "subratings": subratings,
                                            "subratings_normalized": subratings_normalized,
                                            "text_review": review['text'],
                                            "text_to_sentiment": text_to_sentiment,
                                            "vader_sentiment": vader,
                                            "wordnet_sentiment": wordnet,
                                            "wordnet_normalized": (wordnet - (-1)) / 2,
                                            "created_at": datenow
                                        }
                                        # pprint.pprint(data)

                                        sentimentreview_service.create(data)
                                    else:
                                        print("[", datetime.now(), "] Review (",
                                              review['id'], ") on table Sentiment Review is already exist")

                                except Exception as err:
                                    print("[", datetime.now(), "]  Err : ", err)
                                    continue

                                # time.sleep(1)
                                # self.client.admin.command(
                                #     'refreshSessions', [session.session_id], session=session)
                            # reviews.close()

                    else:
                        print(
                            "[", datetime.now(), "] This hotel's review is empty ...")

        # hotels.close()
        # Break Hotel
        # break
        # locations.close()
        # Break location
        # break

    def translate(self, text_to_translate):
        text_translated = self.translate_yandex(
            text_to_translate)

    def map_subratings(self, review_translated):
        subratings = review_translated['subratings']

        mapped_subratings = {
            'rooms': 0,
            'value': 0,
            'sleep_quality': 0,
            'location': 0,
            'cleanliness': 0,
            'service': 0
        }

        if len(subratings) > 0:
            for i, subrate in enumerate(subratings):
                if subrate['name'] == "Rooms":
                    mapped_subratings.update(
                        {'rooms': subrate['value']})
                elif subrate['name'] == "Value":
                    mapped_subratings.update(
                        {'value': subrate['value']})
                elif subrate['name'] == "Sleep Quality":
                    mapped_subratings.update(
                        {'sleep_quality': subrate['value']})
                elif subrate['name'] == "Location":
                    mapped_subratings.update(
                        {'location': subrate['value']})
                elif subrate['name'] == "Cleanliness":
                    mapped_subratings.update(
                        {'cleanliness': subrate['value']})
                elif subrate['name'] == "Service":
                    mapped_subratings.update(
                        {'service': subrate['value']})

        return mapped_subratings

    def normalize_subratings(self, subratings):
        normalize_subrating = subratings.copy()

        normalize_subrating.update(
            {'rooms': float(normalize_subrating['rooms']) / 5})
        normalize_subrating.update(
            {'value': float(normalize_subrating['value']) / 5})
        normalize_subrating.update(
            {'sleep_quality': float(normalize_subrating['sleep_quality']) / 5})
        normalize_subrating.update(
            {'location': float(normalize_subrating['location']) / 5})
        normalize_subrating.update(
            {'cleanliness': float(normalize_subrating['cleanliness']) / 5})
        normalize_subrating.update(
            {'service': float(normalize_subrating['service']) / 5})

        return normalize_subrating

    def store_sentiment(self, reviews):
        language_translator = LanguageTranslator()
        sentiment_analyzer = SentimentAnalyzer()
        sentiment_service = SentimentReviewService()

        for i, review in enumerate(reviews):
            text_to_translate = review['text']
            text_translated = language_translator.translate(text_to_translate)
            vader = sentiment_analyzer.get_vader(text_translated)
            wordnet = sentiment_analyzer.get_sentiwordnet(text_translated)

            data = {
                "location_id": review['hotel_detail']['locationID'],
                "location_object_id": review['hotel_detail']['locationObjectID'],
                "hotel_location_id": review['hotel_locationID'],
                "hotel_location_object_id": review['hotel_ObjectId'],
                "text_to_translate": text_to_translate,
                "text_translated": text_translated,
                "vader_sentiment": vader,
                "wordnet_sentiment": wordnet,
                "created_at": datetime.datetime.now()
            }
            sentiment_service.create(data)


if __name__ == "__main__":
    SentimentAggregation()
    # time.sleep(10000)
