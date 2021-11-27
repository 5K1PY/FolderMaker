import re
import sys
import os
import json
import importlib
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


def contains(characters, value):
    return all([character in value for character in characters])


class FolderMaker:
    def __init__(self, config_dir, path):
        self.config_dir = load_path(config_dir)
        self.path = load_path(path)

        self.config = json.loads(read_file(os.path.join(config_dir, "config.json")))

        self.load_variables()

        if "dir" not in self.config:
            raise Exception("Key \"dir\" missing in config.")
        if "templates" in self.config:
            self.templates = self.config["templates"]
        else:
            self.templates = {}

    def load_variables(self):
        self.variables = {}
        self.loaded_variables = {}

        self.add_variable("\\configDir", self.config_dir, status="loaded")
        self.add_variable("\\path", self.path, status="loaded")

        if "variables" in self.config:
            for variableName, variableValue in self.config["variables"].items():
                self.add_variable(variableName, variableValue)

        if "fileVariables" in self.config:
            for variableName, variableFile in self.config["fileVariables"].items():
                variablePath = load_path(self.config_dir, "fileVariables", variableFile)
                self.add_variable(variableName, read_file(variablePath), status="loaded")

        if "scriptVariables" in self.config:
            sys.path.insert(1, os.path.join(self.config_dir, "scriptVariables"))
            for variableName, scriptArgs in self.config["scriptVariables"].items():
                self.add_variable(variableName, scriptArgs)

        for variable in self.variables:
            self.load_variable(variable)

    def add_variable(self, key, value, status="to load"):
        if key in self.variables:
            raise ValueError(f"Duplicate key {key} in variables.")
        self.variables[key] = value
        self.loaded_variables[key] = status

    def load_variable(self, name):
        if name not in self.variables:
            raise ValueError(f"Unknown name of variable {name}.")

        if name in self.loaded_variables and self.loaded_variables[name] != "loaded":
            if self.loaded_variables[name] == "to load":
                self.loaded_variables[name] = "loading"

                if isinstance(self.variables[name], str):
                    # string variable
                    self.variables[name] = self.load_content(self.variables[name])

                elif isinstance(self.variables[name], list):
                    # list variable
                    self.variables[name] = [self.load_content(element) for element in self.variables[name]]

                elif isinstance(self.variables[name], dict):
                    # script variable
                    if "filename" not in self.variables[name]:
                        raise Exception(f"Missing \"filename\" of script variable {name}.")
                    if "args" not in self.variables[name]:
                        raise Exception(f"Missing \"args\" of script variable {name}.")
                    if "func" not in self.variables[name]:
                        raise Exception(f"Missing \"func\" of script variable {name}.")

                    pythonfile = importlib.import_module(self.variables[name]["filename"])
                    for i in range(len(self.variables[name]["args"])):
                        self.variables[name]["args"][i] = self.load_content(self.variables[name]["args"][i])
                    self.variables[name] = getattr(pythonfile, self.variables[name]["func"])(*self.variables[name]["args"])

                self.loaded_variables[name] = "loaded"

            elif self.loaded_variables[name] == "loading":
                raise Exception(f"Cyclic variable usage (\"{name}\" requires itself for its loading).")

        return self.variables[name]

    def load_content(self, value):
        if len(value) > 0 and value[0] == "$":
            loading_variable = -1
            i = 1
            loading = []
            add_to_list = []
            loading_string = False
        else:
            loading_variable = 0
            i = 0
            loading = [""]

        while i < len(value):
            if i > 0 and value[i-1] == "\\" and (i == 1 or value[i-2] != "\\"):
                loading[-1] += value[i]

            elif value[0] == "$" and loading_string is False and not contains(value[i], "[]\"'+,{}"):
                pass
            elif value[0] == "$" and value[i] == "[":
                loading_variable += 1
                loading.append([])
                add_to_list.append(False)
            elif value[0] == "$" and contains(value[i], ("]", ",")):
                loading_variable -= 1
                if loading_variable < 0:
                    raise Exception("']' before '[' in " + value + ".")
                if add_to_list.pop():
                    loading[loading_variable] += loading.pop()
                else:
                    loading[loading_variable].append(loading.pop())
                    if value[i] == "]" and len(add_to_list) > 0 and add_to_list[-1] is True:
                        add_to_list.pop()
                        loading_variable -= 1
                        if loading_variable < 0:
                            raise Exception("']' before '[' in " + value + ".")
                        loading[loading_variable] += loading.pop()

                if value[i] == ",":
                    add_to_list.append(False)

            elif value[0] == "$" and value[i] == "+":
                add_to_list.append(True)

            elif value[0] == "$" and value[i] == "'" or value[i] == '"':
                if isinstance(loading[-1], list):
                    loading_variable += 1
                    loading.append("")
                    loading_string = True
                elif isinstance(loading[-1], str):
                    loading_string = False

            elif value[i] == "{":
                loading_variable += 1
                loading_string = True
                loading.append("")

            elif value[i] == "}":
                loading_string = False
                if value[0] == "$":
                    loading.append(deepcopy(self.load_variable(loading.pop())))
                else:
                    loading_variable -= 1
                    loading[loading_variable] += self.load_variable(loading.pop())

            else:
                loading[-1] += value[i]
            i += 1

        if loading_variable > 0:
            raise ValueError("No matching parenthesis for '{' in " + value + ".")
        return loading[0]

    def make_directory(self, path=None, directory=None):
        if path is None:
            path = self.path
        if directory is None:
            directory = self.config["dir"]

        for name, value in directory.items():
            name = self.load_content(name)
            # creating a file
            if isinstance(value, str) and (len(value) == 0 or value[0] != "$"):
                if not os.path.exists(os.path.join(path, name)):
                    with open(os.path.join(path, name), "w", encoding="utf-8") as file:
                        file.write(self.load_content(value))
                else:
                    print(f"File {os.path.join(path, name)} already exists, creation skipped.")

            # creating a directory
            elif isinstance(value, dict):
                if ".." in name:
                    raise ValueError(f"Name of directory {name} contains '..'.")
                if not os.path.exists(os.path.join(path, name)):
                    os.mkdir(os.path.join(path, name))
                self.make_directory(path=os.path.join(path, name), directory=value)

            # creating a template
            elif isinstance(value, list) or (isinstance(value, str) and value[0] == "$"):
                if name not in self.templates:
                    raise ValueError(f"Unknown template {name}.")
                template = self.templates[name]

                if (isinstance(value, str) and value[0] == "$"):
                    value = self.load_content(value)

                for args in value:
                    if isinstance(args, str):
                        local_variables = {template["args"][0]: self.load_content(args)}
                    else:
                        local_variables = {template["args"][i]: self.load_content(args[i]) for i in range(len(args))}

                    saved_variables = self.variables
                    self.variables = {**self.variables, **local_variables}
                    self.make_directory(path=path, directory=template["dir"])
                    self.variables = saved_variables


if len(sys.argv) < 3:
    raise Exception("Not enough arguments.")

folder_maker = FolderMaker(sys.argv[1], sys.argv[2])
folder_maker.make_directory()
