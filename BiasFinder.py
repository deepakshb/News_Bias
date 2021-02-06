import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from tqdm import tqdm
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from gensim.models.phrases import Phrases, Phraser
from gensim.utils import simple_preprocess

df = pd.read_csv('news.csv')
cleaned_articles = np.array([re.sub(r'[^A-Za-z ]+',' ', article.lower()) for article in df.articles])
cleaned_articles = np.unique(cleaned_articles, return_counts=False)
sentences = []

for article in tqdm(cleaned_articles):
  splitted_article = article.split()
  tokens = []
  for i in splitted_article:
    stops = set(stopwords.words('english'))
    if i not in stops:
      tokens.append(i)
  sentences.append(' '.join(tokens))

preprocessed_articles = [simple_preprocess(article,min_len=3) for article in sentences]
phrases = Phrases(preprocessed_articles, min_count=3)
bigrams = Phraser(phrases)
sentences = bigrams[preprocessed_articles]

seed_words = ['instructed','targeted','misguided','grotesque','sidelined','defendant','deteriorated','victorious',
              'heartening','rigorous','unequivocally','culmination']
w2v_model = Word2Vec(min_count=5,window=8,size=100)
w2v_model.build_vocab(sentences)
w2v_model.train(sentences, total_examples=w2v_model.corpus_count, epochs=1)
print(w2v_model.wv.most_similar(seed_words,topn=100))