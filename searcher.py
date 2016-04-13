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
        MAX = 50
        hits = self.searcher.search(query, MAX)
        results = []
        for hit in hits.scoreDocs:
            doc = self.searcher.doc(hit.doc)
            results.append([doc.get("id"), doc.get("name"), hit.score])

        results = sorted(results, key=lambda x : x[2], reverse=True)
        # return map(lambda x : x[0], results)
        print "Search hits:", len(results)
        return results

    def filtering(self, search_results, filters):
        print "Filtering..."
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
                        print id, self.data[id]["name"], "filtered by price range, request:", value, "actual:", self.data[id]["attributes"][key]
                        break
                elif key == "Parking":
                    valid = self.check_parking(id)
                    if not valid:
                        print id, self.data[id]["name"], "filtered by parking"
                        break
                elif key == "hours":
                    valid = self.check_hours(id, value)
                    if not valid:
                        break
                elif key == "city" or key == "state":
                    if self.data[id][key] != value:
                        valid = False
                        print id, self.data[id]["name"], "filtered by city/state"
                        break
                elif key == "distance":
                    valid = self.check_distance(id, value)
                    if not valid:
                        print id, self.data[id]["name"], "filtered by distance"
                        break
                else:
                    if key not in self.data[id]["attributes"] or not self.data[id]["attributes"][key]:
                        valid = False
                        print id, self.data[id]["name"], "filtered by others"
                        break

            if valid:
                results.append(item)

        print "After filtering:", len(results)

        return results

    def check_distance(self, id, value):
        p1 = (self.data[id]["latitude"], self.data[id]["longitude"])
        p2 = value[1]
        
        if value[0] <= distance(p1, p2):
            return True
        else:
            return False

    def check_parking(self, id):
        parking = False
        for value in self.data[id]["attributes"]["Parking"].values():
            if value:
                parking = True
                break

        return parking

    def check_hours(self, id, time):
        if time[0] in self.data[id]["hours"]:
            open_time = self.data[id]["hours"][time[0]]["open"]
            close_time = self.data[id]["hours"][time[0]]["close"]
        else:
            print id, self.data[id]["name"], "does not have", time[0]
            return False

        open_time = self.hour_to_number(open_time)
        close_time = self.hour_to_number(close_time)
        query_time = self.hour_to_number(time[1])

        if (open_time > close_time and (query_time >= open_time or query_time <= close_time))\
                or (open_time < close_time and (query_time >= open_time and query_time <= close_time)) or (open_time == close_time):
            return True
        else:
            print id, self.data[id]["name"], "open:", open_time, "close:", close_time, "query:", query_time, "filtered by hours"
            return False

    def hour_to_number(self, hours):
        l = hours.split(":")
        return float(l[0]) + float(l[1])/60

