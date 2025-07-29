PACKAGE_SETUP_TEMPLATE = """#
{PREFIX_DO_NOT_EDIT}
# This file is generated.
#
from pathlib import Path
from setuptools import setup

THIS_DIR = Path(__file__).parent.resolve()
language = THIS_DIR.name

wowool_packages = ["{wowool_module}"]

results = setup(
    name="wowool-lxware-{package_name}",
    version="{repo_version}",
    packages=wowool_packages,
    author="Wowool",
    author_email = "info@wowool.com",
    description="Wowool NLP {package_name} Package",
    zip_safe=False,
    package_data={{"{wowool_module}": ["*"]}},
    include_package_data=True,
    {setup_py_install_requirement}
)

"""


PACKAGE_PYPROJECT_TEMPLATE = """
[project]
name = "wowool-{package_name}"
version = "{repo_version}"
description = "Wowool NLP {package_name} Package"
readme = {{ file = "README.md", content-type = "text/markdown" }}

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
"wowool.lxware.wowool" = ['*.*']

"""

README_TEMPLATE = """# Wowool NLP {package_name} Package
This package contains the language file and domains for {language}.
To use this package, you need to install the wowool-sdk package and request a license file at info@wowool.com

## Usage

```python
from wowool.sdk import Pipeline
from pathlib import Path
input_text = Path("input.txt").read_text()
pipeline = Pipeline("{language},entity")
doc = pipeline(input_text)
print(doc)
```

## Domains

{domains}

"""
