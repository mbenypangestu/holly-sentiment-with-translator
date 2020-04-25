import time
import requests
import os
import pandas as pd
import pprint
import datetime
from googletrans import Translator


class LanguageTranslator:
    def __init__(self):
        self.path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._base_url = "https://translate.yandex.net/api/v1.5/tr.json/translate"
        self._api_key = [
            "trnsl.1.1.20191123T042847Z.9cbe09e68450f11a.6a453d0246373470816ee73d70fa34bb7ae9d0fc",
            "trnsl.1.1.20200420T060848Z.ef746bcf34070aeb.ef62b2a31cc6277c378cd79abf3c18751b153ae9",
            "trnsl.1.1.20200420T061517Z.3503cf9c55c3ad9e.0843787448e9644fe25ea11979be714a9f1ef988",
            "trnsl.1.1.20200420T062240Z.24bdddf1badd55f6.dc2c05c68c8c90de48d9c91e1f67abb009b6e162",
            "trnsl.1.1.20200420T062545Z.4e2c53f70615e6f9.77a11488e2e699195c71e5f2c024753658d95368",
            "trnsl.1.1.20200425T145308Z.36b669a1b7b5aea9.078997a2f889b0c1232cda6d25bc97f9b570636a",
            "trnsl.1.1.20200425T150807Z.17fa0e053dece658.78a95311e1e0cce85c7aaeecd842b362cec15091",
            "trnsl.1.1.20200425T151054Z.2c8b73e25fba1497.509982b5d7e17eaa60a6d81dc5b7489c35a3d151",
            "trnsl.1.1.20200425T151206Z.704f122d666d1a5c.20cf5b0b60b99857f0015d895d3c010a2f09e8aa",
            "trnsl.1.1.20200425T151326Z.ac16722de00af3b6.ce20d649e4f2397c5c819214bc41cd61c0a55302",
        ]
        self.languages = pd.read_csv(
            self.path + "/dataset/language_standart.csv")

    def translate_yandex(self, text="", src_lang="", target_lang="en"):
        lang = target_lang

        if src_lang != "":
            selected_lang = self.languages.loc[self.languages['tripadvisor'] ==
                                               src_lang]
            if not selected_lang.empty:
                src_lang = selected_lang['yandex']
            lang = src_lang + "-" + target_lang

        for key in self._api_key:
            params = {
                'key': key,
                'lang': lang,
                'text': text
            }

            try:
                res = requests.post(self._base_url, params=params)
                res_obj = res.json()
                text_translated = res_obj['text'][0]
                return text_translated
            except Exception as err:
                print("[", datetime.datetime.now(), "] Err : ", err)
                print("[", datetime.datetime.now(),
                      "] Retrying next api key ...")
                continue

    def translate_googletrans(self, text="", src_lang="", target_lang="en"):
        gTranslator = Translator()

        text_translated = gTranslator.translate(text)
        return text_translated.text
