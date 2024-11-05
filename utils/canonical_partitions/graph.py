class Graph:
    def __init__(
        self, num_nodes: int, curr_nodes: list[int], visited: list[bool],
        cardinalities: list[int], parents: list[int], adj: list[list[int]],
        label_to_index: dict[str, int], index_to_label: dict[int, str],
        dag_components: list[list[int]], exogenous: list[int],
        endogenous: list[int]
    ):
        self.num_nodes = num_nodes
        self.curr_nodes = curr_nodes
        self.visited = visited
        self.cardinalities = cardinalities
        self.parents = parents
        self.adj = adj
        self.label_to_index = label_to_index
        self.index_to_label = index_to_label
        self.dag_components = dag_components
        self.endogenous = endogenous
        self.exogenous = exogenous

    def parse(predefined_data=None, input_path=None):
        if predefined_data:
            num_nodes = predefined_data['num_nodes']
            num_edges = predefined_data['num_edges']
        elif input_path:
            num_nodes, num_edges, nodes, nodes_cardinality, edges = file_parser(input_path)
        else:
            num_nodes = int(input())
            num_edges = int(input())

        label_to_index_ex: dict[str, int] = {}
        index_to_label_ex: dict[int, str] = {}
        adj_ex = [[] for _ in range(num_nodes + 1)]
        cardinalities_ex = [0] * (num_nodes + 1)
        visited_ex = [False] * (num_nodes + 1)
        parents_ex = [[] for _ in range(num_nodes + 1)]
        endogenIndex: list[int] = []
        exogenIndex: list[int] = []

        for i in range(1, num_nodes + 1):
            if predefined_data:
                label, cardinality = predefined_data['nodes'][i - 1].split()
            elif input_path:
                label, cardinality = nodes[i-1], nodes_cardinality[i-1]
            else:
                label, cardinality = input().split()
            cardinality = int(cardinality)
            label_to_index_ex[label] = i
            index_to_label_ex[i] = label
            cardinalities_ex[i] = cardinality

        for i in range(num_edges):
            if predefined_data:
                u, v = predefined_data['edges'][i].split(" -> ")
            elif (input_path):
                print(edges[i])
                u, v = edges[i]
            else:
                u, v = input().split()
            u_index = label_to_index_ex[u]
            v_index = label_to_index_ex[v]
            adj_ex[u_index].append(v_index)
            parents_ex[v_index].append(u_index)

        for i in range(1, num_nodes + 1):

            if not (bool(parents_ex[i])):
                exogenIndex.append(i)
            else:
                endogenIndex.append(i)

        return Graph(
            num_nodes=num_nodes,
            curr_nodes=[],
            visited=visited_ex,
            cardinalities=cardinalities_ex,
            parents=parents_ex,
            adj=adj_ex,
            index_to_label=index_to_label_ex,
            label_to_index=label_to_index_ex,
            dag_components=[],
            exogenous=exogenIndex,
            endogenous=endogenIndex
        )

def file_parser(input_path):
    with open(input_path, 'r') as file:
        num_nodes = int(file.readline().strip())
        num_edges = int(file.readline().strip())
        nodes = []
        nodes_cardinality = []

        for _ in range(num_nodes):
            tuple_node_cardinality = file.readline().strip().split(' ')
            node = tuple_node_cardinality[0]
            cardinality = int(tuple_node_cardinality[1])
            nodes.append(node)
            nodes_cardinality.append(cardinality)
        edges = []
        for _ in range(num_edges):
            edge = file.readline().strip().split(' ')
            origin_node = edge[0]
            target_node = edge[1]
            edges.append((origin_node, target_node))
        return num_nodes, num_edges, nodes, nodes_cardinality, edges
