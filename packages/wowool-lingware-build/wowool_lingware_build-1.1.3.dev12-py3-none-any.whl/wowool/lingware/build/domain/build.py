import json
from subprocess import run
from pathlib import Path
import shutil
import logging
from wowool.lingware.build.git import get_version
import json
import os
from wowool.lingware.build.utilities import (
    resolve_template,
    PREFIX_DO_NOT_EDIT,
    eot_namespace,
    wowool_module,
    get_filename_version,
    get_stage_folder,
    get_stage_lxware_folder,
    get_lxcommon,
    get_language,
    clean_python_build_folders,
)

logger = logging.getLogger(__name__)


def domains(folder: Path):
    for domain in folder.glob("domains/*"):
        if domain.is_dir():
            yield domain


def get_nrof_threads() -> int:
    return int(os.environ["WOWOOL_NROF_THREADS"]) if "WOWOOL_NROF_THREADS" in os.environ else 1


def get_variable(domain_project_fn, jo, varname, ext, location=None, prefix=""):
    if varname in jo:
        formatted_string = "f'''" + jo[varname] + "'''"
        fn = eval(formatted_string)
    else:
        if location:
            language = None
            if "language" in jo:
                language = jo["language"]
            else:
                try:
                    language = Path(domain_project_fn).parts[-4]
                except Exception as ex:
                    logger.warning(
                        f"ACHTUNG :-# could not extract language from path {domain_project_fn}, name {varname}\n{jo}\n, ex: {ex}"
                    )
                    pass
            if language:
                fn = Path(location, f"""{prefix}{language}-{jo['name']}{ext}""")
            else:
                fn = Path(location, f"""{prefix}{jo['name']}{ext}""")
                logger.warning(f"ACHTUNG :-# language not found in the config file {domain_project_fn}, name {varname} using {fn} \n{jo}")

        else:
            fn = Path(domain_project_fn)
            fn = fn.with_suffix(ext)
    return fn


def generate_package_info(domain_folder, dom_file_target, config_file_target, additional_package_files_list):
    with open(domain_folder / "package.json", "w") as fh_pi:
        jpi = {"files": [str(dom_file_target), str(config_file_target)]}
        if additional_package_files_list:
            for additional_package_file in additional_package_files_list:
                jpi["files"].append(str(additional_package_file))
        json.dump(jpi, fh_pi, indent=2)


