import  spacy
import string
from flair.data import Sentence
from flair.models import SequenceTagger
from segtok.segmenter import split_single
from transformers import AutoModelForTokenClassification, AutoTokenizer
import torch
model = AutoModelForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
label_list = ["O",       # Outside of a named entity
     "B-MISC",  # Beginning of a miscellaneous entity right after another miscellaneous entity
     "I-MISC",  # Miscellaneous entity
     "B-PER",   # Beginning of a person's name right after another person's name
     "I-PER",   # Person's name
     "B-ORG",   # Beginning of an organisation right after another organisation
     "I-ORG",   # Organisation
     "B-LOC",   # Beginning of a location right after another location
    "I-LOC"   ] # Location ]

nlp= spacy.load("en_core_web_md")
tagger = SequenceTagger.load('ner')
def extractNER(text):
    doc=nlp(text)
    entities=["ORG","PERSON","FAC","WORK_OF_ART"]
    maked=[]
    for token in doc.ents:
        if token.label_ in entities:
            info=(token.label_,token.text)
            maked.append(token.text)
    return maked
def flairNER(text):
    # make a sentence
    #sentence = Sentence(text)

    # load the NER tagger
    
    sentences = [Sentence(sent, use_tokenizer=True) for sent in split_single(text)]
    # run NER over sentence
    tagger.predict(sentences)
# print the entities with below command
    entities=[]
    for sent in sentences:
        for entity in sent.get_spans('ner'):
            entities.append(entity.text)
    return entities
def bertNER(sequences):
    final_toks=[]
    for sequence in sequences.split("."):
        print(sequence)
    # Bit of a hack to get the tokens with the special tokens
        tokens = tokenizer.tokenize(tokenizer.decode(tokenizer.encode(sequence)))
        inputs = tokenizer.encode(sequence, return_tensors="pt")
        outputs = model(inputs)[0]
        predictions = torch.argmax(outputs, dim=2)

        alltokens=[(token, label_list[prediction]) for token, prediction in zip(tokens, predictions[0].numpy()) if label_list[prediction]!="O"]
        prev=""
        all_toks=[]
        for i in alltokens:
            data=i[0]
            if i[0].startswith("##"):
                data=prev+data[2:]
                prev = data
                continue
            
            if prev != "" and prev not in all_toks:all_toks.append(prev)
            if data in sequence.split() and data not in all_toks:
                all_toks.append(data)
            prev=data
        if len(alltokens)>0 and alltokens[-1][0]!= prev:
            all_toks.append(prev)
        final_toks.extend(all_toks)
    return final_toks
def get_hotwords(text):
    result = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN',"VERB"] # 1
    doc = nlp(text.lower()) # 2
    for token in doc:
        # 3
        if(token.text in nlp.Defaults.stop_words or token.text in string.punctuation):
            continue
        # 4
        if(token.pos_ in pos_tag):
            #print(token.pos_)
            result.append(token.text)
                
    return result 