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


def load_tasks_with_examples(base_url, category):
    url = get_newest_url(base_url)
    soup = get_page_soup(url)
    tasks_names = get_names(categorize(load(url), category))
    task_inputs = {}
    task_outputs = {}
    for headline in soup.find_all("h3"):
        task_name = get_task_name(headline.text)
        if task_name not in tasks_names:
            continue
        el = headline.next_sibling
        while el.name != "h3":
            if el.name == "div":
                description = el.find("i")
                if description is not None:
                    if description.text == "Ukázkový vstup:":
                        task_inputs[task_name] = el.find("pre").text.strip()
                    if description.text == "Ukázkový výstup:":
                        task_outputs[task_name] = el.find("pre").text.strip()

            el = el.next_sibling

    grouped = []
    for task_name in tasks_names:
        if task_name not in task_inputs:
            task_inputs[task_name] = ""
        if task_name not in task_outputs:
            task_outputs[task_name] = ""
        grouped.append((task_name, task_inputs[task_name], task_outputs[task_name]))
    return grouped


if __name__ == "__main__":
    base_url = "https://ksp.mff.cuni.cz/h/ulohy/"
    print(get_newest_url(base_url))
    print(autoload(base_url))
    print(autoload_tasks(base_url))
    for category in ("practical", "theoretical", "serial"):
        print(category)
        print("\t", load_tasks_categorized(base_url, category))
    print(load_tasks_with_examples(base_url, "practical"))
