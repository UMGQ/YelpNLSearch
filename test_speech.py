from query_speechrecognition import query_speech
from query import query
from searcher import Searcher

def main():
    searcher = Searcher("data.json")
    while True:
        print
        response = "n"
        print "=================================="
        while response != "y":
            response = raw_input("Ready to say something? (y/n)")
        q, filters = query_speech()
        if not q:
            continue
        print "Filters:"
        print filters
        print searcher.process_query(q, filters)

if __name__ == "__main__":
    main()
