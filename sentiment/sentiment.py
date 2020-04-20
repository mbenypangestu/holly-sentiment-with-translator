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

    def get_wordnet_degree(self, word):
        pos_tag = self.get_wordnet_pos_tag(word[1][0])
        # print(word[0], "  ", word[1][0], "  ", pos_tag)

        lemmatized = self.lemmatize_text(word[0], pos_tag)
        synset = swn.senti_synset('{0}.{1}.03'.format(lemmatized, pos_tag))

        return {
            'positive': synset.pos_score(),
            'negative': synset.neg_score(),
            'objective': synset.obj_score()
        }

    def get_wordnet_aggregation(self, pos, neg, obj):
        pos_wordnet = 0
        neg_wordnet = 0
        result = 0

        if pos > neg:
            pos_wordnet = pos / (pos + neg)
            result = pos_wordnet - (obj * pos_wordnet)
        elif pos < neg:
            neg_wordnet = neg / (pos + neg) * -1
            result = neg_wordnet - (obj * neg_wordnet)
        else:
            result = 0

        return result

    def get_sentiwordnet(self, text):
        sentences_result = 0
        total = 0

        text_preprocessed = self.preprocess_text(text)

        word_count = 0
        for word in text_preprocessed:
            if word[0] not in self.stop_words:
                try:
                    degree = self.get_wordnet_degree(word)
                    result = self.get_wordnet_aggregation(
                        degree['positive'], degree['negative'], degree['objective'])
                    # print("Result = ", result)

                    if result != None:
                        word_count += 1

                    sentences_result += result
                except:
                    continue

        print("Word count : ", word_count)
        sentences_result = sentences_result / word_count

        print("Sentences result = ", sentences_result)
        return result


if __name__ == "__main__":
    sentimentAnalyzer = SentimentAnalyzer()
    # Good
    score = sentimentAnalyzer.get_sentiwordnet(
        "Great Hampton Inn.  Great Location.  Great People.  Good breakfast.  Clean and comfortable .   Easy to get to from the airports.  Has not shown any wear from the time built. The room was comfortable and clean")

    # Bad
    # score = sentimentAnalyzer.get_sentiwordnet(
    #     "I booked this hotel tonight (april 11,2019) under my company reservation for two nights. Once, I arrived your front office staff said no reservation for us (Andi and Ega). They said that no room at all. Your marketing for my company (KPPU) said the same 'No'. They do nothing, do not make an effort for double check. I said that your hotel staff had confirm to Ms.Xenia this noon, but they still refusing us So, we force to search another hotel at 18.38 tonight. What a bad reservation system you had. It is so impossible for me do check in at the hotel without the reservation. And I have no word of apologize at all from your hotel staff Bad.. Very bad indeed.")
