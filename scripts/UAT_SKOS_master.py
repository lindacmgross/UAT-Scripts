# coding: utf-8

import os
import json
import shutil
import rdflib
import unicodedata
import pandas as pd
from datetime import datetime

print "Reading the SKOS file...this may take a few seconds."

timestamp = datetime.now().strftime("%Y_%m%d_%H%M")

##### RDF File Location #####
##### assign this variable to location of UAT SKOS-RDF file exported from VocBench ##### 
rdf = "UATv2.0.0.rdf"

##### Shared Functions and Variables #####
##### do NOT edit this section #####
##### scroll down for conversion scripts #####

#reads SKOS-RDF file into a RDFlib graph for use in these scripts
g = rdflib.Graph()
result = g.parse((rdf).encode('utf8'))

#defines certain properties within the SKOS-RDF file
prefLabel = rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#prefLabel')
broader = rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#broader')
Concept = rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#Concept')
vocstatus = rdflib.term.URIRef('http://art.uniroma2.it/ontologies/vocbench#hasStatus')
altLabel = rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#altLabel')
TopConcept = rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#topConceptOf')
ednotes = rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#editorialNote')
changenotes = rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#changeNote')
scopenotes = rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#scopeNote')
example = rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#example')
related = rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#related')

#a list of all top concepts
alltopconcepts = [bv for bv in g.subjects(predicate=TopConcept)]

#a list of all concepts
allconcepts = [gm for gm in g.subjects(rdflib.RDF.type, Concept)]

#find all terms that have the given term listed as a broader term, so they are therefore narrower terms
def getnarrowerterms(term):
    narrowerterms = {}
    terminal = rdflib.term.URIRef(term)
    try:
        for nts in g.subjects(predicate=broader, object=terminal):
            try:
                narrowerterms[terminal].append(nts)
            except KeyError:
                narrowerterms[terminal] = [nts]
        return narrowerterms[terminal]
    except KeyError:
        pass

#a function to get a list of all broader terms for a term
def getbroaderterms(term):
    terminal = rdflib.term.URIRef(term)
    broaderterms = {}
    try:
        for bts in g.objects(subject=terminal, predicate=broader):
            try:
                broaderterms[terminal].append(bts)
            except KeyError:
                broaderterms[terminal] = [bts]
        return broaderterms[terminal]
    except KeyError:
        pass

#a function to get a list of all alt terms for a term
def getaltterms(term):
    terminal = rdflib.term.URIRef(term)
    alternateterms = {}
    try:
        for ats in g.objects(subject=terminal, predicate=altLabel):
            try:
                alternateterms[terminal].append(ats)
            except KeyError:
                alternateterms[terminal] = [ats]
        return alternateterms[terminal]
    except KeyError:
        pass           

#for cco in alltopconcepts:
#    print getaltterms(cco)

#a function to get a list of all related terms for a term
def getrelatedterms(term):
    terminal = rdflib.term.URIRef(term)
    relatedterms = {}
    try:
        for rts in g.objects(subject=terminal, predicate=related):
            try:
                relatedterms[terminal].append(rts)
            except KeyError:
                relatedterms[terminal] = [rts]
        return relatedterms[terminal]
    except KeyError:
        pass  

#a function to return editorial notes for a term
def getednotes(term):
    d = rdflib.term.URIRef(term)
    for ednoteterm in g.objects(subject=d, predicate=ednotes):
        return ednoteterm

#a function to return change notes for a term
def getchangenotes(term):
    d = rdflib.term.URIRef(term)
    for chnoteterm in g.objects(subject=d, predicate=changenotes):
        return chnoteterm

#a function to return scope notes for a term
def getscopenotes(term):
    d = rdflib.term.URIRef(term)
    for scnoteterm in g.objects(subject=d, predicate=scopenotes):
        return scnoteterm

#a function to return example notes for a term
def getexample(term):
    d = rdflib.term.URIRef(term)
    for termex in g.objects(subject=d, predicate=example):
        return termex

#a function to return the status of a term    
def getvocstatus(term):
    d=rdflib.term.URIRef(term)
    for vcstatus in g.objects(subject=d, predicate=vocstatus):
        return vcstatus

#a function to return the human readable form of the prefered version of a term
def lit(term):
    d = rdflib.term.URIRef(term)
    for prefterm in g.objects(subject=d, predicate=prefLabel):
        return prefterm

#returns a list of all deprecated terms in the file
deprecated = []
for term in allconcepts:
    termstats = getvocstatus(term)
    if termstats == "Deprecated":
        deprecated.append(lit(term))


def getallchilds(term, childlist):
    childs = getnarrowerterms(term)
    if childs != None:
        for kids in childs:
            if unicode(lit(kids)) in deprecated:
                pass
            else:
                childlist.append(unicode(lit(kids)))
                getallchilds(kids, childlist)


##### Conversion Scripts #####
##### comment out scripts you don't want to run at this time #####


print "\nCreating HTML files for the web browsers..."
#execfile("UAT_SKOS_to_html.py")
#working, 1/26/2017

print "\nCreating CSV flatfile..."
#execfile("UAT_SKOS_to_flatfile.py")
#working, 1/26/2017

print "\nCreating 'related to' CSV flatfile..."
#execfile("UAT_SKOS_to_related_list.py")
#working, 1/26/2017

print "\nCreating json file for dendrogram..."
#execfile("UAT_SKOS_to_dendrogram.py")
#probably works, output file needs testing, 12/22/2015

print "\nCreating json file for dendrogram with child term nums..."
#execfile("UAT_SKOS_to_dendrogram-with-child-nums.py")
#probably works, need to test output file, 12/22/2015

print "\nCreating flat json file for all concepts API..."
#execfile("UAT_SKOS_to_json_flat_for_allconcepts_api.py")
#not working, 7/11/2016

print "\nCreating flat list csv file..."
#execfile("UAT_SKOS_to_csv_lists.py")
#working, 1/26/2017

print "\nCreating javascript for autocomplete..."
#execfile("UAT_SKOS_to_autocomplete.py")
#seems to be working, 7/11/2016

print "\nFinished with all scripts!"