def generate_domain_makefile(folder: Path, domain_folder: Path):
    nrof_threads = get_nrof_threads()
    version = get_version()
    filename_version = get_filename_version(version)
    addsign_filename_version = f"@{filename_version}"

    # !! do not remove any , it use in a f-string
    # ----------------------------------------------------
    domain_project_fn = domain_folder / "project.json"
    assert domain_project_fn.exists(), f"Missing project file {domain_project_fn}"
    lxcommon_pth = get_lxcommon(folder)
    lxcommon = str(lxcommon_pth)
    repo = folder
    # ----------------------------------------------------

    STAGE_DIR = get_stage_folder(folder)
    lxware = get_stage_lxware_folder(folder)

    if "WOC_EXEC" in os.environ:
        woc_app = os.environ["WOC_EXEC"]

    else:
        executable = Path(STAGE_DIR, "bin").resolve()
        woc_app = f"{executable}/woc"
        if not Path(woc_app).exists():
            woc_app = "woc"

    lxware_eot = lxware / "wowool"

    compiler_options = ""
    with open(domain_project_fn) as fp:
        jo = json.load(fp)

    # Add additional topics information.
    additional_package_files = ""

    cwd = Path(domain_project_fn).parent
    name = Path(domain_project_fn).stem
    if "name" in jo:
        name = jo["name"]
    else:
        if name == "project":
            name = Path(cwd).stem
        jo["name"] = name

    makefile_fn = domain_folder / "makefile._mk"

    language = None
    language = jo["language"] if "language" in jo else get_language(folder)
    language_filename_version = f"{language}@{filename_version}"
    woc_options = ""
    if "WOC_OPTIONS" in os.environ:
        woc_options += f"{os.environ['WOC_OPTIONS']} "

    woc_options = jo["woc_options"] if "woc_options" in jo else woc_options
    if "$WOC_OPTIONS" in woc_options and "WOC_OPTIONS" in os.environ:
        woc_options = woc_options.replace("$WOC_OPTIONS", os.environ["WOC_OPTIONS"])

    dom_info_file_source = f"{language}-{name}.di" if language else f"{name}.di"
    dom_info_file_source = Path(dom_info_file_source)
    dom_info_file_target = Path(f"{dom_info_file_source.stem}@{filename_version}.dom_info")
    dom_info_file_source = Path(cwd, dom_info_file_source)
    dom_info_file_target = Path(lxware_eot, dom_info_file_target)
    if "target_config" in jo:
        formatted_string = "f''' " + jo["target_config"] + "'''"
        dom_info_file_target = eval(formatted_string)
        if not Path(dom_info_file_target).exists():
            print("target_config file not found!!! in {domain_project_fn}")
            exit(-1)

    domain_description = f"{language}-{name}" if language else f"{name}"
    package_name = f"domain-{domain_description}"
    domain_name = f"{domain_description}@{filename_version}.dom"
    dom_file_target = Path(lxware_eot, domain_name)
    domain_name_dash = domain_description.replace("-", "_")
    package_name_dash = package_name.replace("-", "_")

    if "target" in jo:
        formatted_string = "f''' " + jo["target"] + "'''"
        dom_file_target = eval(formatted_string)

    project = folder
    sources = """\\\n"""

    for file in jo["sources"]:
        formatted_string = "f'''\t" + file + """ \\\\\n'''"""
        resolved_fn = eval(formatted_string)
        sources += eval(formatted_string)
        formatted_string = "f'''" + file + "'''"
        fn = eval(formatted_string)

    thread_option = f" -j {nrof_threads} " if nrof_threads > 0 else " "
    additional_package_build_statements = ""
    additional_package_files_list = []
    if "plugins" in jo and "topics" in jo["plugins"]:
        topic_model_file_target = Path(dom_file_target).parent / f"{language}@{filename_version}.topic_model"
        additional_package_files += f" {topic_model_file_target}"
        additional_package_files_list.append(topic_model_file_target)
        additional_package_build_statements = f"""
{topic_model_file_target}: $(DOM_DOM)
\ttoc -l {language}{addsign_filename_version} -f {repo}/semantics/topics/training_data -o $@ --lxware {lxware}

    """

    logger.debug(f"Generate: {makefile_fn}")

    with open(makefile_fn, "w") as fp_mf:
        from wowool.lingware.build.domain.templates import DOMAIN_MAKEFILE_TEMPLATE

        fp_mf.write(resolve_template(DOMAIN_MAKEFILE_TEMPLATE, globals(), locals()))

    # write a file with package info this the files requred to use in the setup
    generate_package_info(domain_folder, dom_file_target, dom_info_file_target, additional_package_files_list)

    return makefile_fn


def get_sorted_projects(folder: Path):
    fns = []

    for domain_folder in domains(folder):
        domain = domain_folder.name
        project_fn = folder / f"domains/{domain}/project.json"
        assert project_fn.exists(), f"Missing project.json in {domain_folder}"

        fns.append(domain_folder)

    postponed_builds = []
    language = get_language(folder)
    for idx, fn in enumerate(fns):
        domain_dir_name = fn.name
        domain_folder = fn
        dom_info_fn = domain_folder / f"{language}-{domain_dir_name}.di"
        logger.debug(f"Check dom_info file: {dom_info_fn}")
        assert dom_info_fn.exists(), f"   ! Missing domain info file: {dom_info_fn}"
        if domain_folder.name == "topics":
            postponed_builds.append({"idx": idx, "project_fn": fn})

    for postponed_build in postponed_builds:
        del fns[postponed_build["idx"]]

    postponed_builds = [item["project_fn"] for item in postponed_builds]
    return {"paralell": fns, "postponed": postponed_builds}


def build_domain(folder: Path, domain_folder: Path):
    """build a domain."""
    print("Building: ", folder, domain_folder)
    makefile_fn = generate_domain_makefile(folder, domain_folder)
    compile_paralell(folder, [makefile_fn])


