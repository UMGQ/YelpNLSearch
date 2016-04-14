#flask_jqry.py
import json
from flask import Flask, request
from flask import json
from searcher import Searcher
from query_speechrecognition import query_speech
from query import query

app = Flask(__name__)

searcher = None

@app.route('/')
def main():
    """
        This function is ued for display the webpage on the browser
    """
    f = open('index.html', 'r')

    return "\"\"\"" + f.read() 


@app.route('/process', methods=['POST'])
def view_do_something():
    """
        This function for handling the POST request sent from web page and call another python script to run for getting data
    """
    if request.method == 'POST':
        request_text = request.form.get('stext')
        data = process(request_text)
        return data
    else:
        return "NO OK"

def process(q):
    """
        Generating parsed queries and doing search
    """
    if not q:
        return
    q, filters = query(q)
    print "Filters:"
    print filters
    results = searcher.process_query(q, filters)

    ret = ""
    for r in results:
        ret += (str(json.dumps(r)) + "#")

    return ret[:-1]

if __name__ == '__main__':
    searcher = Searcher("data.json")
    print "Finished loading data.json"
    app.run()
