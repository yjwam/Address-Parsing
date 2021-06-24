##############################################################################################
##########################        !!!!!!!!!IMPORTANT!!!!!!!!!!        ########################
########################## install these before running               ########################
########################## 1. pip install nltk                        ########################
########################## 2. nltk.download('english')                ########################
########################## 3. pip install spacy                       ########################
########################## 4. pip install wordfreq                    ########################
########################## 5. python -m spacy download en_core_web_sm ########################
##############################################################################################


from bs4 import BeautifulSoup
import pathlib
import re
from nltk.corpus import stopwords
import nltk
import spacy
from wordfreq import top_n_list
from wordfreq import zipf_frequency

stop_words = list(set(stopwords.words('english')))
nlp = spacy.load('en_core_web_sm')
space_gained = 0
space_input = 0

def removepos(s,pos,a):
    for i in s:
        doc = nlp(i)
        poslist = [token.text for token in doc if token.pos_ == pos and token.dep_ == 'ROOT']
        i_s = re.split(' ',i)
        for j in i_s:
            if j in ['',' ']:
                i_s.remove(j)
        if len(poslist) > 0 and len(i_s) > a:
            s.remove(i)
    return s

def removesentence(S,words):
    for s in S:
        i_up = re.split(' ',s.upper())
        for j in words:
            j = j.upper()
            if j in i_up and s in S:
                S.remove(s)               
    return S


for x in range(10):
    filename = str(x) + ".html"
    file = pathlib.Path('input/' + filename)
    if (file.exists()):
        
        #Read each file
        f = open('input/' + filename, 'r', errors="ignore")
        contents = f.read()   
        
        #Removeing html tags
        soup = BeautifulSoup(contents, 'lxml')        
        output = soup.get_text()
        
##############################################################################################
########## Step 1: Removing text from tags which can't contain any address ###################
##############################################################################################
        
        tag_list=['h1','head','img','noscript','label','nav','iframe','input','a']
        for tag in soup.find_all(tag_list):
            tag.decompose()
        output = soup.get_text()
        
        #split data with \n or | or ,  (In list of strings)
        S = re.split('\n|,', output)

##############################################################################################
############## Step 2: Removing strings with verb, adjective which contain ###################
##############          more than one word using pos from spacy            ###################
##############################################################################################
        
        S = removepos(S,'VERB',1)
        S = removepos(S,'ADJ',1)

##############################################################################################
################### Step 3: Removing sentence containing stop words ##########################
##############################################################################################
        
        word = ['is','are','to', 'or','has','for','who','the']
        stop_words = [w for w in stop_words if len(w) > 3]
        words = word + stop_words
        S = removesentence(S,words)

##############################################################################################
######### CAUTION: Will give better score. Might result in some loss             #############
######### Optional Step: Removing words which are common in english with len > 3 #############
##############################################################################################
        
        #for i in S:
        #    i_s = re.split(' ',i)
        #    for j in i_s:
        #        if zipf_frequency(j.lower(),'en') > 5.28 and len(j) > 3 and i in S and nlp(j)[0].pos_ != 'NUM':
        #            S.remove(i)
                    
##############################################################################################
########## Step 4: Removing labels such as time, Product, event, work_of_art etc. ############
##############################################################################################

        for i in S:
            doc = nlp(i)
            for d in doc.ents:
                if d.label_ in ['EVENT','WORK_OF_ART',
                                 'LAW','LANGUAGE','TIME'
                                 ,'MONEY','PERCENT','QUANTITY','ORDINAL'] and i in S:
                    S.remove(i)  
                    

            
##############################################################################################
###################### Step 5: Removing names (staring with titles) ##########################
##############################################################################################

        title = ['Mr.','Ms.','Dr.','Sr.','Jr.','Er.','Mrs.']
        S = removesentence(S,title)
        
        
        output = '\n'.join(S)
        output = re.sub('\n+', ' ', output)   #Removing multiple "\n"
        output = re.sub(' +', ' ', output)    #Removing multiple " "
        
        #Write the output variable contents to output/ folder.
        fw = open('output/' + filename, "w")
        fw.write(output)
        fw.close()
        f.close()
        
        #Calculate space savings
        space_input = space_input + len(contents)
        space_gained = space_gained + len(contents) - len(output)
        
print("Total Space Gained = " + str(round(space_gained*100/space_input, 2)) + "%") 