import pandas as pd
import numpy as np
import re
from nltk.corpus import stopwords
from tqdm import tqdm
from gensim.models import Word2Vec
from gensim.models.phrases import Phrases, Phraser
from gensim.utils import simple_preprocess
from tabulate import tabulate
from scraper import TOIScraper
import os.path

class BiasWordsFinder:

  def __init__(self):
    self.model = None
    self.seed_words = None
    self.results = None

  def load_and_clean_articles(self):
    # Read CSV file made using scraper.py in a dataframe
    df = pd.read_csv('news.csv')
    # Remove special characters and numbers from the dataset and convert to lowercase
    cleaned_articles = np.array([re.sub(r'[^A-Za-z ]+',' ', article.lower()) for article in df.articles])
    # Ignore if there are any duplicates
    cleaned_articles = np.unique(cleaned_articles, return_counts=False)
    #sentences = []

    print('Cleaning dataset...')
    # Remove stopwords
    sentences =[' '.join([i for i in article.split() if i not in stopwords.words('english') and i != ' '])
                for article in tqdm(cleaned_articles)]
    return sentences

  def tokenize_and_generate_phrases(self):
    # Tokenize news articles, ignore tokens with small length
    preprocessed_articles = [simple_preprocess(article,min_len=3) for article in self.load_and_clean_articles()]

    # Extract phrases
    phrases = Phrases(preprocessed_articles, min_count=3)
    bigrams = Phraser(phrases)
    sentences = bigrams[preprocessed_articles]
    return sentences

  def train_word2Vec(self):
    sentences = self.tokenize_and_generate_phrases()

    # Prepare and train Word2Vec model. Include words whose occurance is more than 5.
    w2v_model = Word2Vec(min_count=3, window=8, size=100)
    print('Preparing Vocabulary...')
    w2v_model.build_vocab(sentences)
    print('Training Word2Vec model...(min_count = 3, Window = 8, size = 100)')
    w2v_model.train(sentences, total_examples=w2v_model.corpus_count, epochs=1)
    self.model = w2v_model

  def make_result_dataframe(self):
    self.seed_words = ['instructed','targeted','misguided','sidelined','defendant','victorious',
                       'rigorous','unequivocally','heartening','deteriorated']

    # Get embedding for each seed word
    self.results = np.array([[i for i in self.model.wv.most_similar(word,topn=100)] for word in self.seed_words])
    self.results = self.results.transpose(0,2,1).reshape(-1,100)

  def display_results(self):
    # Display results interactively
    choice = True
    while choice:
      print(tabulate([['1. instructed', '2. targeted', '3. misguided'], ['4. sidelined', '5. defendant', '6. victorious'],
                  ['7. rigorous', '8.unequivocally','9. heartening'],['10. deteriorated','0. exit']]))
      num_seed = input('\nFor which of the about would you like to see similar words (Enter number)? ')
      if int(num_seed) == 0:
        break
      index_in_results = (int(num_seed) - 1) * 2

      print(tabulate({'Word': self.results[index_in_results],
                    'Cosine similarity': self.results[index_in_results + 1]}, headers="keys", tablefmt="psql"))

      more_input = input("Would you like to see more (Yes: 1, No: 0)?")
      choice = bool(int(more_input))


if __name__ == '__main__':
    file_available = os.path.exists('news.csv')

    if file_available ==False:
        obj_scraper = TOIScraper("https://timesofindia.indiatimes.com/")
        obj_scraper.scrape_news_articles()

    # Clean articles and train Word2Vec model. Then display the results.
    obj_bias = BiasWordsFinder()
    obj_bias.train_word2Vec()
    obj_bias.make_result_dataframe()
    obj_bias.display_results()