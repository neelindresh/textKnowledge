import nltk 
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize, sent_tokenize 

stopWords = set(stopwords.words("english"))

def averageScoringModel(text):
	words = word_tokenize(text)
	
	freq_tab={}
	
	for word in words:
		word=word.lower()
		if word in stopWords:
			continue
		if word in freq_tab:
			freq_tab[word]+=1
		else:
			freq_tab[word]=1

	sentences = sent_tokenize(text)
	sentDict={}

	for sentence in sentences:
		for word,freq in freq_tab.items():
			if word in sentence.lower():
				if sentence in sentDict:
					sentDict[sentence]+=1
				else:
					sentDict[sentence]=1

	totalValues=0
	for k,v in sentDict.items():
		totalValues+=v

	average=int(totalValues/len(sentDict))


	summary = '' 

	for sentence in sentences: 
		if (sentence in sentDict) and (sentDict[sentence] > (1.2 * average)): 
			summary += " " + sentence 
	return summary
#print(averageScoringModel(text))

