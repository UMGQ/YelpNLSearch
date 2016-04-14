"""
This script is used to index the yelp dataset.
Please use the following command to start this script:
    python test_indexer.py <path_to_yelp_dataset_folder> data.json
The inverted index will be saved to ./index/ folder, refer to indexer.py for more information.
The preprocessed data will be saved to file ./data.json.
"""
import sys
import os
from indexer import Indexer

def main():
    print "Usage: python test_indexer.py <source path> [destination]"
    source = sys.argv[1]
    destination = None
    if len(sys.argv) > 2:
        destination = sys.argv[2]

    # initialize a indexer object
    indexer = Indexer(source, destination)
    # preprocess the yelp dataset
    indexer.preprocess()
    # index the preprocessed data
    indexer.index()

if __name__ == "__main__":
    main()
