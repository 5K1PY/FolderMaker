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
                    # variable
                    self.variables[name] = self.load_content(self.variables[name])

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
            if isinstance(value, str):
                with open(os.path.join(path, name), "w", encoding="utf-8") as file:
                    file.write(self.load_content(value))

            # creating a directory
            elif isinstance(value, dict):
                if not os.path.exists(os.path.join(path, name)):
                    os.mkdir(os.path.join(path, name))
                self.make_directory(path=os.path.join(path, name), directory=value)

            # creating a template
            if isinstance(value, list):
                if name not in self.templates:
                    raise ValueError(f"Unknown template {name}.")
                template = self.templates[name]
                for args in value:
                    if isinstance(args, str):
                        if len(template["args"]) != 1:
                            raise Exception(f"Not enough arguments [{args}] for template {name}.")
                        local_variables = {template["args"][0]: self.load_content(args)}
                    else:
                        if len(template["args"]) != len(args):
                            raise Exception(f"Not enough arguments {args} for template {name}.")
                        local_variables = {template["args"][i]: self.load_content(args[i]) for i in range(len(args))}

                    saved_variables = self.variables
                    self.variables = {**self.variables, **local_variables}
                    self.make_directory(path=path, directory=template["dir"])
                    self.variables = saved_variables


if len(sys.argv) < 3:
    raise Exception("Not enough arguments.")

folder_maker = FolderMaker(sys.argv[1], sys.argv[2])
folder_maker.make_directory()
