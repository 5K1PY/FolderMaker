import sys
import os
import json


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


def add_variable(key, value):
    global variables
    if key in variables:
        raise Exception(f"Duplicate key {key}")


if len(sys.argv) < 3:
    raise Exception("Not enough arguments")

config_file = load_path(sys.argv[1])
path = load_path(sys.argv[2])

config = json.loads(read_file(config_file))

variables = config["variables"]
for variableName, variableFile in config["variableFiles"].items():
    path = load_path(os.path.dirname(config_file), variableFile)
    add_variable(variableName, read_file(path))

for a, b in variables.items():
    print(a, b)
