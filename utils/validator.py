import json
import os
from pathlib import Path
from typing import Dict, List, Tuple


class InvalidInputFormatError(Exception):
    pass


class InvalidSolversFormatError(Exception):
    pass


class InvalidEdgeFormatError(Exception):
    pass


class InvalidVariableError(Exception):
    pass


class InvalidPathError(Exception):
    pass


class InvalidCsvPathError(InvalidPathError):
    pass


class InvalidUaiPathError(InvalidPathError):
    pass


class InvalidMappingFormatError(Exception):
    pass


class Validator:
    def __init__(self):
        pass

    def is_valid_string(self, s: str) -> bool:
        if s is None:
            return False
        if not isinstance(s, str):
            return False
        if s.strip() == "":
            return False
        return True

    def get_valid_test_name(self, test_name: str) -> str:
        if not self.is_valid_string(test_name):
            raise Exception(f"Invalid test name: {test_name}.")
        return test_name

    def get_valid_solver_list(self, solvers_str: str) -> List[str]:
        if not self.is_valid_string(solvers_str):
            raise InvalidSolversFormatError(
                f"Invalid solvers format: {solvers_str}.")
        try:
            return solvers_str.lower().split(' ')
        except Exception as e:
            raise InvalidSolversFormatError(
                f"Invalid solvers format: {solvers_str}.{e}.") from e

    def get_valid_edge_tuple_list(
        self, edges_str: str
    ) -> List[Tuple[str, str]]:
        edges = []
        for edge in edges_str.split(', '):
            nodes = edge.split(' -> ')
            if len(nodes) != 2 or not nodes[0].strip() or not nodes[1].strip():
                raise InvalidEdgeFormatError(
                    f"Invalid format for edge: '{edge}'")
            edges.append((nodes[0].strip(), nodes[1].strip()))
        return edges

    def get_valid_edges_in_string(
        self, edges_str: str
    ) -> Tuple[str, List[Tuple[str, str]]]:
        if not self.is_valid_string(edges_str):
            raise InvalidEdgeFormatError(
                f"Invalid edges format: '{edges_str}'.")
        edges_str = edges_str.upper()
        edges_list = self.get_valid_edge_tuple_list(edges_str)
        return edges_str, edges_list

    def get_valid_variable(self, var: str, edges: str) -> str:
        if not self.is_valid_string(var):
            raise InvalidVariableError(f"Invalid variable: '{var}'.")
        if var.upper() not in edges:
            raise InvalidVariableError(
                f"Invalid variable: '{var}'. Not present in the edges.")
        return var.upper()

    def get_valid_unobservables(self, vars: str, edges: str) -> str:
        if not self.is_valid_string(vars):
            raise InvalidVariableError(
                f"Invalid string of variables: '{vars}'.")
        if vars == "-":
            return None
        unobs = vars.split(',')
        for var in unobs:
            if var.strip().upper() not in edges:
                raise InvalidVariableError(
                    f"Invalid variable: '{var}'. Not present in the edges.")
        return var.upper()

    def get_valid_mapping(self, mapping: str) -> Dict:
        if not self.is_valid_string(mapping):
            raise InvalidMappingFormatError(
                f"Invalid format for mapping variables from input: "
                f"'{mapping}'.")
        try:
            return json.loads(mapping.upper())
        except json.JSONDecodeError as e:
            raise InvalidMappingFormatError(
                f"Invalid format for mapping variables from input: "
                f"'{mapping}'. {e}"
            ) from e
        except Exception as e:
            raise InvalidMappingFormatError(
                f"An unexpected error occurred while processing the mapping: "
                f"'{mapping}'.") from e

    def is_valid_path(self, path_str: str) -> bool:
        if os.path.exists(path_str):
            return True
        return Path(path_str).exists()

    def get_valid_path(self, path: str) -> str:
        if not self.is_valid_path(path):
            raise InvalidPathError(
                f"Invalid path: '{path}'. Please provide a valid path.")
        return path

    def get_valid_csv_path(self, path: str, check_path: bool = True) -> str:
        if check_path:
            self.get_valid_path(path)
        if not path.endswith('.csv'):
            raise InvalidCsvPathError(
                f"Invalid CSV path: '{path}'. "
                f"Please provide a valid CSV path.")
        return path

    def get_valid_uai_path(self, path: str, check_path: bool = True) -> str:
        if check_path:
            self.get_valid_path(path)
        if not path.endswith('.uai'):
            raise InvalidUaiPathError(
                f"Invalid UAI path: '{path}'. "
                f"Please provide a valid UAI path.")
        return path
