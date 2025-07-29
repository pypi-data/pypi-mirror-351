from pathlib import Path
import logging
from wowool.lingware.build.git import get_version
from wowool.lingware.build.utilities import clean_python_build_folders, resolve_template, PREFIX_DO_NOT_EDIT
from wowool.lingware.build.templates import PACKAGE_SETUP_TEMPLATE, PACKAGE_PYPROJECT_TEMPLATE, README_TEMPLATE
import json

logger = logging.getLogger(__name__)


def generate_package_setupfile(package_folder: Path, language: str, output_folder: Path):
    wowool_module = "wowool.lxware.wowool"
    package_name = language
    logger.debug(f"Template variables: {wowool_module=}{package_name=}")
    setup_fn = output_folder / "setup.py"
    # eot_namespace_dash = eot_namespace.replace("-", "_")
    repo_version = get_version()

    setup_py_install_requirement = ""
    # setup_dependencies = [f"{eot_namespace_dash}_language_{language}_basic=={repo_version}"]
    # if "dependencies" in jo_domain_info:
    #     dom_info_dependencies = jo_domain_info["dependencies"]
    #     setup_dependencies.extend([f"{eot_namespace_dash}_domain_{dep}=={repo_version}".replace("-", "_") for dep in dom_info_dependencies])

    clean_python_build_folders(package_folder)
    # !! do not remove it's used to resolve
    # setup_py_install_requirement = f"install_requires={json.dumps(setup_dependencies)}"
    # logger.debug(f"Template variables: {setup_py_install_requirement=}")

    setup_filename = package_folder / setup_fn
    try:
        with open(setup_filename, "w") as fp_mf:
            fp_mf.write(resolve_template(PACKAGE_SETUP_TEMPLATE, globals(), locals()))
        return setup_fn
    except Exception as ex:
        logger.exception(ex)
        setup_filename.unlink(missing_ok=True)


import re


def strip_version(component_name: str) -> str:
    return re.sub("""(.*)@(?:dev\\d*|[0-9\\.]+[\\d]+)(\\.(?:language|dom))?""", "\\1\\2", component_name)


def generate_pyproject_file(package_folder: Path, language: str, output_folder: Path):

    wowool_module = "wowool.lxware.wowool"
    package_name = language
    logger.debug(f"Template variables: {wowool_module=}{package_name=}")
    pyproject_fn = output_folder / "pyproject.toml"
    repo_version = get_version()
    lxware = output_folder / "src/wowool/lxware/wowool"
    domains_ = []
    for fn in lxware.glob("*.dom_info"):
        dom_info = json.loads(fn.read_text())
        print("dom_info----->>>>>>", dom_info)
        name = strip_version(fn.name)
        dom_text = f"### {name}\n"

        dom_text += """\n| Entity | Description | Sample |"""
        dom_text += """\n| ------ | ----------- | ------ |"""
        for sample in dom_info["examples"]:
            dom_text += f"""\n| {sample['concept']} |{sample['desc']} | {sample['sample']} |"""
        dom_text += "\n\n"
        domains_.append(dom_text)

    domains = "\n".join(domains_)

    readme_fn = output_folder / "README.md"
    readme_fn.write_text(resolve_template(README_TEMPLATE, globals(), locals()))

    setup_py_install_requirement = ""

    clean_python_build_folders(output_folder)
    # !! do not remove it's used to resolve
    # setup_py_install_requirement = f"install_requires={json.dumps(setup_dependencies)}"
    # logger.debug(f"Template variables: {setup_py_install_requirement=}")

    filename = package_folder / pyproject_fn
    try:
        with open(filename, "w") as fp_mf:
            fp_mf.write(resolve_template(PACKAGE_PYPROJECT_TEMPLATE, globals(), locals()))
        return pyproject_fn
    except Exception as ex:
        logger.exception(ex)
        filename.unlink(missing_ok=True)
