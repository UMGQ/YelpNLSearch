#flask_jqry.py
import NLP
import load_test
from flask import Flask, request
from flask import json

app = Flask(__name__)

@app.route('/')
def main():
    f = open('index.html', 'r')

    return "\"\"\"" + f.read() 


@app.route('/process', methods=['POST'])
def view_do_something():

    if request.method == 'POST':
        request_text = request.form.get('stext')
        #location = NLP.do_query_NLP(request_text)
        #your database process here
        #data = "hahahah"
        data = str(load_test.load_test())
        #return "location:" + location
        return data
    else:
        return "NO OK"

if __name__ == '__main__':
    app.run()
