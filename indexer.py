import sys
import os
import collections
import json
import lucene
from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

class Indexer(object):
    def __init__(self, source_path, destination=None):
        self.source_path = source_path
        self.destination = destination
        self.business = source_path + "yelp_academic_dataset_business.json"
        self.review = source_path + "yelp_academic_dataset_review.json"
        self.tip = source_path + "yelp_academic_dataset_tip.json"
        self.data = {}

    def preprocess(self):
        print "PREPROCESSING..."
        
        """
        for file in os.listdir("."):
            if file == self.destination:
                print "Loading from " + self.destination
                with open(self.destination, "r") as f:
                    self.data = json.load(f)
                return
        """

        # preprocess business.json
        print "Preprocessing business.json"
        with open(self.business, "r") as f:
            for line in f:
                line = json.loads(line)
                id = line["business_id"]
                if id in self.data:
                    print "id already exists"
                else:
                    self.data[id] = line
                    self.data[id]["review"] = []
                    self.data[id]["tip"] = []

        # preprocess review.json
        print "Preprocessing review.json"
        with open(self.review, "r") as f:
            for line in f:
                line = json.loads(line)
                if line["business_id"] in self.data:
                    self.data[line["business_id"]]["review"].append(line)
                else:
                    print "review not related!"

        # preprocess tip.json
        print "Preprocessing tip.json"
        with open(self.tip, "r") as f:
            for line in f:
                line = json.loads(line)
                if line["business_id"] in self.data:
                    self.data[line["business_id"]]["tip"].append(line)
                else:
                    print "tip not related!"

        # dump to json
        """
        if self.destination:
            print "Writing to " + self.destination
            with open(self.destination, "w") as f:
                json.dump(self.data, f)
        """

    def index(self):
        print "INDEXING..."
        lucene.initVM()
        indexDir = SimpleFSDirectory(File("index/"))
        writerConfig = IndexWriterConfig(Version.LUCENE_4_10_1, StandardAnalyzer())
        writer = IndexWriter(indexDir, writerConfig)

        for key, business in self.data.items():
            doc = Document()
            doc.add(Field("name", business["name"], Field.Store.YES, Field.Index.ANALYZED))
            doc.add(Field("address", business["full_address"], Field.Store.YES, Field.Index.ANALYZED))
            cat_text = "\n".join(business["categories"])
            doc.add(Field("category", cat_text, Field.Store.YES, Field.Index.ANALYZED))

            review_text = ""
            for review in business["review"]:
                review_text += review["text"]

            tip_text = ""
            for tip in business["tip"]:
                tip_text += tip["text"]

            doc.add(Field("review", review_text, Field.Store.YES, Field.Index.ANALYZED))
            doc.add(Field("tip", tip_text, Field.Store.YES, Field.Index.ANALYZED))

            writer.addDocument(doc)

        writer.close()
