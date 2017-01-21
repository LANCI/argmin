
# coding: utf-8

# # Ann2nx
# 
# Convertit les fichiers "ann" du corpus annoté de Stab & Gurevych en un fichier networkx

# In[10]:

import networkx
import zipfile
import re


# In[20]:

annfiles = re.compile("brat-project/essay[0-9]+.ann$")
rawdata = []
with zipfile.ZipFile("ArgumentAnnotatedEssays-1.0/brat-project.zip", "r") as f:
    for i in list(filter(annfiles.match,f.namelist())):
        ann = f.read(i).decode()
        txt = f.read(i[:-3]+"txt").decode()
        rawdata += [(ann,txt)]


# In[22]:

G = networkx.DiGraph()


# In[54]:

def filterType(t, letter):
    f = filter(None, t)
    return filter(lambda x: x[0]==letter, f)


# In[55]:

def get_whole_sentence(txt, start, end):
    bound = re.compile("[.!?]+")
    pre = bound.split(txt[:start])[-1].lstrip()
    post = bound.split(txt[end:])[0].rstrip()
    return pre + txt[start:end] + post


# In[26]:

def indicators(ann, txt, start, end):
    sent = get_whole_sentence(txt, start, end)
    
    markers = []
    na = 0
    ns = 0
    
    # Markers of support
    for i in "because therefore after for since when assuming so accordingly thus hence then consequently".split():
        if i in sent.lower():
            markers += [i]
            ns += 1
    
    #Markers of attack
    for i in "however but though except not never no whereas nonetheless yet despite".split():
        if i in sent.lower():
            markers += [i]
            na +=1
    
    if ns-na == 0:
        polarity = "none" if len(markers) == 0 else "neutral"
    elif ns > na:
        polarity = "support"
    elif na > ns:
        polarity = "against"
    
    return {"indicators": " ".join(markers), 
            "sentence": sent,
            "num_support": ns,
            "num_against": na,
            "polarity": polarity}


# In[94]:

def addnodes(ann, txt, num):
    global G
    for ln in filterType(ann.split("\n"), "T"):
        s = ln.split()
        name = s[0]
        node_type = s[1]
        start, end = map(int, s[2:4])
        text = " ".join(s[4:])
        extra_attrs = indicators(ann, txt, start, end)
        
        G.add_node("Arg%02d_%s" % (num, name),
                   type = node_type,
                   text = text,
                   start = start,
                   end = end,
                   essay = num,
                   **extra_attrs)


# In[91]:

def addstances(ann, num):
    global G
    for ln in filterType(ann.split("\n"), "A"):
        s = ln.split()
        stance = s[1].lower()
        node_name = s[2]
        stance_type = s[3].lower()
        G.node["Arg%02d_%s" % (num, node_name)][stance] = stance_type


# In[80]:

def addedges(ann, num):
    global G
    for ln in filterType(ann.split("\n"), "R"):
        s = ln.split()
        n1 = re.search(r"Arg1:(\w+)\b",s[2]).group(1)
        n2 = re.search(r"Arg2:(\w+)\b",s[3]).group(1)
        G.add_edge("Arg%02d_%s" % (num, n1), "Arg%02d_%s" % (num, n2), {"edge_type": s[1]})


# In[92]:

G = networkx.DiGraph()
n = 1
for ann, txt in rawdata:
    addnodes(ann, txt, n)
    addstances(ann, n)
    addedges(ann, n)
    n += 1


# In[106]:

networkx.write_gpickle(G,"corpus.gpickle")

