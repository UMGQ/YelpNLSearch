import sys
import os
from searcher import Searcher

def main():
    print "Usage: python test_searcher.py <data>"
    path = sys.argv[1]
    searcher = Searcher(path)
    print searcher.process_query("clancy's pub", {})

if __name__ == "__main__":
    main()
