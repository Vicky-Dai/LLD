""" Bug Squash – snakeyaml parser
You are given a small Java project that uses the SnakeYAML library to parse configuration files.
Your task is to fix two failing unit tests related to data parsing.
The project defines a class that reads YAML and CSV configuration files into Java objects or maps.
However, some of the tests currently fail because the parser does not correctly handle certain data formats and conversions.

There are two main failing tests:
Bug #1 — Boolean parsing issue
YAML file contains:
flag: On
Expected behavior:
The parser should correctly interpret "On" (case-insensitive) as a boolean true.
Actual behavior:
The parser currently treats it as a string "On" instead of a boolean.
Your task:
Update the YAML parsing logic so that boolean-like strings such as "on", "yes", "true" (in any case) are parsed as true, and "off", "no", "false" as false.
Hint: SnakeYAML does not automatically coerce all variants of boolean text, so you may need to manually post-process or configure the parser.

Bug #2 — CSV parsing issue
A separate test attempts to load configuration from a CSV file, e.g.:
id,name,active
1,John,true
2,Alice,false
Expected behavior:
Parser should successfully read the CSV file and produce a list or map of parsed records.
Actual behavior:
The parser currently throws an exception when trying to parse the CSV input, due to incorrect handling of file type or stream conversion.
Your task:
Fix the parsing logic so that CSV files can be read without errors.
The function should properly detect file type (YAML vs CSV) and handle each format separately.
Requirements
You may modify only the parsing logic or helper functions — do not change the test expectations.
Make the parser robust for case-insensitive boolean values.
Ensure the CSV parsing path does not break YAML parsing.
All tests should pass after your fixes.

Example Input/Output (for YAML)
threshold: 10
flag: On
Parsed result:
{
  "threshold": 10,
  "flag": true
} """


# Bug #2 - CSV parsing issue
def parse_config(filename, content):
    splitfilename = filename.split(".")
    if splitfilename[-1] == "csv":
        return parse_csv(content)
    if splitfilename[-1] == "yaml":
        return parse_yaml(content)
# second way to do it
def parse_config(filename, content):
    if filename.endswith("csv"):
        return parse_csv(content)
    if filename.endswith("yaml"):
        return parse_yaml(content)

#     raise ValueError(f"Invalid file type: {splitfilename[-1]}")

import yaml

def parse_yaml(content):
    return yaml.safe_load(content)
                    
def parse_csv(content):
    parse_content = content.split("\n")
    form = []
    head = parse_content[0].split(",")
    for line in parse_content[1:]:
        values = line.split(",")
        form.append(dict(zip(head, values)))
    return form

