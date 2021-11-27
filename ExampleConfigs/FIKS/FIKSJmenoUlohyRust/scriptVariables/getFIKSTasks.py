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


def get_el(tree, xpath):
    return tree.xpath(xpath)


@cache
def load(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError(f"Something faied, request to URL '{url}' returned {response.status_code}")
    soup = BeautifulSoup(response.content, "html.parser")
    names = []
    for div in soup.find_all("div", class_="panel panel-default"):
        names.append((
            div.find("a").text.strip(),
            "kola lze řešit i v" in div.find("div", class_="panel-body").text.strip()
        ))
    return names


def beautify(name):
    return "".join([REPLACER[char] if char in REPLACER else char for char in name.lower()])


def get_name(task):
    name = f"{task[0]+1} {task[1][0]}"
    return (name, beautify(name))


def load_all_tasks(url):
    return list(map(get_name, enumerate(load(url))))


def load_new_tasks(url):
    return list(map(get_name, enumerate(filter(lambda x: not x[1], load(url)))))


if __name__ == "__main__":
    url = "https://fiks.fit.cvut.cz/ulohy/"
    print(load_all_tasks(url))
    print(load_new_tasks(url))
