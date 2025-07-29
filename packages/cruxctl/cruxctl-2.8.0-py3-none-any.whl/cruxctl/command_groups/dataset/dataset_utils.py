"""
Utility routines for the dataset command group.
"""

import asyncio
import os
import re
from pathlib import Path
from typing import List

import typer
from crux_odin.dict_utils import YAMLFileClosures, yaml_file_to_dict
from rich.console import Console

error_console = Console(stderr=True)


def get_yaml_file_closures(
    start_directory: str, yaml_files: List[str]
) -> List[List[str]]:
    """
    Returns lists of lists of parent/children in groups. These groups have to be coalesced
    and processed as a single YAML for each group.

    :param str start_directory: The directory to start looking for the YAML file and its parent.
    :param List[str] yaml_files: The YAML file to apply (with an optional parent). This must
    be a file reference and not a path (relative or absolute).
    """
    assert start_directory and isinstance(start_directory, str)
    assert yaml_files and isinstance(yaml_files, List)

    if not os.path.isdir(start_directory):
        error_console.print(f"Directory {start_directory} does not exist.")
        raise typer.Exit(1)
    shortened_yaml_list = []
    for file in yaml_files:
        if not re.compile(r"\.yaml$").search(str(file)):
            error_console.print(f"YAML file {file} must end in .yaml.")
            raise typer.Exit(1)
        if os.sep in str(file):
            # We are going to search below start_directory for the file so we don't need
            # the path portion. We don't allow two files with the same name so that shouldn't
            # be an issue.
            file = os.path.basename(file)
        shortened_yaml_list.append(file)

    yaml_full_paths = []
    for yaml_file in shortened_yaml_list:
        glob_generator = Path(start_directory).rglob(yaml_file)
        glob_path_list = [*glob_generator]
        assert (
            len(glob_path_list) <= 1
        ), f"Found more than one {yaml_file} in {start_directory}"
        if not glob_path_list:
            error_console.print(
                f"YAML file {yaml_file} not found in {start_directory}."
            )
            raise typer.Exit(1)
        yaml_full_paths.append(str(glob_path_list[0]))

    pathlib_list_of_list = asyncio.run(
        YAMLFileClosures(*yaml_full_paths, src_dir=start_directory).get_lists()
    )
    return pathlib_list_of_list


def verify_yaml_file_names_and_if_they_exist(yaml_files: List[str]):
    """
    Verifies that the file has the name '*.yaml' and that it exists.
    :param List[str] yaml_files: The YAML files to validate. These must be file references.
    """
    assert all(isinstance(s, str) for s in yaml_files)
    for file in yaml_files:
        if not re.compile(r"\.yaml$").search(file):
            error_console.print(f"YAML file {file} must end in .yaml.")
            raise typer.Exit(1)
        if not os.path.isfile(file):
            error_console.print(f"YAML file {file} does not exist.")
            raise typer.Exit(1)


def verify_parent_relationships_of_coalesced_files(yaml_files: List[str]):
    """
    Verifies that the YAML files passed have parent relationships between them. Prints
    warnings if they don't.
    :param List[str] yaml_files: YAML files to check for parent relationships.
    """
    assert (
        yaml_files
        and isinstance(yaml_files, list)
        and all(isinstance(s, str) for s in yaml_files)
        and all(re.compile(r"\.yaml$").search(file) for file in yaml_files)
    )

    file_path: dict = {}
    parent: dict = {}
    for yf in yaml_files:
        dict_from_yaml = yaml_file_to_dict(yf)
        if "id" not in dict_from_yaml:
            raise ValueError(f"YAML file {yf} does not have an 'id' field.")
        id = dict_from_yaml["id"]
        file_path[id] = yf
        file_stem = os.path.splitext(os.path.basename(yf))[0]
        if file_stem != id:
            error_console.print(
                f"YAML file {yf} has an 'id' field {id} that does not match the filename."
            )
        if "parent" in dict_from_yaml:
            no_path_parent = os.path.splitext(
                os.path.basename(dict_from_yaml["parent"])
            )[0]
            parent[id] = no_path_parent
    for k, v in parent.items():
        if v not in file_path:
            error_console.print(f"Parent {v} of {file_path[k]} does not exist.")
    if len(parent) != len(file_path) - 1:
        error_console.print(
            f"Not all YAML files of {yaml_files} have a parent relationship."
        )


def parse_cmd_line_yaml_lists(yamls: List[str]) -> List[List[str]]:
    """
    Parses the validate command line arguments, looks for parent/child relationships
    and returns lists of lists of files to concatenate together. The returned lists
    may contain relative or absolute paths.
    :param str yamls: The YAML files to validate. There are two modes: 1) Simple
    path names where parent/child relationships are given by separating the
    YAML files by commas and 2) First you give a directory. Then you give YAML
    file names below that directory. The command will search below the directory for
    the YAML file with that name and use it and also if the YAML file is a parent
    or a child, it will find the companion file and return that too.
    :return: List of lists of YAML files which can be absolute or relative paths,
    but the files have been verified to exist.
    """

    assert yamls and isinstance(yamls, list) and all(isinstance(s, str) for s in yamls)

    first_yaml = yamls[0]
    if os.path.isdir(first_yaml):
        start_directory = first_yaml
        yaml_files = yamls[1:]
        # get_yaml_files_closures() checks for file extensions and existence.
        return get_yaml_file_closures(start_directory, yaml_files)

    pathlib_list_of_list = []
    for yaml_file in yamls:
        if "," in yaml_file:
            split_yamls = yaml_file.split(",")
            verify_yaml_file_names_and_if_they_exist(split_yamls)
            # Now check the files being coalesced and warn if there aren't
            # parent relationships in the files.
            verify_parent_relationships_of_coalesced_files(split_yamls)
            pathlib_list_of_list.append(split_yamls)
        else:
            verify_yaml_file_names_and_if_they_exist([yaml_file])
            pathlib_list_of_list.append([yaml_file])
    return pathlib_list_of_list
