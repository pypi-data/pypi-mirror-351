import networkx as nx
from pydantic import BaseModel

def get_zero_outdeg_nodes(G: nx.DiGraph) -> list:
    """Get nodes with zero outdegree in a directed graph."""
    return [node for node in G.nodes() if G.in_degree(node) == 0]

def get_zero_outdeg_nodes_if_remove_nodes(G: nx.DiGraph, api_list: list[BaseModel]) -> list:
    """Get nodes with zero outdegree in a directed graph if the given nodes are removed."""
    nodes = [api._api_name for api in api_list]
    G_copy = G.copy()
    G_copy.remove_nodes_from(nodes)
    return get_zero_outdeg_nodes(G_copy)