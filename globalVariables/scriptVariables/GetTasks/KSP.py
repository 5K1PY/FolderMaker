from functools import cache
import requests
from bs4 import BeautifulSoup
import urllib.parse


def get_el(tree, xpath):
    return tree.xpath(xpath)


@cache
def get_page_soup(url):
    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError(f"Something faied, request to URL '{url}' returned {response.status_code}")
    return BeautifulSoup(response.content, "html.parser")


@cache
def get_newest_url(url):
    soup = get_page_soup(url)
    year = soup.find("ul", class_="tasks")
    last_series = None
    for part in year.find_all("li"):
        if "série" in part.text:
            last_series = part.find("a")
    return urllib.parse.urljoin(url, last_series.attrs["href"])


@cache
def get_task_name(raw_name):
    raw_name = raw_name.strip()
    for i in range(len(raw_name)-1, -1, -1):
        if raw_name[i] == "(":
            return raw_name[:i].strip()
    return raw_name


def load(url):
    soup = get_page_soup(url)
    tasks = []
    for task_name in soup.find_all("h3"):
        if task_name.find("img") is None:
            continue
        if task_name.find("img").attrs["title"] == "Praktická opendata úloha":
            task_type = "practical"
        elif task_name.find("img").attrs["title"] == "Teoretická úloha":
            task_type = "theoretical"
        elif task_name.find("img").attrs["title"] == "Seriálová úloha":
            task_type = "serial"
        else:
            continue

        tasks.append((get_task_name(task_name.text), task_type))
    return tasks


def autoload(base_url):
    return load(get_newest_url(base_url))


def categorize(tasks, category):
    return list(filter(lambda x: x[1] == category, tasks))


def get_names(tasks):
    return list(map(lambda x: x[0], tasks))


# task returning functions - use these
def autoload_tasks(base_url):
    return get_names(autoload(base_url))


def load_tasks_categorized(base_url, category):
    return get_names(categorize(autoload(base_url), category))


if __name__ == "__main__":
    base_url = "https://ksp.mff.cuni.cz/h/ulohy/"
    print(get_newest_url(base_url))
    print(autoload(base_url))
    print(autoload_tasks(base_url))
    for category in ("practical", "theoretical", "serial"):
        print(category)
        print("\t", load_tasks_categorized(base_url, category))
