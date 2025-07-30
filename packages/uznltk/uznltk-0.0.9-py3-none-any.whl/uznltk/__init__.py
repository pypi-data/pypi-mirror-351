from ._tokenizer import split_sentences, split_words
from ._stop_words import stop_words_list, clear_stopword
from ._download import download_resources, book_download, news_download, numbers_download
from ._lemmatizer import lemmatize
from ._stem import stem_word
from ._clean import clean_text, solid_sign
from ._syllable import syllables, hyphenation, count

# # Faqat funksiyalarni eksport qilamiz
# __all__ = [
#     'stop_word',
#     'clean_stop_words',
#     'lemmatize',
#     'stem_word',
#     'clean_text',
#     'solid_sign',
#     'syllables',
#     'book', 'news', 'hyphenation', 'count', 'count_text', 'split_sentences', 'split_words'
# ]