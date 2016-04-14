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
    """
    This class is used to preprocess the yelp dataset and index the preprocessed data.
    The inverted index will be saved on disk.
    """
    def __init__(self, source_path, destination=None):
        """
        source_path: the path to the yelp dataset folder
        destination: the destination file where to save the preprocessed data
        The business, review and tip data from the Yelp dataset are processed and indexed.
        The inverted index will be saved to folder ./index/
        The preprocessed data will be saved to "destination" which can be read by searcher later on.
        """
        self.source_path = source_path
        self.destination = destination
        self.business = source_path + "yelp_academic_dataset_business.json"
        self.review = source_path + "yelp_academic_dataset_review.json"
        self.tip = source_path + "yelp_academic_dataset_tip.json"
        self.data = {}

    def preprocess(self):
        """
        This function is used to preprocess the yelp dataset.
        Data from the business, review and tip file will be combined,
        to form a single entity (a dict with business_id as key) that represents all the businesses.
        """
        print "PREPROCESSING..."

        # if the data has been preprocessed before, just return
        for file in os.listdir("."):
            if file == self.destination:
                print "Loading from " + self.destination
                with open(self.destination, "r") as f:
                    self.data = json.load(f)
                return

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

        # save the preprocessed data to destination file
        if self.destination:
            print "Writing to " + self.destination
            with open(self.destination, "w") as f:
                json.dump(self.data, f)

    def index(self):
        """
        This function is used to index the preprocessed data.
        The inverted index will be saved to ./index/ folder
        business_id, name, address, categories, review and tip data are indexed.
        """
        print "INDEXING..."
        lucene.initVM()
        indexDir = SimpleFSDirectory(File("index/"))
        writerConfig = IndexWriterConfig(Version.LUCENE_4_10_1, StandardAnalyzer())
        writer = IndexWriter(indexDir, writerConfig)

        # each business indexed as a document
        for key, business in self.data.items():
            doc = Document()
            text = ""
            doc.add(Field("id", business["business_id"], Field.Store.YES, Field.Index.ANALYZED))
            doc.add(Field("name", business["name"], Field.Store.YES, Field.Index.ANALYZED))
            doc.add(Field("address", business["full_address"], Field.Store.YES, Field.Index.ANALYZED))
            cat_text = "\n".join(business["categories"])
            doc.add(Field("category", cat_text, Field.Store.YES, Field.Index.ANALYZED))

            # combine all reviews of a business together
            review_text = ""
            for review in business["review"]:
                review_text += review["text"]
            # combine all tip of a business together
            tip_text = ""
            for tip in business["tip"]:
                tip_text += tip["text"]

            # concatenate the data to be indexed and add it as one field
            text += business["name"]
            text += business["full_address"]
            text += cat_text
            text += review_text
            text += tip_text
            doc.add(Field("text", text, Field.Store.YES, Field.Index.ANALYZED))
            
            # add the business doc to writer
            writer.addDocument(doc)

        writer.close()
