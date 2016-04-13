import sys
import os
import json

def main():
    data = None
    with open("data.json", "r") as f:
        data = json.load(f)

    i = 0

    temp = {}

    for key in data:
        temp[key] = data[key]
        i += 1
        if i >= 1000:
            break

    with open("sample1000.json", "w") as f:
        json.dump(temp, f)


if __name__ == "__main__":
    main()
