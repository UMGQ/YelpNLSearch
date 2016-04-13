import sys
import os
import collections
import json
import lucene
from distance import distance
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
        with open(path, "r") as f:
            self.data = json.load(f)
        lucene.initVM()
        self.analyzer = StandardAnalyzer(Version.LUCENE_4_10_1)
        self.reader = IndexReader.open(SimpleFSDirectory(File("index/")))
        self.searcher = IndexSearcher(self.reader)

    def process_query(self, query, filters):
        print "Processing query:", query
        search_results = self.searching(query)
        results = self.filtering(search_results, filters)
        return results

    def searching(self, query):
        print "Searching:", query
        query = QueryParser(Version.LUCENE_4_10_1, "text", self.analyzer).parse(query)
        MAX = 5
        hits = self.searcher.search(query, MAX)
        results = []
        for hit in hits.scoreDocs:
            doc = self.searcher.doc(hit.doc)
            results.append([doc.get("id"), doc.get("name"), hit.score])

        results = sorted(results, key=lambda x : x[2], reverse=True)
        # return map(lambda x : x[0], results)
        return results

    def filtering(self, search_results, filters):
        results = []
        for item in search_results:
            id = item[0]
            if not self.data[id]["open"]:
                continue

            valid = True
            for key, value in filters.items():
                if key == "Price Range":
                    if self.data[id]["attributes"][key] != value:
                        valid = False
                        break
                elif key == "Parking":
                    p = False
                    for v in self.data[id]["attributes"][key].values():
                        if v:
                            p = True
                            break
                    if not p:
                        valid = False
                        break
                else:
                    if key not in self.data[id]["attributes"] or not self.data[id]["attributes"][key]:
                        valid = False
                        break

            if valid:
                results.append(item)

        return results
