# Voice Enabled Natural Language Search Engine for Yelp

## Dataset
This system runs on Yelp Dataset Challenge dataset (https://www.yelp.com/dataset_challenge).
Download the dataset and extract the files to a folder.

## Packages/tools needed to run the system:
The following packages needs to be installed for the system to work:
* Speech Recognition 3.3.3 (https://pypi.python.org/pypi/SpeechRecognition/)
* NLTK (http://www.nltk.org)
* Geonamescache (https://pypi.python.org/pypi/geonamescache)
* PyLucene (http://lucene.apache.org/pylucene/index.html)
* Flask (http://flask.pocoo.org)
* Bootstrap (http://getbootstrap.com)

## Steps to run the system
1. Index the Yelp dataset:
  
  The preprocessed data will be saved to `data.json`. The inverted index will be saved to `./index/` folder
  This step has been done and all the output files has been uploaded to rod. You can skip to step 2.

  `python test_indexer.py <source to yelp dataset folder> data.json`

2. Start the system:

  This will load necessary data into memory and initialize all necessary objects and start a web server.
  The address to access the web server will be displayed. Enter that address in a browser to access the page.

  `python flask_jqry.py`

## Steps to test the voice search system
1. Index the Yelp dataset (if this has been done before, you can skip this step):
  
  The preprocessed data will be saved to `data.json`. The inverted index will be saved to `./index/` folder
  This step has been done and all the output files has been uploaded to rod. You can skip to step 2.

  `python test_indexer.py <source to yelp dataset folder> data.json`

2. Start the voice search module using the following command and then follow on screen prompt:
  
  `python test_speech.py`
