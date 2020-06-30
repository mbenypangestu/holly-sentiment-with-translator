import requests
import json
from datetime import datetime
from time import sleep

from mongoengine import connect
from pymongo import MongoClient

from database.mongo_service import MongoService


class HotelService(MongoService):
    def __init__(self):
        super().__init__()

    def get_all_hotels(self):
        hotels = self.db.hotel.find()
        return hotels

    def get_by_hotellocationid(self, location_id):
        hotel = self.db.hotel.find_one(
            {'location_id': location_id})
        return hotel

    def get_hotels_by_locationid(self, location_id):
        hotels = self.db.hotel.find(
            {'locationID': location_id}, no_cursor_timeout=True)
        return hotels

    def is_hotel_exist(self, hotel_id):
        hotel = self.db.hotel.find({'id': hotel_id})
        if hotel.count() > 0:
            return True
        else:
            return False
