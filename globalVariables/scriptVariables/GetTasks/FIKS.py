from functools import cache
import requests
from bs4 import BeautifulSoup


def get_el(tree, xpath):
    return tree.xpath(xpath)


@cache
def load_raw(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError(f"Something faied, request to URL '{url}' returned {response.status_code}")
    soup = BeautifulSoup(response.content, "html.parser")
    divs = []
    for div in soup.find_all("div", class_="panel panel-default"):
        divs.append(div)
    return divs


def load(url):
    tasks = []
    for task_num, div in enumerate(load_raw(url)):
        if "Odpověz Sfinze!" in div.text:
            flag = "practical"
        elif "Rozmysli, popiš a naprogramuj!" in div.text:
            flag = "mixed"
        elif "Zamysli se!" in div.text:
            flag = "theoretical"

        tasks.append([
            task_num+1,
            div.find("a").text.strip(),
            "kola lze řešit i v" in div.find("div", class_="panel-body").text.strip(),
            flag
        ])
    return tasks


def filter_new_tasks(tasks):
    tasks = list(filter(lambda x: not x[2], tasks))
    for i in range(len(tasks)):
        tasks[i][0] = i+1
    return tasks


def beautify(tasks):
    return list(map(lambda x: f"{x[0]} {x[1]}", tasks))


def categorize(tasks, category):
    return list(filter(lambda x: x[3] == category, tasks))


# task returning functions - use these
def load_all_tasks(url):
    return beautify(load(url))


def load_new_tasks(url):
    return beautify(filter_new_tasks(load(url)))


def load_tasks_categorized(url, category):
    return beautify(categorize(load(url), category))


def load_new_tasks_categorized(url, category):
    return beautify(categorize(filter_new_tasks(load(url)), category))


if __name__ == "__main__":
    url = "https://fiks.fit.cvut.cz/ulohy/"
    print(load_all_tasks(url))
    print(load_new_tasks(url))
    for category in ("practical", "mixed", "theoretical"):
        print(category)
        print("\t", load_tasks_categorized(url, category))
        print("\t", load_new_tasks_categorized(url, category))
