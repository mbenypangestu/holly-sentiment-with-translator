
import requests
import json
from datetime import datetime
from time import sleep

from mongoengine import connect
from pymongo import MongoClient

from database.mongo_service import MongoService


class TemporalDataService(MongoService):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

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

    def get_by_hotel_date(self, hotel_id, year, month):
        temporal_data = self.db.temporal_data.find_one({
            'hotel_id': hotel_id, "year": year,  "month": month,
        })
        return temporal_data

    def isexist_temporal_data_by_hotel_date(self, hotel_id, year, month):
        temporal_data = self.get_by_hotel_date(hotel_id, year, month)
        if temporal_data != None:
            return True
        else:
            return False

    def create(self, temporal_data):
        try:
            result = self.db.temporal_data.insert_one(temporal_data)
            print("[", self.now, "] Msg: Success saving data temporal_data hotel !")
        except Exception as err:
            print(
                "[", self.now, "] Err: Failed to save result temporal_data hotel !")
            print(
                "[", self.now, "]", err)

    def update_byid(self, id_temporal_data, data_update):
        try:
            result = self.db.temporal_data.update_one({
                '_id': id_temporal_data
            }, {
                "$set": data_update
            })
            print("[", self.now, "] Msg: Success updating temporal_data hotel !")
        except Exception as err:
            print(
                "[", self.now, "] Err: Failed to update result temporal_data hotel !")
            print(
                "[", self.now, "]", err)