def compile_paralell(folder: Path, makefiles, target=""):
    from subprocess import run

    makefile_all_fn = folder / "MakeAll._mk"
    with open(makefile_all_fn, "w") as fh:
        fh.write("all:")
        for makefile in makefiles:
            fh.write(f"{makefile.parent.stem}_make ")
        fh.write("\n")
        for makefile in makefiles:
            fh.write(f"{makefile.parent.stem}_make:\n")
            fh.write(f"\t cd {makefile.parent} ; make -f {makefile.name} {target}\n\n")

    compiler_options_fn = folder / "woc_options.json"
    if compiler_options_fn.exists():
        with open(compiler_options_fn) as fh:
            woc_jo = json.load(fh)
            if "WOC_OPTIONS" in woc_jo:
                args = woc_jo["WOC_OPTIONS"]
                os.environ["WOC_OPTIONS"] = args
                print("SETTING: WOC_OPTIONS", os.environ["WOC_OPTIONS"])

    threads = get_nrof_threads()
    cmd = f"make -f {makefile_all_fn} -j {threads}"
    logger.debug(f"paralell: {cmd=}")
    run(cmd, shell=True, check=True)


def build_domains(folder):
    """build all the domains."""

    build_type = get_sorted_projects(folder)

    makefiles = []
    for domain_folder in build_type["paralell"]:
        makefile_fn = generate_domain_makefile(folder, domain_folder)
        makefiles.append(makefile_fn)

    if makefiles:
        compile_paralell(folder, makefiles)

    makefiles = []
    for domain_folder in build_type["postponed"]:
        makefile_fn = generate_domain_makefile(folder, domain_folder)
        makefiles.append(makefile_fn)

    if makefiles:
        compile_paralell(folder, makefiles)


def get_project_info(domain_folder: Path):
    package_json_fn = domain_folder / "project.json"
    if package_json_fn.exists():
        with open(package_json_fn) as fh:
            return json.load(fh)
    return {}


def get_package_info(domain_folder: Path):
    package_json_fn = domain_folder / "package.json"
    if package_json_fn.exists():
        with open(package_json_fn) as fh:
            return json.load(fh)
    return {}


def get_dom_info(domain_folder: Path):
    di_fn = [fn for fn in domain_folder.glob("*.di")][0]
    with open(di_fn) as fh:
        return json.load(fh)
    return {}


def clean_domain(folder: Path, domain_folder: Path):
    package_info = get_package_info(domain_folder)
    if "files" in package_info:
        for fn in package_info["files"]:
            Path(fn).unlink(missing_ok=True)
    Path(domain_folder / "makefile._mk").unlink(missing_ok=True)
    Path(domain_folder / "package.json").unlink(missing_ok=True)
    clean_python_build_folders(domain_folder)
    shutil.rmtree(f"{domain_folder}/wowool", ignore_errors=True)
    for egg_info in domain_folder.glob("*.egg-info"):
        shutil.rmtree(egg_info, ignore_errors=True)
    Path(f"{folder}/setup.py").unlink(missing_ok=True)


def clean_domains(folder):
    for domain_folder in domains(folder):
        clean_domain(folder, domain_folder)


def generate_domain_setupfile(domain_folder: Path, jo_domain_info, package_name, language):
    eot_namespace = "wowool-lxware"
    wowool_module = "wowool.lxware.wowool"
    lxware_namespace = "wowool-lxware"
    logger.debug(f"Template variables: {eot_namespace=}{wowool_module=}{lxware_namespace=}")
    setup_fn = "setup.py"
    eot_namespace_dash = eot_namespace.replace("-", "_")
    repo_version = get_version()

    setup_py_install_requirement = ""
    setup_dependencies = [f"{eot_namespace_dash}_language_{language}_basic=={repo_version}"]
    if "dependencies" in jo_domain_info:
        dom_info_dependencies = jo_domain_info["dependencies"]
        setup_dependencies.extend([f"{eot_namespace_dash}_domain_{dep}=={repo_version}".replace("-", "_") for dep in dom_info_dependencies])

    clean_python_build_folders(domain_folder)
    # !! do not remove it's used to resolve
    setup_py_install_requirement = f"install_requires={json.dumps(setup_dependencies)}"
    logger.debug(f"Template variables: {setup_py_install_requirement=}")

    setup_filename = domain_folder / setup_fn
    try:
        with open(setup_filename, "w") as fp_mf:
            from wowool.lingware.build.domain.templates import DOMAIN_SETUP_TEMPLATE

            fp_mf.write(resolve_template(DOMAIN_SETUP_TEMPLATE, globals(), locals()))
        return setup_fn
    except Exception as ex:
        logger.exception(ex)
        setup_filename.unlink(missing_ok=True)


