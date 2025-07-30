from .balinese_lemmatization.Lemmatization import Lemmatization
import re
from .utils import load_balinese_lemmatization_file, load_balinese_normalization_dict, load_balinese_stop_words
from nltk.tokenize import word_tokenize
import pandas as pd
import string


class TextPreprocessor:
    # Initialize the data only once when the class is loaded
    # This prevents reloading the file for every function call
    _BALINESE_STOP_WORDS = None
    _BALINESE_NORMALIZE_DICT = None
    _BALINESE_VOCAB = None

    @classmethod
    def _initialize_data(cls):
        if cls._BALINESE_STOP_WORDS is None:
            cls._BALINESE_STOP_WORDS = load_balinese_stop_words()
        if cls._BALINESE_NORMALIZE_DICT is None:
            cls._BALINESE_NORMALIZE_DICT = load_balinese_normalization_dict()
        if cls._BALINESE_VOCAB is None:
            cls._BALINESE_VOCAB = load_balinese_lemmatization_file()

    def __init__(self):
        # Call the initialization method to load data if not already loaded
        TextPreprocessor._initialize_data()

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
    def remove_tab_characters(text):
        cleaned_text = text.replace('\\t', " ").replace('\\n', "").replace(
            '\\u', " ").replace('\\', "").replace('\\r', "").replace('\\x', "")
        return cleaned_text

    # case folding in text
    def case_folding(text):
        return text.lower()

    # remove special e and å characters in balinese text
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

    def remove_special_punctuation(text):
        cleaned_text = text.replace(
            '–', '-').replace("…", " ").replace("..", ".").replace('„„', '')
        return cleaned_text

    # remove punctiation based on string.punctuation in text
    def remove_punctuation(text):
        string_punctuation = '"#$%&\'()*+/:;<=>@[\\]?!^_`{|}~,”“’‘“'
        return text.translate(str.maketrans("", "", string_punctuation)).strip()

    # remove period punctuation

    def remove_period_punctuation(text):
        text = text.replace('.', '')
        return text

    # remove multiple whitespace into single whitespace
    def remove_whitespace_multiple(text):
        return re.sub('\s+', ' ', text)

    # remove number in text 1 digit or more
    def remove_number(text):
        return re.sub(r"\d+", "", text)

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

    def remove_person_entities_in_text(sentences, **kwargs):
        list_of_detected_character = kwargs['characters']
        for character in list_of_detected_character:
            sentences = sentences.replace(character, '')
        sentences = sentences.replace('  ', ' ').replace(' .', '.')
        return sentences.strip()

    def remove_stop_words(text):
        BALINESE_STOP_WORDS = TextPreprocessor._BALINESE_STOP_WORDS
        # remove stopwords process
        tokenize_text = word_tokenize(text)
        for idx, token in enumerate(tokenize_text):
            if token.lower() in BALINESE_STOP_WORDS:
                del tokenize_text[tokenize_text.index(token)]

        return " ".join(tokenize_text)

    def normalize_words(text):
        # Balinese Normalize Words
        BALINESE_NORMALIZE_WORDS = TextPreprocessor._BALINESE_NORMALIZE_DICT['normalized']
        BALINESE_UNNORMALIZE_WORDS = TextPreprocessor._BALINESE_NORMALIZE_DICT['unnormalized']

        # normalize words process
        tokenize_text = word_tokenize(text)
        for idx, token in enumerate(tokenize_text):
            if token.lower() in BALINESE_UNNORMALIZE_WORDS:
                tokenize_text[tokenize_text.index(
                    token)] = BALINESE_NORMALIZE_WORDS[BALINESE_UNNORMALIZE_WORDS.index(token.lower())]

        return " ".join(tokenize_text)

    def remove_punctuation_except_commas(text):
        if type(text) == str:
            for char in text:
                if (char in string.punctuation) and (char != '-'):
                    text = text.replace(char, ",")
        return text

    def add_enter_after_period_punctuation(text):
        text = text.replace('.', '.\\n')
        return text

    def lemmatize_text(text):
        BALINESE_VOCABS = TextPreprocessor._BALINESE_VOCAB
        lemmatized_tokens = [Lemmatization(BALINESE_VOCABS).lemmatization(
            token.strip()) for token in text.split(' ')]
        return ' '.join(lemmatized_tokens)
