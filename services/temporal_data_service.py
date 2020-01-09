
import requests
import json
from datetime import datetime
from time import sleep

from mongoengine import connect
from pymongo import MongoClient

from database.mongo_service import MongoService


class TemporalDataService(MongoService):
    def __init__(self):
        super().__init__()

    def get_all_temporal_datas(self):
        temporal_datas = self.db.temporal_data.find()
        return temporal_datas

    def get_temporal_data_by_hotel_locid(self, hotel_id):
        temporal_datas = self.db.temporal_data.find({
            'hotel_id': hotel_id
        })
        return temporal_datas

    def isexist_temporal_data_by_hotel_date(self, hotel_id, year, month):
        temporal_datas = self.db.temporal_data.find({
            'hotel_id': hotel_id, "year": year,  "month": month,
        })

        print(temporal_datas.count())

        if temporal_datas.count() > 0:
            return True
        else:
            return False

    def create(self, temporal_data):
        try:
            result = (self.db.temporal_data.insert_one(
                temporal_data)).inserted_id
            print("Msg: Success saving data with id ",
                  result, "to temporal_data hotel !")
        except:
            print("Err: Failed to save result temporal_data hotel !")
