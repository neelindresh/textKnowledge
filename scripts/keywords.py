import pandas as pd
import sklearn
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer 
import nltk
import  re
import numpy as np

stopwords= set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer() 


#rint(stopwords)
def clean(text,lower=False,stop_words=False,sp_char=True):
    if lower:
        text=text.lower()
    if sp_char:
        text=re.sub("[^A-Za-z- ]+"," ",text)
    if stop_words:
        text = text.split()
        st_text=[]
        for i in text:
            if i in stopwords:
                continue
            i=lemmatizer.lemmatize(i)
            st_text.append(i)
        text=" ".join(st_text)
    return text
def sort(orders):
    sort_orders = sorted(orders.items(), key=lambda x: x[1], reverse=True)
    return sort_orders

def defrequent(freq,bigrams):
    flist=[]
    [flist.extend(list(i[0])) for i in bigrams]
    new_frequency=[]
    for i in freq:
        if i in flist:
            continue
        new_frequency.append(i)
    return new_frequency
def getFreq(wordlist):
    fruqency={}
    for i in wordlist:
        if i in fruqency:
            fruqency[i]+=1
        else:
            fruqency[i]=1
    return fruqency
def frequencyKeyWords(text):
    text=clean(text,lower=True, stop_words=True)
    fruqency={}
    bifreq={}
    trifreq={}
    for i in text.split():
        if i in fruqency:
            fruqency[i]+=1
        else:
            fruqency[i]=1

    frequency={k:v for k,v in fruqency.items() if v>1}
    frequency=sort(fruqency)
    frequency = [i[0] for i in frequency if i[1]>1]


    bigrm = list(nltk.bigrams(text.split()))
    for i in bigrm:
        if i in bifreq:
            bifreq[i]+=1
        else:
            bifreq[i]=1
    bifreq={k:v for k,v in bifreq.items() if v>1}
    bifreq=sort(bifreq)
    frequency=defrequent(frequency,bifreq)
    bifreq=[i[0][0]+" " +i[0][1] for i in bifreq]


    trigrams = list(nltk.trigrams(text.split()))
    
    for i in trigrams:
        if i in trifreq:
            trifreq[i]+=1
        else:
            trifreq[i]=1
    trifreq={k:v for k,v in trifreq.items() if v>1}
    trifreq=[" ".join(list(i)) for i in trifreq]
    return frequency+bifreq+trifreq

def rake_key_phrase(wordlist):
    key_phrases=[]
    keywords=[]
    _temp=[]
    for i in wordlist:
        if i in stopwords or "." in i or "," in i:
            if len(_temp)>0:
                key_phrases.append(" ".join(_temp))
                _temp=[]
        else:
            _temp.append(i)
            keywords.append(i)
        
    if len(_temp)>0:
        key_phrases.append(" ".join(_temp))
                
    return key_phrases,keywords
def getDegree(coor,freq):
    new_dict={}
    for i in coor:
        new_dict[i]=coor[i]/freq[i]
    return new_dict
def degree_of_co_occurance(key_phrases,keywords):
    keywords=list(set(keywords))
    word_dict={}
    for word in keywords:
        for phrase in key_phrases:
            if word in phrase:
                if word in word_dict:
                    word_dict[word]+=len(phrase.split())
                else:
                    word_dict[word]=len(phrase.split())
    return word_dict
def RAKE(text):
    key_phrase,keywords=rake_key_phrase(text.split())
    coor=degree_of_co_occurance(key_phrase,keywords)
    freq=getFreq(keywords)
    degree=getDegree(coor,freq)
    phrase_dict={}
    final_total_dregree=[]
    for phrase in key_phrase:
        total_dregree=0
        for word in phrase.split():
            total_dregree+=degree[word]
        phrase_dict[phrase]=total_dregree
        final_total_dregree.append(total_dregree)
    phrase_dict=sort(phrase_dict)
    
    return [i[0] for i in phrase_dict[:40] ]
