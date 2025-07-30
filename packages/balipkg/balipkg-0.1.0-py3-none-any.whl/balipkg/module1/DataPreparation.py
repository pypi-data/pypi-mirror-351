import pandas as pd
from balinese_library import POS_tag
from TextPreprocessor import *
import numpy as np


class DataPreparation:

    def __init__(self):
        pass

    def data_preprocessing(self, raw_df_text):
        """
        Function for preprocessing text data

        Args:
            - raw_df_text: raw input text in dataframe format which contain two important columns (story_title, story_text)

        Output:
            - Cleaned text in dataframe format
        """
        # preprocessing title
        raw_df_text['story_title'] = raw_df_text['story_title'].apply(
            TextPreprocessor.convert_special_characters)
        raw_df_text['story_title'] = raw_df_text['story_title'].apply(
            TextPreprocessor.case_folding)
        raw_df_text['story_title'] = raw_df_text['story_title'].apply(
            lambda x: "_".join(x.split(' ')))

        # preprocessing text
        raw_df_text['story_text'] = raw_df_text['story_text'].apply(
            TextPreprocessor.convert_special_characters)
        raw_df_text['story_text'] = raw_df_text['story_text'].apply(
            TextPreprocessor.normalize_words)
        raw_df_text['story_text'] = raw_df_text['story_text'].apply(
            TextPreprocessor.remove_tab_characters)
        raw_df_text['story_text'] = raw_df_text['story_text'].apply(
            TextPreprocessor.remove_special_punctuation)
        raw_df_text['story_text'] = raw_df_text['story_text'].apply(
            TextPreprocessor.remove_punctuation)
        raw_df_text['story_text'] = raw_df_text['story_text'].apply(
            TextPreprocessor.remove_exclamation_words)
        raw_df_text['story_text'] = raw_df_text['story_text'].apply(
            TextPreprocessor.add_enter_after_period_punctuation)
        raw_df_text['story_text'] = raw_df_text['story_text'].apply(
            TextPreprocessor.remove_leading_trailing_whitespace)
        raw_df_text['story_text'] = raw_df_text['story_text'].apply(
            TextPreprocessor.remove_whitespace_multiple)

        return raw_df_text

    def __dataframe_creation_ner_tagset(self, cleaned_df_text):
        """
        Function for creating ner tagset in DataFrame format
        """
        data = list()
        idx_sentences = 0
        for idx_story, story in cleaned_df_text.iterrows():
            story_text = story['story_text']
            for sentence in story_text.split('\\n'):
                sentence_id = 'Sentence: '+str(idx_sentences)
                words = TextPreprocessor.remove_whitespace_multiple(
                    sentence.strip()).split(' ')
                if not (len(words) == 1 and words[0] == ''):
                    for word in words:
                        pos_tag_word = POS_tag.pos_tag(
                            word).replace('\n', '').split('/')[1]
                        data.append([
                            story['story_title'], sentence_id, word, pos_tag_word, ''
                        ])
                idx_sentences += 1
        # convert to dataframe
        df_nertagset = pd.DataFrame(
            data, columns=['StoryTitle', 'sentence', 'Word', 'POS', 'Tag'])
        return df_nertagset

    def format_ner_tagset(self, raw_df_text):
        """
        Function for formatting your raw Balinese story text into dataframe for training ner model

        Args:
            - raw_df_text: raw input text in dataframe format which contain two important columns (story_title, story_text)

        Output:
            - Formatted dataset in DataFrame which contain four important column:
                - StoryTitle: Your Story Title
                - sentence: Sentence ID
                - Word: Your token from splitted sentence
                - POS: Part-of-speech label using POS Tagger from Balinese_library
                - Tag: Character NER Tagset column that will remain empty
        """
        # preprocessing input data
        cleaned_df_text = self.data_preprocessing(raw_df_text)

        # dataframe creation
        df_ner_tagset = self.__dataframe_creation_ner_tagset(cleaned_df_text)

        return df_ner_tagset

    def __dataframe_creation_chars_identification(self, cleaned_df_text):
        dictionaries = dict()
        for story_id, story in cleaned_df_text.iterrows():
            story_text = story['story_text'].split('\\n')
            story_text.pop()

            data = {
                'id_sentence': [],
                'focus_sentences': [],
                'number_of_ground_truth_chars': [],
                'ground_truth_chars': [],
                'number_of_predicted_chars': [],
                'predicted_chars': []

            }
            # split text story by sentence
            for idx_sentence, sentence in enumerate(story_text):
                # append into dataframe
                data['id_sentence'].append(idx_sentence)
                data['focus_sentences'].append(sentence)
                data['number_of_ground_truth_chars'].append(0)  # by default 0
                data['ground_truth_chars'].append(np.nan)
                data['number_of_predicted_chars'].append(0)  # by default 0
                data['predicted_chars'].append(np.nan)

            dictionaries[story['story_title']] = pd.DataFrame(data)
        return dictionaries

    def format_character_identification_dataset(self, raw_df_text):
        """
        Function for formatting your raw Balinese story text into dataframe as ground truth dataset for character identification task

        Args:
            - raw_df_text: raw input text in dataframe format which contain two important columns (story_title, story_text)

        Output:
            - Formatted dataset in dictionary of Dataframe (dictionary's key is story_title) which contain four important column in each Dataframe:
                - id_sentence: sentence ID
                - focus_sentences: corresponding sentence of current sentence ID
                - number_of_ground_truth_chars: number of ground truth characters in current sentence. By default is 0 and you must annotate manually here.
                - ground_truth_chars: ground truth of character names separated by ';'. By default is NaN and you must annotate manually here
                - number_of_predicted_chars: number of predicted characters by supervised model. By default is 0 and you must use any model to predict the number of character of certain sentence here
                - predicted_chars: predicted of character names from supervised model separated by ';'. By default is NaN and you must predict manually here.
        """
        # data preprocessing
        cleaned_df_text = self.data_preprocessing(raw_df_text)

        # formatting
        df_chars_identification = self.__dataframe_creation_chars_identification(
            cleaned_df_text)

        return df_chars_identification
