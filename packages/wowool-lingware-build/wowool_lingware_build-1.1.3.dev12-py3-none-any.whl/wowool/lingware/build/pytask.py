from os import getcwd
from pathlib import Path
from typing import Union

from invoke.collection import Collection
from invoke.tasks import task
from logging import getLogger
from shutil import rmtree

logger = getLogger("wowool.lingware.build")


def create_py_tasks(fp_root: Union[str, Path, None] = None) -> Collection:
    fp_root = Path(fp_root) if fp_root is not None else Path(getcwd())
    if fp_root.is_file():
        fp_root = fp_root.parent

    _ns = Collection()

    @task
    def version(c):
        from wowool.lingware.build.git import get_version

        print(get_version())

    _ns.add_task(version)

    @task
    def build_languages(_):
        """
        build the basic morphology files.
        """
        from wowool.lingware.build.language import make_language

        make_language(fp_root)

    _ns.add_task(build_languages)

    @task
    def build_domains(_):
        """Build all the domain files."""

        from wowool.lingware.build.domain import build_domains

        build_domains(fp_root)

    _ns.add_task(build_domains)

    @task(pre=[build_languages, build_domains])
    def build(_):
        """
        build the complete language module.
        """
        pass

    _ns.add_task(build)

    # --------------------------------------------------------------------------------------

    @task(pre=[build_languages])
    def package_languages(_):
        """
        build the basic morphology files.
        """
        from wowool.lingware.build.language import package_languages

        package_languages(fp_root)

    _ns.add_task(package_languages)

    @task(pre=[build_domains])
    def package_domains(_):
        """upload domains all the domain file."""
        from wowool.lingware.build.domain import package_domains

        package_domains(fp_root)

    _ns.add_task(package_domains)

    @task(pre=[package_languages, package_domains])
    def package(_):
        pass

    @task
    def package_all(_, clean: bool = True):
        from wowool.lingware.build.language import package_languages
        from wowool.lingware.build.domain import package_domains
        from wowool.lingware.build.build import generate_pyproject_file
        from subprocess import run

        output_folder = fp_root / "_build_package"
        if clean:
            rmtree(output_folder, ignore_errors=True)
        lxware_src = output_folder / "src/wowool/lxware/wowool"

        print(f"Package languages and domains in {fp_root} to {lxware_src}")
        package_languages(fp_root, package_lxware_wowool=lxware_src, run_setup=False)
        print(f"Package domains and domains in {fp_root} to {lxware_src}")
        package_domains(fp_root, package_lxware_wowool=lxware_src, run_setup=False)
        generate_pyproject_file(fp_root, fp_root.name, output_folder=output_folder)
        logger.debug(f"Run build package in {output_folder}")
        run(f"python -m build --wheel {output_folder}", cwd=output_folder, shell=True)

    _ns.add_task(package_all)

    # --------------------------------------------------------------------------------------

    @task
    def upload_all(_):
        """
        deploy all the language and domains packages.
        """
        from wowool.build.pypi import upload_pypi

        output_folder = fp_root / "_build_package"
        if output_folder.exists():
            upload_pypi(output_folder)
        else:
            raise FileNotFoundError(f"Folder {output_folder} not found.")

    _ns.add_task(upload_all)

    @task
    def upload_languages(_):
        """
        deploy all the language packages.
        """
        from wowool.lingware.build.language import upload_languages

        upload_languages(fp_root)

    _ns.add_task(upload_languages)

    @task
    def upload_domains(_):
        """
        deploy all the domains packages.
        """
        from wowool.lingware.build.domain import upload_domains

        upload_domains(fp_root)

    _ns.add_task(upload_domains)

    @task(post=[upload_languages, upload_domains])
    def upload(_):
        """
        deploy all the package.
        """
        from wowool.lingware.build.language import upload_languages
        from wowool.lingware.build.domain import upload_domains

        upload_languages(fp_root)
        upload_domains(fp_root)

    _ns.add_task(upload)

    # --------------------------------------------------------------------------------------
    @task
    def clean_domains(_):
        """Clean all the domain files."""
        from wowool.lingware.build.domain import clean_domains

        clean_domains(fp_root)

    _ns.add_task(clean_domains)

    @task
    def clean_languages(_):
        """
        cleans the language folder.
        """
        from wowool.lingware.build.language import make_language

        make_language(fp_root, "clean")

    _ns.add_task(clean_languages)

    @task(pre=[clean_languages, clean_domains])
    def clean(_):
        """
        cleans the language and domains.
        """
        pass

    _ns.add_task(clean)

    @task
    def test_domains(context, domains="*", target="", verbose=False, j=1):
        """test all the domain files."""

        from wowool.lingware.unittest.unittest import test_domains

        test_domains(fp_root)

    _ns.add_task(test_domains)

    @task
    def test_wheels(context, domains="*", target="", verbose=False, j=1):
        """test all the domain files."""

        from wowool.lingware.unittest.unittest import test_wheels

        test_wheels(fp_root)

    _ns.add_task(test_wheels)

    @task(
        help={
            "verbose": "print the results on screen",
            "diff": "app used for the diff, default(meld)",
            "overwrite": "generate the expected result file",
            "pattern": "glob pattern to run, default **/*.txt",
        }
    )
    def test(context, verbose=False, diff="meld", overwrite=False, pattern="**/*.txt", integration=False):
        """
        start the unit-test.
        """
        from wowool.lingware.unittest.unittest import run_test_folder

        run_test_folder(context, fp_root, verbose, diff, overwrite, pattern, integration)

    _ns.add_task(test)

    from wowool.lingware.build.domain import load_domain_tasks

    exec(load_domain_tasks(fp_root, "_ns"))

    return _ns


# Allow both default Invoke namespaces to be available for import
ns = create_py_tasks()
namespace = ns
