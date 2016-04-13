import json
from pprint import pprint

def load_test():
    f = open('display_sample.json', 'r')
    d = ""
    for line in f:
        data = json.loads(line)
        dd = str(json.dumps(data)) + "#"
        d += dd
    return d[0:-1]





