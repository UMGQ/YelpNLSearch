import sys
import os
import collections
import json
import lucene
from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexReader
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser

class Searcher(object):
    def __init__(self, path):
        print "Loading data.json..."
        #with open(path, "r") as f:
        #    self.data = json.load(f)
        lucene.initVM()
        self.analyzer = StandardAnalyzer(Version.LUCENE_4_10_1)
        self.reader = IndexReader.open(SimpleFSDirectory(File("index/")))
        self.searcher = IndexSearcher(self.reader)

    def process_query(self, query, filters):
        print "Processing query:", query
        search_results = self.searching(query)
        results = self.filtering(search_results, filters)
        return search_results

    def searching(self, query):
        print "Searching:", query
        query = QueryParser(Version.LUCENE_4_10_1, "text", self.analyzer).parse(query)
        MAX = 5
        hits = self.searcher.search(query, MAX)
        results = []
        for hit in hits.scoreDocs:
            doc = self.searcher.doc(hit.doc)
            results.append([doc.get("name"), hit.score])

        results = sorted(results, key=lambda x : x[1], reverse=True)
        # return map(lambda x : x[0], results)
        return results

    def filtering(self, search_results, filters):
        pass
