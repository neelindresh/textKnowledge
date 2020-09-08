import spacy
import numpy as np
import pandas as pd

import re
import sys
text=""
with open("sample.txt","r") as f:
    text=f.read()



def getskills():
    with open("../static/DB/summ.txt","r") as f:
        data=f.readlines()
    return [i.strip() for i in data]



skills=getskills()
nlp = spacy.load('en_core_web_sm')
'''
train_data_structute=[
                      (sent,
                            {"entities":
                                        [
                                            (start,end,"entname"),
                                            (start,end,"entname")
                                        ]
                            }
                        ),
                      (sent,
                            {"entities":[
                                (start,end,"entname"),
                                (start,end,"entname")
                                        ]
                            }
                        )
                      ]
'''
def create_data(text,skills):
    text=text.replace("e.g.","eg")
    text=text.replace("i.e.","ie")
    text=text.replace("P.S.","ps")
    start_ind=[]
    train_data=[]
    for sent in text.split("."):
        _temp={"entities":[]}
        flag=False
        for skill in skills:
            if skill.lower() in sent:
                
                strt=sent.lower().index(skill.lower())
                end=strt+len(skill)
                #print(sent,skill,len(sent),strt,end)
                #skill=sent[strt:].split()[0]
                if (strt==len(sent) or sent[strt-1]==" " ) and (end+1>=len(sent) or sent[end+1] ==" ") and strt not in start_ind:
                    flag= True
                    start_ind.append(strt)
                    if len(skill.split())>1:
                        fro=strt
                        for idx,brk in enumerate(skill.split()):
                            upto=fro+ len(brk)
                            '''
                            if idx==0:
                                _temp["entities"].append((fro,upto,"B-TECH"))
                            elif idx == len(skill.split())-1:
                                _temp["entities"].append((fro,upto,"L-TECH"))
                            else:
                                _temp["entities"].append((fro,upto,"I-TECH"))
                            '''
                            _temp["entities"].append((fro,upto,"TECH_"))
                            fro=upto+1
                    else:
                        skill=sent[strt:].split()[0]
                        end=strt+len(skill)
                        _temp["entities"].append((strt,end,"TECH"))
        if flag:
            #print(_temp)
            train_data.append((sent+".",_temp))
    return train_data
'''
for i in train_data[0][1]["entities"]:
    print(i)
    print(train_data[0][0][i[0]:i[1]])

print(nlp.make_doc(train_data[0][0]))
print(spacy.gold.biluo_tags_from_offsets(nlp.make_doc(train_data[0][0]), train_data[0][1]["entities"]))
'''
def model_train(train_data,entities,epochs=10,model=None,):
    if model!=None:
        nlp=spacy.load(model)
    else:
        nlp=spacy.load("en_core_web_sm")
    add_ents = ['TECH',"TECH_"] # The new entity
    # Piplines in core pretrained model are tagger, parser, ner. Create new if blank model is to be trained using `spacy.blank('en')` else get the existing one.
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner") # "architecture": "ensemble" simple_cnn ensemble, bow # https://spacy.io/api/annotation
        nlp.add_pipe(ner)
    else:
        ner = nlp.get_pipe("ner")
    prev_ents = ner.move_names # All the existing entities recognised by the model
    print('[Existing Entities] = ', ner.move_names)
    for ent in add_ents:
        ner.add_label(ent)
    
    new_ents = ner.move_names
    # print('\n[All Entities] = ', ner.move_names)
    print('\n\n[New Entities] = ', list(set(new_ents) - set(prev_ents)))
    ## Training

    # Since we are training a fresh model not a saved model
    n_iter = epochs
    print("Traing Data:" ,len(train_data))
    other_pipes=[pipe for pipe in nlp.pipe_names if pipe!="ner"]
    with nlp.disable_pipes(*other_pipes):  # only train ner
        # optimizer = nlp.begin_training()
        if model is None:
            optimizer = nlp.begin_training()
        else:
            optimizer = nlp.resume_training()
        for i in range(n_iter):
            losses = {}
            for data,annotation in train_data:
            #print("*"*50)
                #spacy.gold.biluo_tags_from_offsets(nlp.make_doc(text), annotation)
                '''
                for i in annotation["entities"]:

                    print(i)
                    print(text[i[0]:i[1]])
                print(nlp.make_doc(text))
                print(spacy.gold.biluo_tags_from_offsets(nlp.make_doc(text), annotation["entities"]))
                '''
                nlp.update([data], [annotation],  sgd=optimizer, drop=0.0, losses=losses)
                #print("*"*50)
            # nlp.entity.update(d, g)
            print("Losses", losses)
    nlp.to_disk("NERmodel")

train_data=create_data(text,skills)
print(train_data)
model_train(train_data,['TECH',"TECH_"],30,model="NERmodel")

