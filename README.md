# Tableau Hyper IO: read and write Tableau hyper files using Pandas DataFrames
[![PyPI](https://img.shields.io/pypi/v/tableauhyperio)](https://pypi.org/project/tableauhyperio)
[![PyPI - License](https://img.shields.io/pypi/l/tableauhyperio)](https://github.com/AlexFrid/tableauhyperio/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## What is it?
A simple way to read Tableau hyper files into Pandas DataFrames
and write to Tableau hyper files from Pandas DataFrames.

## Why was this made?
For a project I was working on I needed to read hyper files.
I searched if a package already existed and found only the [pandleau](https://pypi.org/project/pandleau/) package,
which only writes to hyper files but does not read them and also uses the older extract 2.0 API.
Since I couldn't find any other package that met my needs I decided to make one myself, which has been a good learning experience.

## Installation

You can install tableauhyperio using pip:
```bash
pip install tableauhyperio
```
This will also try downloading the Tableau hyper API, tqdm and pandas packages
if you don't have them already.

## Example usage
```python
import tableauhyperio as hio

# Reading a regular hyper file
df = hio.read_hyper("example.hyper")

# Reading a hyper file with a custom schema
df = hio.read_hyper("example.hyper", "my_schema")

# Writing a regular hyper file
hio.to_hyper(df, "example_output.hyper")

# Writing a hyper file with a custom schema and custom table name
hio.to_hyper(df, "example_output.hyper", "my_schema", "my_table")
```

## Dependencies
- [Pandas](https://pandas.pydata.org)
- [tableauhyperapi](https://help.tableau.com/current/api/hyper_api/en-us/index.html)
- [tqdm](https://github.com/tqdm/tqdm)