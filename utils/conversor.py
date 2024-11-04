from typing import List, Tuple


def convert_str_edges_into_a_tuple_list(edges_str: str) -> List[Tuple[str, str]]:
    if ' -> ' not in edges_str:
        # TODO ERROR exception
        return None
    return [tuple(edge.split(' -> ')) for edge in edges_str.split(', ')]

