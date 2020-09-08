
from flask import Flask,render_template,Markup
import flask
from summa import keywords,summarizer
import scripts.keywords as kw
import scripts.extraction as extraction
from scripts.summerrizer import averageScoringModel
from scripts.scraper import getFromUrl
from tinydb import TinyDB,Query
import uuid

app = Flask(__name__)

database= TinyDB("static/DB/graph.json")
databaseSumm= TinyDB("static/DB/summary.json")
node=TinyDB("static/DB/nodes.json")
query=Query()
def get_entity(summ, entities):
    summ_n=""
    for i in entities:
       
        if i in summ:
            
            strt=summ.index(i)
            end=strt+len(i)
            summ_n+=summ[:strt]+'<span class="tag is-danger">'+summ[strt:end]+'</span>'
            summ=summ[end:]
    return summ_n
def getnodeindex():
    nodes=node.all()
    if len(nodes)>0:
        return "idx_"+str(int(nodes[-1]["id"].split("_")[-1])+1)
    else:
        return "idx_0"

@app.route('/',methods=["GET","POST"])
def index():
    view={"flag":False}
    marked=""
    entity=[]
    wordlist=[]
    if flask.request.method=="POST":
        url= flask.request.form["url"]
        text= flask.request.form["text"]
        model= flask.request.form["model"]
        keyword_model=flask.request.form["keyword"]
        NER_model= flask.request.form["NER"]
        title=""
        if url !="":
            title,text=getFromUrl(url)
        if model=="ASM":
            summ=averageScoringModel(text)
        elif model == "textRank":
            summ=summarizer.summarize(text)
        else:
            summ=summarizer.summarize(text)

        if keyword_model =="fbng":
            wordlist=kw.frequencyKeyWords(text)
        elif keyword_model=="RAKE":
            wordlist=kw.RAKE(text)
        elif keyword_model== "textRank":
            wordlist=keywords.keywords(text)
            wordlist=wordlist.split("\n")
        else:
            wordlist=keywords.keywords(text)
            wordlist=wordlist.split("\n")
        

        view["flag"]=True
        view["status"]="Summarized "+ str(len(text.split()))+" words to " + str(len(summ.split()))
        if NER_model=="spacy":
            entity=extraction.extractNER(summ)
        elif NER_model=="flair":
            entity=extraction.flairNER(summ)
        elif NER_model=="bert":
            entity=extraction.bertNER(summ)
        else:
            entity=extraction.extractNER(summ)
        

        if url !="" and len(summ)>10 and len(entity)>2:
            idx=str(uuid.uuid4())
            f_idx=getnodeindex()
            trueidx=int(f_idx.split("_")[-1])
            node.insert({"id":f_idx,"name":title,"faveColor": "#37a32d","size":60,"role":"parent","root":""})
            for i in set(entity):
                nodeidx="idx_"+str(trueidx+1)
                if len(node.search(query.name == i))==0:
                    node.insert({"id":nodeidx,"name":i,"faveColor": "#9c2ca8","shape":"circle","size":40,"role":"child","root":f_idx})
                else:
                    nodelist=node.search(query.name == i)
                    nodeidx=nodelist[-1]["id"]
                    node.insert({"id":nodeidx,"name":i,"faveColor": "#f0d58d","shape":"rectangle","size":40,"role":"child","root":f_idx})
                    node.update({"shape":"rectangle"},query.name==i)
                    node.update({"faveColor": "#f0d58d"},query.name==i)
                database.insert({"target":nodeidx,"source": f_idx,"id":nodeidx+f_idx})
                trueidx+=1
            databaseSumm.insert({"idx":idx,"title":title,"entity":entity,"keywords":wordlist,"summary":summ,"link":url})
        marked=get_entity(summ,entity)
    return render_template("index.html",view=view,marked=Markup(marked),ner=entity,wordlist=wordlist)
@app.route('/store/',methods=["GET","POST"])
def store():
    data=databaseSumm.all()
    nodes=node.all()
    data_notes=database.all()
    kyword_args=flask.request.args.get("keywords")
    if flask.request.method == "POST":
        document= flask.request.form["document_search"]
        
        doc_words=document.split()
        for word in doc_words:
            data=[i for i in data if word in i["title"].lower()]
            nodes_w_word=[i["id"] for i in nodes if word in i["name"].lower() and i["root"]==""]
        
        nodesn=[i for i in nodes if i["id"] in nodes_w_word or i["root"] in nodes_w_word]
        nodes_idx=[i["id"] for i in nodesn]
    
        data_notesn=[i for i in data_notes if i["source"] in nodes_idx or i["target"] in nodes_idx]
        nid=[]
        for i in data_notesn:
            nid.append(i["source"])
            nid.append(i["target"])
        nodes=[i for i in nodes if i["id"] in nid or i["root"] in nid]
        nodes_idx=[i["id"] for i in nodes]
        data_notes=[i for i in data_notes if i["source"] in nodes_idx or i["target"] in nodes_idx]
    if kyword_args!=None:
        keywords=kyword_args.split(",")
        keywords=[i.strip().lower() for i in keywords if i!=""]
        nodes_w_word=[]
        for word in keywords:
            
            for i in nodes:
                 if word in i["name"].lower():
                     nodes_w_word.append(i["id"])
                     if i["root"]!="":
                        nodes_w_word.append(i["root"])
        nodesn=[i for i in nodes if i["id"] in nodes_w_word or i["root"] in nodes_w_word]
        nodes_idx=[i["id"] for i in nodesn]
        
        data_notesn=[i for i in data_notes if i["source"] in nodes_idx or i["target"] in nodes_idx]
        nid=[]
        for i in data_notesn:
            nid.append(i["source"])
            nid.append(i["target"])
        nodes=[i for i in nodes if i["id"] in nid or i["root"] in nid]
        nodes_idx=[i["id"] for i in nodes]
        data_notes=[i for i in data_notes if i["source"] in nodes_idx or i["target"] in nodes_idx]
    idxmap={i["id"]:i["name"] for i in nodes}
    parentChild={i["id"]:i["role"] for i in nodes}
    return flask.render_template("store.html",data=data,nodes=nodes,edges=data_notes,mapping=idxmap,parentChild=parentChild)

@app.route('/store/keywords',methods=["GET","POST"])
def store_keywords():
    document=""
    if flask.request.method=="POST":
        document= flask.request.form["selected"]
    return flask.redirect(flask.url_for("store",keywords=document))
if __name__ =="__main__":
	app.run()
