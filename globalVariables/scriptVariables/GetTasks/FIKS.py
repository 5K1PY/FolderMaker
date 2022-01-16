from functools import cache
import requests
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
    for div in soup.find_all("div", class_="panel panel-default"):
        names.append((
            div.find("a").text.strip(),
            "kola lze řešit i v" in div.find("div", class_="panel-body").text.strip()
        ))
    return names


def filter_new_tasks(tasks):
    return list(filter(lambda x: not x[1], tasks))


def ordered_tasks(tasks):
    return list(map(lambda x: (x[0]+1, x[1][0]), enumerate(tasks)))


def load_all_tasks(url):
    return list(map(lambda x: f"{x[0]} {x[1]}", ordered_tasks(load(url))))


def load_new_tasks(url):
    return list(map(lambda x: f"{x[0]} {x[1]}", ordered_tasks(filter_new_tasks(load(url)))))


if __name__ == "__main__":
    url = "https://fiks.fit.cvut.cz/ulohy/"
    print(load_all_tasks(url))
    print(load_new_tasks(url))
