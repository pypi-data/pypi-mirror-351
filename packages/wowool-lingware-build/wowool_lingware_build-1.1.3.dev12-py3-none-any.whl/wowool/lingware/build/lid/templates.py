LANGUAGE_SETUP_TEMPLATE = """{PREFIX_DO_NOT_EDIT}
# This file is generated.
#
from setuptools import setup

wowool_packages = ["{wowool_module}"]
results = setup(
    name="{eot_namespace}-{package_name}",
    version="{repo_version}",
    packages=wowool_packages,
    author="EyeOnText",
    author_email = "info@eyeontext.com",
    description="Wowool NLP {' '.join(package_name.split('-'))} Package",
    zip_safe=False,
    package_data={{"{wowool_module}": ["*"]}},
    include_package_data=True,
    {setup_py_requirement}
)
"""
