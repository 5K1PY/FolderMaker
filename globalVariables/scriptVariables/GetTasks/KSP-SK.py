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
    table = soup.find("table", class_="task-list")
    for row in table.children:
        if row.find("a") != -1 and row.find("a") is not None:
            names.append(f'{row.find("td").text.strip()} {row.find("a").text}')
    return names


def load_all_tasks(url):
    return load(url)


def load_suitable_tasks(url, level):
    try:
        level = int(level)
    except ValueError:
        print(f"KSP-SK level is not a number: {level}")
        return []
    return load(url)[level-1:level+4]


if __name__ == "__main__":
    url = "https://www.ksp.sk/ulohy/"
    print(load_all_tasks(url))
    for i in range(1, 5):
        print(load_suitable_tasks(url, str(i)))
