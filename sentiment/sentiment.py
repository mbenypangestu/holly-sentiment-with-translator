from time import sleep
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import sentiwordnet as swn, stopwords, wordnet
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import nltk
import pandas as pd
import re

nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('sentiwordnet')


class SentimentAnalyzer:
    def __init__(self):
        self.sentimentAnalyzer = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

    def preprocess_text(self, text):
        # Special Character Filtering
        text_char_filter = self.specialchar_filtering_text(text)
        # To lower case
        text_lower = self.to_lowercase_text(text_char_filter)
        # Tokenized
        tokenized = self.tokenize_text(text_lower)

        result = tokenized
        return result

    def specialchar_filtering_text(self, text):
        print("\n======================== Special Char Filtering =========================")
        result = " ".join(re.findall("[a-zA-Z]+", text))
        print(result)
        return result

    def to_lowercase_text(self, text):
        print("\n======================== Data case folding =========================")
        result = text.lower()
        print(result)
        return result

    def tokenize_text(self, text):
        print("\n======================== Data tokenized =========================")
        result = nltk.pos_tag(word_tokenize(text))
        print(result)
        return result

    def lemmatize_text(self, text, pos_tag):
        result = self.lemmatizer.lemmatize(text, pos_tag)
        # print(result)
        return result

    def get_wordnet_pos_tag(self, tag):
        tag_dict = {
            "J": wordnet.ADJ,
            "N": wordnet.NOUN,
            "V": wordnet.VERB,
            "R": wordnet.ADV,
        }

        return tag_dict.get(tag, wordnet.NOUN)

    def get_vader(self, text):
        return self.sentimentAnalyzer.polarity_scores(text)

    def get_sentiwordnet(self, text):
        pos_temp = 0
        neg_temp = 0
        obj_temp = 0

        result = 0
        total = 0

        text_preprocessed = self.preprocess_text(text)

        for word in text_preprocessed:
            if word[0] not in self.stop_words:
                pos_tag = self.get_wordnet_pos_tag(word[1][0])
                print(
                    "\n======================== Data lemmatized =========================")
                print(word[0], "  ", word[1][0], "  ", pos_tag)
                lemmatized = self.lemmatize_text(word[0], pos_tag)

                try:
                    synset = swn.senti_synset(
                        '{0}.{1}.03'.format(lemmatized, pos_tag))
                except:
                    continue

                print("Pos : ", synset.pos_score())
                print("Neg : ", synset.neg_score())
                print("Obj : ", synset.obj_score())

                pos_temp += synset.pos_score()
                neg_temp += synset.neg_score()
                obj_temp += synset.obj_score()

        print("\n Result : ")
        print(pos_temp, " - ", neg_temp, " - ", obj_temp)
        print(" Pos - Neg = ", pos_temp - neg_temp)

        pos_wordnet = 0
        neg_wordnet = 0

        total_wordnet = pos_temp + neg_temp + obj_temp

        if total_wordnet != 0:
            pos_wordnet = (pos_temp + obj_temp) / total_wordnet
            neg_wordnet = (neg_temp + obj_temp) / total_wordnet

        result = (pos_wordnet + neg_wordnet) * 0.5 / 2

        print("Total Pos : ", pos_wordnet)
        print("Total Neg : ", neg_wordnet)
        print(result)

        return result


if __name__ == "__main__":
    sentimentAnalyzer = SentimentAnalyzer()
    # Good
    # score = sentimentAnalyzer.get_sentiwordnet(
    #     "Great Hampton Inn.  Great Location.  Great People.  Good breakfast.  Clean and comfortable .   Easy to get to from the airports.  Has not shown any wear from the time built. The room was comfortable and clean")

    # Bad
    score = sentimentAnalyzer.get_sentiwordnet(
        "I booked this hotel tonight (april 11,2019) under my company reservation for two nights. Once, I arrived your front office staff said no reservation for us (Andi and Ega). They said that no room at all. Your marketing for my company (KPPU) said the same 'No'. They do nothing, do not make an effort for double check. I said that your hotel staff had confirm to Ms.Xenia this noon, but they still refusing us So, we force to search another hotel at 18.38 tonight. What a bad reservation system you had. It is so impossible for me do check in at the hotel without the reservation. And I have no word of apologize at all from your hotel staff Bad.. Very bad indeed.")
