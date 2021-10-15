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
        raise FileNotFoundError(f"Path {path} doesn't exist")


def read_file(path):
    with open(path, encoding="utf-8") as file:
        content = file.read()
    return content


def add_variable(key, value, variables):
    if key in variables:
        raise ValueError(f"Duplicate key {key} in variables.")
    variables[key] = value


def load_variable(name, variables, loaded_variables=None):
    if name not in variables:
        raise ValueError(f"Unknown name of variable {name}.")

    if loaded_variables is not None and loaded_variables[name] is False:
        variables[name] = load_content(variables[name], variables, loaded_variables)
        loaded_variables[name] = True
    return variables[name]


def load_content(value, variables, loaded_variables=None):
    i = 0
    loading_variable = 0
    loading = [""]

    while i < len(value):
        add = ""
        if i > 0 and value[i-1] == "\\" and (i == 1 or value[i-2] != "\\"):
            loading[-1] += value[i]

        elif value[i] == "{":
            loading_variable += 1
            loading.append("")

        elif value[i] == "}":
            loading_variable -= 1
            if loading_variable < 0:
                raise ValueError("'}' before '{' in " + value + ".")
            loading[loading_variable] += load_variable(loading.pop(), variables, loaded_variables)

        else:
            loading[-1] += value[i]
        i += 1

    if loading_variable > 0:
        raise ValueError("No matching parenthesis for '{' in " + value + ".")
    return loading[0]


def make_directory(path, directory, variables, templates):
    for name, value in directory.items():
        name = load_content(name, variables)
        # creating a file
        if isinstance(value, str):
            with open(os.path.join(path, name), "w", encoding="utf-8") as file:
                file.write(load_content(value, variables))
        # creating a directory
        elif isinstance(value, dict):
            if not os.path.exists(os.path.join(path, name)):
                os.mkdir(os.path.join(path, name))
            make_directory(os.path.join(path, name), value, variables, templates)
        # creating a template
        if isinstance(value, list):
            if name not in templates:
                raise ValueError(f"Unknown template {name}.")
            template = templates[name]
            for args in value:
                if isinstance(args, str):
                    if len(template["args"]) != 1:
                        raise Exception(f"Not enough arguments [{args}] for template {name}.")
                    local_variables = {template["args"][0]: args}
                else:
                    if len(template["args"]) != len(args):
                        raise Exception(f"Not enough arguments {args} for template {name}.")
                    local_variables = {template["args"][i]: args[i] for i in range(len(args))}
                make_directory(path, template["dir"], {**variables, **local_variables}, templates)


def load_variables(config_dir, config):
    variables = deepcopy(config["variables"])
    for variableName, variableFile in config["variableFiles"].items():
        path = load_path(config_dir, "fileVariables", variableFile)
        add_variable(variableName, read_file(path), variables)

    # TODO add script variables

    loaded_variables = {key: key not in config["variables"] for key in variables}

    for variable in variables:
        load_variable(variable, variables, loaded_variables)

    return variables


if len(sys.argv) < 3:
    raise Exception("Not enough arguments.")

config_dir = load_path(sys.argv[1])
path = load_path(sys.argv[2])

config = json.loads(read_file(os.path.join(config_dir, "config.json")))

variables = load_variables(config_dir, config)
make_directory(path, config["dir"], variables, config["templates"])
