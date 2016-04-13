import sys
import os
from searcher import Searcher

def main():
    print "Usage: python test_searcher.py <data>"
    path = sys.argv[1]
    searcher = Searcher(path)
    print searcher.process_query("burger", {'distance': [10, (36.169941, -115.13983)]})

if __name__ == "__main__":
    main()
