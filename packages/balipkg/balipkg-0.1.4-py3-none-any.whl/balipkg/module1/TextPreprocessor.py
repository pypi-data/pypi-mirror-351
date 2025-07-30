
from .balinese_lemmatization.BalineseLemmatization.Lemmatization import Lemmatization
import re
from nltk.tokenize import word_tokenize
import pandas as pd
import string
import os
import sys


ROOT_PATH_FOLDER = os.path.dirname(os.getcwd())
ROOT_PATH_MODULE_FOLDER = ROOT_PATH_FOLDER + "\\packages\\module1\\"
sys.path.append(ROOT_PATH_MODULE_FOLDER)


class TextPreprocessor:

    @staticmethod
    def remove_emoji_pattern(input_text):
        """
        Remove emojis from the input text.

        Args:
            input_text (str): The text from which to remove emojis.

        Returns:
            str: The cleaned text without emojis.
        """
        # https://en.wikipedia.org/wiki/Unicode_block
        EMOJI_PATTERN = re.compile(
            "["
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "]+"
        )
        # Replace emojis with an empty string
        cleaned_text = EMOJI_PATTERN.sub('', input_text)
        return cleaned_text

    @staticmethod
    def remove_leading_trailing_whitespace(text):
        """
        used to remove leading and trailing whitespace (spaces, tabs, newlines) from a string.

        Args:
            input_text (str): The raw input text

        Returns:
            str: The cleaned text
        """
        return text.strip()

    # remove special characters in text such as tab, enter, \r
    @staticmethod
    def remove_tab_characters(text):
        cleaned_text = text.replace('\\t', " ").replace('\\n', "").replace(
            '\\u', " ").replace('\\', "").replace('\\r', "").replace('\\x', "")
        return cleaned_text

    # case folding in text
    @staticmethod
    def case_folding(text):
        return text.lower()

    # remove special e and å characters in balinese text
    @staticmethod
    def convert_special_characters(sentences):
        list_characters = list(sentences)
        special_e_characters = ['é', 'é', 'è',
                                'é', 'é', 'é', 'é', 'é', 'ê', 'ë', 'é']
        special_i_characters = ['ì', 'í']
        special_u_characters = ['û']
        special_a_characters = ['å', 'å']
        for idx, character in enumerate(list_characters):
            if character in special_e_characters:
                list_characters[idx] = 'e'
            if character in special_a_characters:
                list_characters[idx] = 'a'
            if character in special_i_characters:
                list_characters[idx] = 'i'
            if character in special_u_characters:
                list_characters[idx] = 'u'

        return "".join(list_characters)

    @staticmethod
    def remove_special_punctuation(text):
        cleaned_text = text.replace(
            '–', '-').replace("…", " ").replace("..", ".").replace('„„', '')
        return cleaned_text

    # remove punctiation based on string.punctuation in text
    @staticmethod
    def remove_punctuation(text):
        string_punctuation = '"#$%&\'()*+/:;<=>@[\\]?!^_`{|}~,”“’‘“'
        return text.translate(str.maketrans("", "", string_punctuation)).strip()

    # remove period punctuation

    @staticmethod
    def remove_period_punctuation(text):
        text = text.replace('.', '')
        return text

    # remove multiple whitespace into single whitespace
    @staticmethod
    def remove_whitespace_multiple(text):
        return re.sub('\s+', ' ', text)

    # remove number in text 1 digit or more
    @staticmethod
    def remove_number(text):
        return re.sub(r"\d+", "", text)

    @staticmethod
    def remove_exclamation_words(text):
        kata_seruan = [
            'Prrrr.',
            'Brrr.',
            'biaaar',
            'Beh',
            'ri…ri…',
            'kwek…',
            'Ihhh…'
        ]
        for seruan in kata_seruan:
            text = text.replace(seruan, '')
        return text

    @staticmethod
    def remove_person_entities_in_text(sentences, **kwargs):
        list_of_detected_character = kwargs['characters']
        for character in list_of_detected_character:
            sentences = sentences.replace(character, '')
        sentences = sentences.replace('  ', ' ').replace(' .', '.')
        return sentences.strip()

    @staticmethod
    def remove_stop_words(text):
        # include our list of Balinese StopWords
        # Balinese Stop Word
        with open(ROOT_PATH_MODULE_FOLDER+'/balinese_stop_words/list_of_stop_words.txt', 'r') as file:
            BALINESE_STOP_WORDS = sorted(
                [term.strip().lower() for term in file.readlines()])
        BALINESE_STOP_WORDS = list(dict.fromkeys(
            BALINESE_STOP_WORDS))  # remove duplicate term

        # remove stopwords process
        tokenize_text = word_tokenize(text)
        for idx, token in enumerate(tokenize_text):
            if token.lower() in BALINESE_STOP_WORDS:
                del tokenize_text[tokenize_text.index(token)]

        return " ".join(tokenize_text)

    @staticmethod
    def normalize_words(text):
        # Balinese Normalize Words
        BALINESE_NORMALIZE_DICT = pd.read_excel(
            ROOT_PATH_MODULE_FOLDER+'/balinese_normalization_words/normalization.xlsx')
        BALINESE_NORMALIZE_WORDS = list(
            BALINESE_NORMALIZE_DICT['normalized'].str.lower())
        BALINESE_UNNORMALIZE_WORDS = list(
            BALINESE_NORMALIZE_DICT['unormalized'].str.lower())

        # normalize words process
        tokenize_text = word_tokenize(text)
        for idx, token in enumerate(tokenize_text):
            if token.lower() in BALINESE_UNNORMALIZE_WORDS:
                tokenize_text[tokenize_text.index(
                    token)] = BALINESE_NORMALIZE_WORDS[BALINESE_UNNORMALIZE_WORDS.index(token.lower())]

        return " ".join(tokenize_text)

    @staticmethod
    def remove_punctuation_except_commas(text):
        if type(text) == str:
            for char in text:
                if (char in string.punctuation) and (char != '-'):
                    text = text.replace(char, ",")
        return text

    @staticmethod
    def add_enter_after_period_punctuation(text):
        text = text.replace('.', '.\\n')
        return text

    @staticmethod
    def lemmatize_text(text):
        lemmatized_tokens = [Lemmatization().lemmatization(
            token.strip()) for token in text.split(' ')]
        return ' '.join(lemmatized_tokens)
