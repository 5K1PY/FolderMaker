from functools import cache
import requests
import lxml.html
from bs4 import BeautifulSoup


def get_el(tree, xpath):
    return tree.xpath(xpath)


@cache
def load(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError(f"Something faied, request to URL '{url}' returned {response.status_code}")
    soup = BeautifulSoup(response.content, "html.parser")
    names = []
    for headline in soup.find_all("h3", class_="task-headline"):
        names.append(headline.text)
    return names


def load_all_tasks(url):
    return load(url)


def load_filtered_tasks(url, suitable):
    return list(filter(lambda x: x.split(".")[0] in suitable, load(url)))


if __name__ == "__main__":
    url = "https://fykos.cz/zadani"
    print(load_all_tasks(url))
    print(load_filtered_tasks(url, ["1", "2", "3", "4", "5", "E", "S"]))
    print(load_filtered_tasks(url, ["P"]))
