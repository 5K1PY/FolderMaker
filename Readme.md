# Description
FolderMaker is a tool to create folders and files with custom content with writing as few code as possible.

# Usage
To run FolderMaker run `python Main.py <config folder> <destination folder>` in terminal.
This will create folders and files in `destination folder` according to the recipe in `config folder`.

Example: `python Main.py ".\ExampleConfigs\Fykos\FykosTexJmenoUlohy\" "."`

# Config Folder
Each config folder must have inside a `config.json` file.
It can also have `fileVariables` and `scriptVariables` folders.

## Example configs
Example configs are configs of folders for common czech competitions. Use them at your free wish.

# Config File
Config file is a json with a dictionary. The dictionary can have a following keys in it:
 - [dir](#dir)
 - [variables](#variables)
 - [fileVariables](#file-variables)
 - [scriptVariables](#script-variables)
 - [templates](#templates)

## Dir
Dictionary under key `dir` specifies how the maked directories and files will look like.
The dictionary contains folders, files and templates, that will be created in the destination folder.

The contents of this dictionary can be recipes for:
 - files: `"fileName": "fileContent"`, which creates file `fileName` with content `fileContent` at the current folder
 - folders: `"folderName": {folder contents}`, which creates folder `folderName` with its contents (contents are specified in a same way as in this directory - recursively).
 - temlates: `temlateName: []` or `temlateName: "..."`, where string evalutes to list (see [list evaluation](#variable-to-list)). This corresponds to several callings of [template](#templates), where in i-th call arguments are i-th element in this array.  

## Folder creation variables
For FolderMaker to be highly customisable, it can create names and file contents, that change based on variables. For adding variables into names and contents we use string evaluation, which works simmilary to f-strings:

### Variable to string
Variable to string is evaluated when enclosed in **{}**. Consider variable `myVar` that equals `"1"`. String `"a{myVar}{myVar}b"` then evaluates to `a11b`.

### Variable to list
Varibles are evaluated to lists when first character of the string is `"$"`. Then the entire string is treated as the result is the list. List variables are evaluated and added together: \
`myList` = `["1"]` \
`"${myList} + ["1", "2"]"` evalutes to `"["1", "1", "2"]"` \
`"${myList} + ["1", {myList}]"` evalutes to `"["1", "1", ["1"]]"`

### Variables
Variables can be three types:
 - [basic](#basic-variables)
 - [file](#file-variables)
 - [script](#script-variables)
 - [special](#special-variables)

### Basic variables
Basic variables are included in `config.json` and their string form is automatically evaluated before file creation.

Syntax:
1. `"variables": {`
2. `    "variable1": "foo",`
3. `    "variable2": "not {variable1}"`
4. `}`
### File variables
File variables are loaded from `./fileVariables` folder. This option is designed in order to reduce `config.json` text with limited functionality. Beware: File variables are **not** evaluated!

Syntax:
1. `"fileVariables": {`
2. `    "variable": "file1.txt"`
3. `}`

### Script variables
Script variables are python programs, that are given thier arguments and variable contents are the results they return. Arguments of scripts are automatically evaluated, whilist their results are not.

Syntax:
1. `"scriptVariables": {`
2. `    "variable": {`
3. `        "filename": "GetVar", // name of python script`
4. `        "func": "foo",  // function to call`
5. `        "args": ["arg1", "{variable1}"]  // function arguments`
6. `    }`
7. `}`

Use script variables when you can't get something by normal varibles e.g. loading data from web or getting lowest available folder name

### Special variables
Special variables are not defined by the user, but are defined by the program. Those are:
 - `"\\configDir"`: path to Config directory
 - `"\\path"`: path to `destination folder`, where folders and files are made

## Templates
Templates are folder/file recipts to reduce lenght of `dir`. They are defined in `templates` dictionary. They have similar syntax to `dir` dictionary, but can have local variables, that are given as arguments, but can use global variables as well.

Syntax:
1. `"template1": {`
2. `    "arguments": ["folderName", "fileName"],`
3. `    "dir": {`
4. `        "{folderName}": {`
5. `            "{fileName}.{fileType}":  "example1"`
6. `        }`
7. `    }`
8. `}`

(Here fileType is a global variable)
When using templates in `dir` dictionary use template name as key and list or string that evaluates to list as arguments: \
1. `"dir"`: {`
2. `    "folder1": {`
3. `        "template1": ["1", "{var1}"]`
4. `    }`
5. `}`
