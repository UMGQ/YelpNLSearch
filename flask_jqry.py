#flask_jqry.py
import NLP
import json
from flask import Flask, request
from flask import json
from searcher import Searcher
from query_speechrecognition import query_speech
from query import query

app = Flask(__name__)

searcher = None

#This function is ued for display the webpage on the browser
@app.route('/')
def main():
    f = open('index.html', 'r')

    return "\"\"\"" + f.read() 

#This function for handling the POST request sent from web page and call another python script to run for getting data
@app.route('/process', methods=['POST'])
def view_do_something():

    if request.method == 'POST':
        request_text = request.form.get('stext')
        #location = NLP.do_query_NLP(request_text)
        #your database process here
        #data = "hahahah"
        data = process(request_text)
        #return "location:" + location
        return data
    else:
        return "NO OK"

#Generating parsed queries and doing search
def process(q):
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
