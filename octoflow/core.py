# AUTOGENERATED! DO NOT EDIT! File to edit: 02_text_patterns.ipynb (unless otherwise specified).

__all__ = ['split_into_sentences', 'alphabets', 'prefixes', 'suffixes', 'starters', 'acronyms', 'websites',
           'get_pubmed_records', 'get_attribute_text', 'get_segment', 'sentence_has_phrase',
           'find_sentence_in_abstract', 'replace_outof_vocab_words', 'nlp', 'extra_vocab', 'special_tokens',
           'take_while', 'partition', 'partition_all', 'n_grams', 'lemmatize', 'nlp']

# Cell

import json
import re


alphabets= "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"

def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

# Cell
import pandas as pd
from Bio import Entrez
from pydash import get

def get_pubmed_records(pmids):
    Entrez.email = "strasser.ms@gmail.com"
    # handle type is http.client.HTTPResponse
    handle = Entrez.efetch(
        db="pubmed",
        id=",".join(pmids),
        #api_key="be67e0a1be023d17fff5334a6c6f45287a08",
        rettype="xml",
        retmode="text",
    )
    records = Entrez.read(handle)
    return records

def get_attribute_text(AbstractText, NlmCategory):
    if AbstractText is None:
        return None
    for string_element in AbstractText:
        cat = ""
        try:
            #the worst API arbitrary nonsense ... 1h of my life for getting data out of it
            cat = string_element.attributes["NlmCategory"]
        except:
            None

        if cat == NlmCategory:
            return string_element

def get_segment(record, segment_label):
    if record is None:
        return None
    return str(
        get_attribute_text(
            get(record, "MedlineCitation.Article.Abstract.AbstractText"),
            segment_label
        )
    )

# Cell
import itertools
from pydash import find_index
#OLD one-off functions that need refactoring
def sentence_has_phrase(sentence, cue_phrases):
    for c in cue_phrases: #unsafe scope
        if c in sentence:
            return True
    return False

def find_sentence_in_abstract(paragraph, bias=0):
    """checks paragraph for key sentences. Returns first matching hit"""
    p_sents = split_into_sentences(paragraph)
    idx = find_index(p_sents, sentence_has_phrase)
    if idx < 0:
        return ""

    i = idx + bias #bias- for sentence before or after
    if i < 0:
        return ""
    return get(p_sents, i)

# Cell

import spacy
import en_core_web_md
with open("vocab30k.txt") as f:
    vocab30k = f.read().split("\t\n")

nlp = en_core_web_md.load()

extra_vocab = [
               "-PRON-", "-pron-", ".", ",", ";"  #lemmatizer inconsitency
]

special_tokens = {
    "(": "-lrb-",
    ")": "-rrb-"
}

def replace_outof_vocab_words(text, vocab, nlp=nlp, extra_vocab=extra_vocab, special_tokens=special_tokens):
    vocab += extra_vocab
    newtext = ""
    for token in nlp(text):
        t = token.text
        if special_tokens.get(t):
            t=special_tokens.get(t)
        elif token.lemma_.lower() not in vocab and token.tag_ is not None:
            t= "ii" + token.tag_.lower()
        newtext += t + " "

    return newtext



# Cell

def take_while(fn, coll):
    """Yield values from coll until fn is False"""
    for e in coll:
        if fn(e):
            yield e
        else:
            return

def partition(n, coll, step=None):
    return take_while(lambda e: len(e) == n,
        (coll[i:i+n] for i in range(0, len(coll), step or n)))

def partition_all(n, coll, step=None):
    return (coll[i:i+n] for i in range(0, len(coll), step or n))

def n_grams(texts, n_gram=2): return [" ".join(n) for t in texts for n in partition(n_gram, t.split(" "), 1)]

# Cell

import spacy
nlp = spacy.load("en_core_web_md")

def lemmatize(text, nlp=nlp):
    return " ".join([tok.lemma_ for tok in nlp(text)])