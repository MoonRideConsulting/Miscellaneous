import streamlit as st

import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
from collections import Counter
import pandas as pd

def fetch_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()
    return text

def generate_wordcloud(text):
    wordcloud = WordCloud().generate(text)
    return wordcloud

import nltk
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('stopwords')

def get_top_ngrams(text, n, k):
    words = nltk.word_tokenize(text)
    words = [word.lower() for word in words if word.isalpha() and word.lower() not in stopwords.words('english')]
    ngrams = nltk.ngrams(words, n)
    ngram_freq = nltk.FreqDist(ngrams)
    return ngram_freq.most_common(k)

import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from gensim import corpora

def preprocess(text):
    result = []
    for token in simple_preprocess(text):
        if token not in STOPWORDS and len(token) > 3:
            result.append(token)
    return result

def generate_topic_model(text):
    data = [preprocess(text)]
    dictionary = corpora.Dictionary(data)
    corpus = [dictionary.doc2bow(text) for text in data]
    lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,
                                                id2word=dictionary,
                                                num_topics=5,
                                                random_state=100,
                                                update_every=1,
                                                chunksize=100,
                                                passes=10,
                                                alpha='auto',
                                                per_word_topics=True)
    return lda_model

st.title("Text Analytics App")

option = st.radio("Select an option:", ("Enter raw text", "Enter URL"))

if option == "Enter raw text":
    text = st.text_area("Enter some text:")
    if text:
        wordcloud = generate_wordcloud(text)
        st.image(wordcloud.to_array(), use_column_width=True)
        
        from textblob import TextBlob
        
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        
        if sentiment > 0:
            st.write("The sentiment of the text is positive.")
        elif sentiment < 0:
            st.write("The sentiment of the text is negative.")
        else:
            st.write("The sentiment of the text is neutral.")
        st.header("Sentiment Analysis")
        st.write("The sentiment analysis score is:", sentiment)
        st.write("The sentiment analysis score ranges from -1 to 1, where -1 is the most negative sentiment and 1 is the most positive sentiment. A score of 0 indicates a neutral sentiment.")
        st.header("Subjectivity Analysis")
        st.write("The subjectivity score is:", blob.sentiment.subjectivity)
        st.write("The subjectivity score ranges from 0 to 1, where 0 is the most objective and 1 is the most subjective. A score of 0 indicates a very objective text, while a score of 1 indicates a very subjective text.")
        
        st.header("Top Ngrams")
        n = st.slider("Select the number of grams:", 1, 5, 2)
        k = st.slider("Select the number of top ngrams to display:", 1, 20, 10)
        top_ngrams = get_top_ngrams(text, n, k)
        st.write(f"Top {k} {n}-grams:")
        for ngram, count in top_ngrams:
            st.write(f"{ngram}: {count}")
        
        st.header("Topic Modeling")
        lda_model = generate_topic_model(text)
        topics = lda_model.show_topics(num_topics=5, num_words=10, formatted=False)
        for i, topic in enumerate(topics):
            st.write(f"Topic {i+1}:")
            for word, prob in topic[1]:
                st.write(f"{word} ({prob:.2f})")
                
elif option == "Enter URL":
    url = st.text_input("Enter a URL:")
    if url:
        text = fetch_url(url)
        wordcloud = generate_wordcloud(text)
        st.image(wordcloud.to_array(), use_column_width=True)
        
        from textblob import TextBlob
        
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        
        if sentiment > 0:
            st.write("The sentiment of the text is positive.")
        elif sentiment < 0:
            st.write("The sentiment of the text is negative.")
        else:
            st.write("The sentiment of the text is neutral.")
        st.header("Sentiment Analysis")
        st.write("The sentiment analysis score is:", sentiment)
        st.write("The sentiment analysis score ranges from -1 to 1, where -1 is the most negative sentiment and 1 is the most positive sentiment. A score of 0 indicates a neutral sentiment.")
        st.header("Subjectivity Analysis")
        st.write("The subjectivity score is:", blob.sentiment.subjectivity)
        st.write("The subjectivity score ranges from 0 to 1, where 0 is the most objective and 1 is the most subjective. A score of 0 indicates a very objective text, while a score of 1 indicates a very subjective text.")
        
        st.header("Top Ngrams")
        n = st.slider("Select the number of grams:", 1, 5, 2)
        k = st.slider("Select the number of top ngrams to display:", 1, 20, 10)
        top_ngrams = get_top_ngrams(text, n, k)
        st.write(f"Top {k} {n}-grams:")
        for ngram, count in top_ngrams:
            st.write(f"{ngram}: {count}")
        
        st.header("Topic Modeling")
        lda_model = generate_topic_model(text)
        topics = lda_model.show_topics(num_topics=5, num_words=10, formatted=False)
        for i, topic in enumerate(topics):
            st.write(f"Topic {i+1}:")
            for word, prob in topic[1]:
                st.write(f"{word} ({prob:.2f})")
