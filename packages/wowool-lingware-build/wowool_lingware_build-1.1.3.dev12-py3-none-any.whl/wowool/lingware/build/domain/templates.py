DOMAIN_SETUP_TEMPLATE = """#
{PREFIX_DO_NOT_EDIT}
# This file is generated.
#
import os
import shutil
from pathlib import Path
import sys
from setuptools import setup, find_namespace_packages, Extension

THIS_DIR = Path(__file__).parent.resolve()
language = THIS_DIR.name

wowool_packages = ["{wowool_module}"]

results = setup(
    name="{lxware_namespace}-{package_name}",
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

DOMAIN_MAKEFILE_TEMPLATE = """######################################################################################
# Generate Makefile to build {name} {language_filename_version} modules:
# Unpublished Copyright (c) 2020 EyeOnText, All Rights Reserved.
# NOTICE:  All information contained herein is, and remains the property of EyeOnText.
######################################################################################
WOC:= {woc_app}
COMPONENT={name}
DOM_DOM ={dom_file_target}
DOM_CONF_SRC={dom_info_file_source}
DOM_INFO_TARGET={dom_info_file_target}
FILENAME_VERSION:={filename_version}

BUILD_PREP=_build_{name}
PACKAGE_FILES=$(DOM_DOM) $(DOM_INFO_TARGET) {additional_package_files}
PACKAGE = $(PACKAGE_FILES)

all: $(PACKAGE)

SOURCES := {sources}

$(DOM_DOM) : $(SOURCES)
	$(WOC) {woc_options} -l wowool/{language_filename_version} {thread_option} -o $(DOM_DOM) $(SOURCES) --lxware {lxware}

$(DOM_INFO_TARGET) : $(DOM_CONF_SRC)
	convert_domain_info -f $< --output_file $@ --filename_version $(FILENAME_VERSION)

{additional_package_build_statements}

ut:
	$(WOC) -t -l wowool/{language_filename_version} -o $(DOM_DOM) $(SOURCES)

clean:
	-rm -r $(PACKAGE) dist build *.egg-info
	-rm $(DOM_DOM)_inc

clean_deploy:
	-rm -r dist build *.egg-info


"""
