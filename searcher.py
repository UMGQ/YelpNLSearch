
"""
This class is used to perform query searches.
When a Searcher object is created, it loads the preprocessed data from disk to memory.
A query can be performed by calling function perform_query. The function will return list of search
results ranked by ranking score.
"""
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
        """
        Function to process a query.
        There are two steps: the first step uses the query to find relevant results ranked;
        the second step use the filter to eliminate items that do not match the filter.
        """
        print "Processing query:", query
        search_results = self.searching(query)
        results = self.filtering(search_results, filters)
        # if more than 10 results match the search query and pass the filtering
        # only 10 will be returned to web server and displayed in webpage
        MAX = 10
        if len(results) < MAX:
            MAX = len(results)
        ret = []
        # the following fields will be displayed in the webpage
        for i in range(MAX):
            id = results[i][0]
            tmp = {}
            tmp["name"] = self.data[id]["name"]
            tmp["address"] = self.data[id]["full_address"]
            tmp["category"] = self.data[id]["categories"]
            tmp["review count"] = self.data[id]["review_count"]
            tmp["stars"] = self.data[id]["stars"]
            ret.append(tmp)
        return ret

    def searching(self, query):
        """
        Function to perform the search. Results will be returned based on relevance.
        """
        print "Searching:"
        query = QueryParser(Version.LUCENE_4_10_1, "text", self.analyzer).parse(query)
        MAX = 500
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
        """
        Function to perform filtering.
        """
        print "Filtering..."
        results = []
        for item in search_results:
            id = item[0]
            # get rid of those businesses that are not longer in existence
            if "open" in self.data[id] and not self.data[id]["open"]:
                continue

            valid = True
            for key, value in filters.items():
                if key == "Price Range":
                    if key in self.data[id]["attributes"] and self.data[id]["attributes"][key] != value:
                        valid = False
                        #print id, self.data[id]["name"], "filtered by price range, request:", value, "actual:", self.data[id]["attributes"][key]
                        break
                elif key == "Parking":
                    valid = self.check_parking(id)
                    if not valid:
                        #print id, self.data[id]["name"], "filtered by parking"
                        break
                elif key == "hours":
                    valid = self.check_hours(id, value)
                    if not valid:
                        break
                elif key == "city" or key == "state":
                    if self.data[id][key] != value:
                        valid = False
                        #print id, self.data[id]["name"], "filtered by city/state"
                        break
                elif key == "distance":
                    valid = self.check_distance(id, value)
                    if not valid:
                        #print id, self.data[id]["name"], "filtered by distance"
                        break
                else:
                    if key not in self.data[id]["attributes"] or not self.data[id]["attributes"][key]:
                        valid = False
                        #print id, self.data[id]["name"], "filtered by others"
                        break

            if valid:
                results.append(item)

        print "After filtering:", len(results)

        return results

    def check_distance(self, id, value):
        """
            check if a business resides in the requested distance radius
        """
        p1 = (self.data[id]["latitude"], self.data[id]["longitude"])
        p2 = value[1]
        
        if distance(p1, p2) <= value[0]:
            return True
        else:
            return False

    def check_parking(self, id):
        """
            function to check if a business has parking
        """
        parking = False
        if "Parking" not in self.data[id]["attributes"]:
            return False
        for value in self.data[id]["attributes"]["Parking"].values():
            if value:
                parking = True
                break

        return parking

    def check_hours(self, id, time):
        """
            function to check if a business opens at a given time
        """
        if time[0] in self.data[id]["hours"]:
            open_time = self.data[id]["hours"][time[0]]["open"]
            close_time = self.data[id]["hours"][time[0]]["close"]
        else:
            #print id, self.data[id]["name"], "does not have", time[0]
            return True

        open_time = self.hour_to_number(open_time)
        close_time = self.hour_to_number(close_time)
        query_time = self.hour_to_number(time[1])

        if (open_time > close_time and (query_time >= open_time or query_time <= close_time))\
                or (open_time < close_time and (query_time >= open_time and query_time <= close_time)) or (open_time == close_time):
            return True
        else:
            #print id, self.data[id]["name"], "open:", open_time, "close:", close_time, "query:", query_time, "filtered by hours"
            return False

    def hour_to_number(self, hours):
        l = hours.split(":")
        return float(l[0]) + float(l[1])/60

