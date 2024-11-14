import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

'''
'
'
Test Name Validator
'
'
'''


def is_valid_string(s: str) -> bool:
    if s is None:
        return False
    if not isinstance(s, str):
        return False
    if s.strip() == "":
        return False
    return True


'''
'
'
Test Name Validator
'
'
'''


def get_valid_test_name(test_name: str) -> str:
    if not is_valid_string(test_name):
        raise Exception(f"Invalid test name: {test_name}.")
    return test_name


'''
'
'
Solvers Validator
'
'
'''


class InvalidSolversFormatError(Exception):
    pass


def get_valid_solver_list(solvers_str: str) -> List[str]:
    if not is_valid_string(solvers_str):
        raise InvalidSolversFormatError(f"Invalid solvers format: {solvers_str}.")
    try:
        return solvers_str.lower().split(' ')
    except Exception as e:
        raise InvalidSolversFormatError(f"Invalid solvers format: {solvers_str}.{e}.") from e


'''
'
'
Edges Validator
'
'
'''


class InvalidEdgeFormatError(Exception):
    pass


def get_valid_edge_tuple_list(edges_str: str) -> List[Tuple[str, str]]:
    edges = []
    for edge in edges_str.split(', '):
        nodes = edge.split(' -> ')
        if len(nodes) != 2 or not nodes[0].strip() or not nodes[1].strip():
            raise InvalidEdgeFormatError(f"Invalid format for edge: '{edge}'")
        edges.append((nodes[0].strip(), nodes[1].strip()))
    return edges


def get_valid_edges_in_string(edges_str: str) -> Tuple[str, List[Tuple[str, str]]]:
    if not is_valid_string(edges_str):
        raise InvalidEdgeFormatError(f"Invalid edges format: '{edges_str}'.")
    edges_str = edges_str.upper()
    edges_list = get_valid_edge_tuple_list(edges_str)
    return edges_str, edges_list


'''
'
'
Variable Validator
'
'
'''


class InvalidVariableError(Exception):
    pass


def get_valid_variable(var: str, edges: str) -> str:
    if not is_valid_string(var):
        raise InvalidVariableError(f"Invalid variable: '{var}'.")
    if var.upper() not in edges:
        raise InvalidVariableError(f"Invalid variable: '{var}'. Not present in the edges.")
    return var.upper()


def get_valid_unobservable(var: str, edges: str) -> str:
    if not is_valid_string(var):
        raise InvalidVariableError(f"Invalid variable: '{var}'.")
    if var == "-":
        return None
    if var.upper() not in edges:
        raise InvalidVariableError(f"Invalid variable: '{var}'. Not present in the edges.")
    return var.upper()


'''
'
'
Mapping Validator
'
'
'''


class InvalidMappingFormatError(Exception):
    pass


def get_valid_mapping(mapping: str) -> Dict:
    if not is_valid_string(mapping):
        raise InvalidMappingFormatError(f"Invalid format for mapping variables from input: '{mapping}'.")
    try:
        return json.loads(mapping.upper())
    except json.JSONDecodeError as e:
        raise InvalidMappingFormatError(f"Invalid format for mapping variables from input: '{mapping}'. {e}") from e
    except Exception as e:
        raise InvalidMappingFormatError(f"An unexpected error occurred while processing the mapping: '{mapping}'.") from e


'''
'
'
Path Validator
'
'
'''


class InvalidPathError(Exception):
    pass


def is_valid_path(path_str: str) -> bool:
    if os.path.exists(path_str):
        return True
    return Path(path_str).exists()


def get_valid_path(path: str) -> str:
    if not is_valid_path(path):
        raise InvalidPathError(f"Invalid path: '{path}'. Please provide a valid path.")
    return path