def package_domain(folder: Path, domain_folder: Path, package_lxware_wowool: Path | None = None, run_setup: bool = True):
    package_info = get_package_info(domain_folder)
    assert "files" in package_info, "missing the file section in the package.json of {domain_folder}"
    if package_lxware_wowool is None:
        dst_folder = domain_folder / "wowool/lxware/wowool"
    else:
        dst_folder = package_lxware_wowool
    shutil.rmtree(domain_folder / "wowool", ignore_errors=True)
    dst_folder.mkdir(parents=True, exist_ok=True)
    for fn in package_info["files"]:
        shutil.copy(fn, dst_folder)

    jo_domain_info = get_dom_info(domain_folder)
    language = get_language(folder)
    name = domain_folder.name
    domain_description = f"{language}-{name}" if language else f"{name}"

    package_name = f"domain-{domain_description}"

    if run_setup:
        generate_domain_setupfile(domain_folder, jo_domain_info, package_name, language)
        logger.debug(f"Run setup.py in {domain_folder}")
        run("python setup.py bdist_wheel", cwd=domain_folder, shell=True)


def package_domains(folder: Path, package_lxware_wowool: Path | None = None, run_setup: bool = True):
    for domain_folder in domains(folder):
        package_domain(folder, domain_folder, package_lxware_wowool=package_lxware_wowool, run_setup=run_setup)


def upload_domain(folder: Path, domain_folder: Path):
    from wowool.build.codeartifact import upload_pypi

    upload_pypi(domain_folder)


def upload_domains(folder: Path):
    for domain_folder in domains(folder):
        upload_domain(folder, domain_folder)


def load_domain_tasks(folder, collection_name=None):
    code = """
from wowool.lingware.build.domain.build import build_domain, clean_domain, package_domain, upload_domain

    """

    for domain_folder in domains(folder):
        domain_name = domain_folder.name
        domain_function_name = domain_name.replace("-", "_")
        code += f"""


@task(name = '{domain_function_name}/build' )
def build_{domain_function_name}( context  ):
    \"\"\" Build the '{domain_name}' Domain. \"\"\"
    from wowool.lingware.build.domain.build import build_domain
    build_domain( Path.cwd(), Path("{domain_folder}") )

if {collection_name}:
    {collection_name}.add_task(build_{domain_function_name})

@task(name = '{domain_function_name}/clean' )
def clean_{domain_function_name}( context ):
    \"\"\" Clean the '{domain_name}' Domain. \"\"\"
    from wowool.lingware.build.domain.build import clean_domain
    clean_domain( Path.cwd(), Path("{domain_folder}") )

if {collection_name}:
    {collection_name}.add_task(clean_{domain_function_name})
    
@task(name = '{domain_function_name}/package' )
def package_{domain_function_name}( context ):
    \"\"\" Package the '{domain_name}' Domain. (setup.py) \"\"\"
    THIS_DIR = Path(__file__).parent
    from wowool.lingware.build.domain.build import package_domain
    package_domain( THIS_DIR, Path("{domain_folder}") )

if {collection_name}:
    {collection_name}.add_task(package_{domain_function_name})

@task(name = '{domain_function_name}/upload' )
def upload_{domain_function_name}( context ):
    \"\"\" Upload the '{domain_name}' Domain to nexus \"\"\"
    THIS_DIR = Path(__file__).parent
    from wowool.lingware.build.domain.build import upload_domain
    upload_domain( THIS_DIR, Path("{domain_folder}") )

if {collection_name}:
    {collection_name}.add_task(upload_{domain_function_name})



"""

    # @task(name = '{domain_function_name}' )
    # def action_{domain_function_name}( context , action ):
    #     THIS_DIR = Path(__file__).parent
    #     if action == "test":
    #         lingware_tasks.unittest_folder(context, THIS_DIR, verbose=False, diff="meld", overwrite=False, pattern="**/*.txt")
    #     elif action == "test_dictionaries":
    #         lingware_tasks.unittest_folder(context, THIS_DIR, verbose=False, diff="meld", overwrite=False, pattern="**/*.txt")
    #     else:
    #         lingware_tasks.build_domains( context, THIS_DIR, "{domain_name}" , target=action )

    # print(code)
    return code
