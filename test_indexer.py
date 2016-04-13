import sys
import os
from indexer import Indexer

def main():
    print "Usage: python test_indexer.py <source path> [destination]"
    source = sys.argv[1]
    destination = None
    if len(sys.argv) > 2:
        destination = sys.argv[2]

    indexer = Indexer(source, destination)
    indexer.preprocess()
    indexer.index()

if __name__ == "__main__":
    main()
