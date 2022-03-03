from functools import cache
import requests
from bs4 import BeautifulSoup

REPLACER = {
    " ": "_",
    "á": "a",
    "č": "c",
    "ď": "d",
    "é": "e",
    "ě": "e",
    "í": "i",
    "ň": "n",
    "ó": "o",
    "ř": "r",
    "š": "s",
    "ť": "t",
    "ú": "u",
    "ů": "u",
    "ý": "y"
}


def beautify_one(name):
    return "".join([REPLACER[char] if char in REPLACER else char for char in name.lower()])


def beautify(tasks):
    return list(map(beautify_one, tasks))


def beautify_to_pair(tasks):
    return list(map(lambda x: (x, beautify_one(x)), tasks))


def beautify_first(tasks):
    return [(task[0], beautify_one(task[0])) + task[1:] for task in tasks]


if __name__ == "__main__":
    tasks = ["1 Pěnkavy", "2 Sloni", "3 Ryby"]
    print(beautify(tasks))
    print(beautify_to_pair(tasks))
