import os
import re


def load(directory, regex, regex_index=0, type_of="all"):
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory {directory} not found.")

    check = []
    for file in os.scandir(directory):
        if type_of == "all":
            check.append(file)
        elif file.is_dir() and type_of == "folders":
            check.append(file)
        elif not file.is_dir() and type_of == "files":
            check.append(file)

    result = 0
    for file in check:
        occurences = re.findall(regex, file.name)
        if len(occurences) > 0:
            result = max(result, int(occurences[regex_index]))

    return str(result + 1)


if __name__ == "__main__":
    print(load(".", "Serie(\\d+)"))
