import os
import subprocess
import sys

from .os_utils import get_parent_process_params, get_cwd


class PipIdxSource(object):
    def __init__(self, idx_id):
        self.idx_id = idx_id
        self.args = []
        self.idxs = []
        self.error_code = None

    def set_error_code(self, code):
        self.error_code = code


def parse_requirements_from_args(arg_list):

    from pip._internal.commands import create_command
    from pip._internal.commands.install import InstallCommand
    from pip._internal.network.session import PipSession
    from pip._internal.index.package_finder import PackageFinder
    from pip._internal.index.collector import LinkCollector
    from pip._internal.models.search_scope import SearchScope
    from pip._internal.models.selection_prefs import SelectionPreferences
    from typing import cast

    idx_urls = set()
    pkgs = set()
    session = PipSession()

    link_collector = LinkCollector(
        session=session, search_scope=SearchScope([], [], False),)
    finder = PackageFinder.create(
        link_collector=link_collector, selection_prefs=SelectionPreferences(allow_yanked=True))

    command = cast(InstallCommand, create_command('install'))
    options, args = command.parse_args(arg_list)
    option_dict = vars(options)
    idx_urls.update(option_dict['extra_index_urls'])
    idx_urls.add(option_dict['index_url'])
    parsed_requirements = command.get_requirements(
        args, options, finder, session)

    # This loop is required or the index_urls will not be populated
    for req_inst in parsed_requirements:
        req_str = getattr(req_inst, "requirement", None) or getattr(
            req_inst, "req", None)
        if req_str:
            pkgs.add(req_str.name)

    idx_urls.update(finder.search_scope.index_urls)

    return pkgs, idx_urls


def parse_requirements_with_finder(req_file_path):

    from pip._internal.req import parse_requirements
    from pip._internal.network.session import PipSession
    from pip._internal.index.package_finder import PackageFinder
    from pip._internal.index.collector import LinkCollector
    from pip._internal.models.search_scope import SearchScope
    from pip._internal.models.selection_prefs import SelectionPreferences

    session = PipSession()

    link_collector = LinkCollector(
        session=session, search_scope=SearchScope([], [], False),)
    finder = PackageFinder.create(
        link_collector=link_collector, selection_prefs=SelectionPreferences(allow_yanked=True))

    # Parse the requirements file, providing the finder.
    parsed_requirements = parse_requirements(
        req_file_path,
        session=session,
        finder=finder
    )

    # This loop is required or the index_urls will not be populated
    for req_inst in parsed_requirements:
        req_str = getattr(req_inst, "requirement", None) or getattr(
            req_inst, "req", None)

    return finder.search_scope.index_urls


def get_pip_config_output():
    # Create a copy of the environment variables
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)

    # Build the subprocess command
    command = [sys.executable, '-m', 'pip', 'config', 'list']

    # Run the subprocess command and capture its output
    result = subprocess.run(command, env=environment,
                            capture_output=True, text=True)
    output_lines = result.stdout.splitlines()

    return output_lines


def get_pip_index_list():

    parent_args = get_parent_process_params()
    if "-r" in parent_args:
        index = parent_args.index("-r")
        req_file_path = parent_args[index + 1]
        if not os.path.isabs(req_file_path):
            req_file_path = os.path.abspath(
                os.path.join(get_cwd(), req_file_path))
            parent_args[index + 1] = req_file_path

    if 'install' in parent_args:
        index = parent_args.index("install")
        pip_args = parent_args[index+1:]
        return parse_requirements_from_args(pip_args)
    else:
        return [], []


def pip_install(pkg_name, pkg_version, idx_map):
    """
    Registers a package using pip with the provided arguments and registration info.

    Args:
        package_name (str): The name of the package to register.
        package_version (str): The version of the package to register.
        argument_map (dict): A dictionary of additional arguments to pass to pip.
        registration_info (list): A list to store registration results.
    """

    ret_val = '6'
    for idx_url in idx_map.values():
        # Create a copy of the environment variables and remove PYTHONPATH if it exists
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)

        # Build the pip command
        cmd = [sys.executable, '-m', 'pip',
               'install', '--extra-index-url',  idx_url]
        cmd.append(f'"{pkg_name}<{pkg_version}"')

        # Run the pip command and handle errors
        try:
            res = subprocess.run(
                cmd, env=env, capture_output=True, text=True)
            if "No matching distribution found" in res.stderr:
                ret_val = '56'
            else:
                break
        except Exception:
            ret_val = '57'

    # Append the registration result
    return ret_val
