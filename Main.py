import re
import sys
import os
import json
from copy import copy, deepcopy


def load_path(*paths):
    path = os.path.join(*paths)
    if os.path.exists(path):
        return path
    else:
        raise Exception(f"Path {path} doesn't exist")


def read_file(path):
    with open(path, encoding="utf-8") as file:
        content = file.read()
    return content


def add_variable(key, value, variables):
    if key in variables:
        raise Exception(f"Duplicate key {key} in variables.")
    variables[key] = value


def load_variable(name, variables, loaded_variables):
    if name not in variables:
        raise Exception(f"Unknown name of variable {name}.")

    if loaded_variables[name] is False:
        variables[name] = load_content(variables[name])
        loaded_variables[name] = True
    return variables[name]


def load_content(value, variables, loaded_variables):
    i = 0
    loading_variable = 0
    loading = [""]

    while i < len(value):
        add = ""
        if i > 0 and value[i-1] == "\\":
            loading[-1] += value[i]

        elif value[i] == "{":
            loading_variable += 1
            loading.append("")

        elif value[i] == "}":
            loading_variable -= 1
            if loading_variable < 0:
                raise Exception("'}' before '{' in " + value + ".")
            loading[loading_variable] += load_variable(loading.pop(), variables, loaded_variables)

        else:
            loading[-1] += value[i]
        i += 1

    if loading_variable > 0:
        raise Exception("No matching parenthesis for '{' in " + value + ".")
    return loading[0]


def load_variables(config_dir, config):
    variables = deepcopy(config["variables"])
    for variableName, variableFile in config["variableFiles"].items():
        path = load_path(config_dir, "fileVariables", variableFile)
        add_variable(variableName, read_file(path), variables)

    # TODO add script variables
    print(variables)

    loaded_variables = {key: key not in config["variables"] for key in variables}

    for variable in variables:
        load_variable(variable, variables, loaded_variables)


if len(sys.argv) < 3:
    raise Exception("Not enough arguments.")

config_dir = load_path(sys.argv[1])
path = load_path(sys.argv[2])

config = json.loads(read_file(os.path.join(config_dir, "config.json")))

load_variables(config_dir, config)
