import networkx as nx
from networkx import DiGraph
from pydantic import BaseModel, PrivateAttr, Field
import json
from typing import Any
from queue import Queue

from biochatter.api_agent.base.agent_abc import BaseAPI, BaseDependency
from biochatter.api_agent.dep_graph.utils import read_apis_from_graph_dict, read_deps_from_graph_dict    

class DependencyGraph(DiGraph):
    """A class representing a dependency graph for API calls.

    This class extends the DiGraph class from NetworkX to represent a directed
    graph where nodes are API calls and edges represent dependencies between them.

    Not all DiGraph methods have corresponding methods in this class. Only methods used
    by other codes are implemented. The rest are inherited from DiGraph.

    Arguments:
    ----------
    api_names : list[str] | None = None
        The names of the APIs to be added to the graph. These api_names serve as index 
        to nodes in dependency graph dict. Please finding this dict in info_hub.py.
    dependencies : list[(str, str)] | None = None
        The dependencies in tuple format to be added to the graph. These dependencies serve as
        index to edges in dependency graph dict. Please finding this dict in info_hub.py.
    api_class_dict : dict | None = None
        The dictionary of API classes.
    dep_class : BaseDependency | None = None
        The class of the dependencies.
    """

    def __init__(self, 
                 api_names: list[str] | None = None, 
                 dependencies: list[(str, str)] | None = None, 
                 api_class_dict: dict | None = None,
                 dep_class: BaseDependency | None = None):
        super().__init__()

        self.apis_dict = {}
        self.deps_dict = {}
    
        if api_names or dependencies:
            assert api_names and dependencies, "Nodes and edges must be provided at the same time."
            assert api_class_dict is not None, "API class dictionary must be provided."
            assert dep_class is not None, "Dependency class must be provided."

            apis_dict = read_apis_from_graph_dict(api_names, api_class_dict)
            deps_dict = read_deps_from_graph_dict(dependencies, dep_class)

            self.add_apis_from(list(apis_dict.values()))
            self.add_deps_from(list(deps_dict.values()))
    
    def add_api(self, api: BaseAPI):
        super().add_node(api._api_name.default)
        self.apis_dict[api._api_name.default] = api

    def add_apis_from(self, api_list: list[BaseModel]):
        for api in api_list:
            self.add_api(api)

    def remove_api(self, api: str):
        super().remove_node(api)
        del self.apis_dict[api]

    def remove_apis_from(self, api_list: list[str]):
        for api in api_list:
            self.remove_api(api)

    def add_dep(self, dep: BaseDependency):
        u_api_name, v_api_name = dep.u_api_name, dep.v_api_name
        super().add_edge(u_api_name, v_api_name)
        self.deps_dict[(u_api_name, v_api_name)] = dep

    def add_deps_from(self, dep_list: list[BaseDependency]):
        for dep in dep_list:
            self.add_dep(dep)
        
    def remove_dep(self, u_api_name: str, v_api_name: str):
        super().remove_edge(u_api_name, v_api_name)
        del self.deps_dict[(u_api_name, v_api_name)]
    
    def remove_deps_from(self, u_v_api_names: list[(str, str)]):
        for u_api_name, v_api_name in u_v_api_names:
            self.remove_dep(u_api_name, v_api_name)

    def in_apis(self, api_name: str) -> list[BaseModel]:
        """Get the dependent APIs of the given API."""
        in_nodes = super().predecessors(api_name)
        return self.get_apis(list(in_nodes))
    
    def out_apis(self, api_name: str) -> list[BaseModel]:
        """Get the APIs that depend on the given API."""
        out_nodes = super().successors(api_name)
        return self.get_apis(list(out_nodes))
    
    def in_deps(self, api_name: str) -> list[BaseDependency]:
        """Get the dependencies of the given API."""
        in_edges = super().in_edges(api_name)
        return self.get_deps(list(in_edges))
    
    def out_deps(self, api_name: str) -> list[BaseDependency]:
        """Get the dependencies that depend on the given API."""
        out_edges = super().out_edges(api_name)
        return self.get_deps(list(out_edges))
    
    def update_api(self, api: BaseAPI):
        if api._api_name.default in self.apis_dict:
            self.apis_dict[api._api_name.default] = api
        else:
            raise ValueError(f"API {api._api_name.default} not found in the dependency graph.")
        
    def update_dep(self, dep: BaseDependency):
        if (dep.u_api_name, dep.v_api_name) in self.deps_dict:
            self.deps_dict[(dep.u_api_name, dep.v_api_name)] = dep
        else:
            raise ValueError(f"Dependency {dep.u_api_name} -> {dep.v_api_name} not found in the dependency graph.")
        
    def clear(self):
        super().clear()
        self.apis_dict.clear()
        self.deps_dict.clear()

    def clear_deps(self):
        super().clear_edges()
        self.deps_dict.clear()

    def get_api(self, api_name: str) -> BaseAPI:
        """Get the API object associated with the given API name."""
        api: BaseAPI | None = self.apis_dict.get(api_name)
        if api is not None:
            return api
        else:
            raise ValueError(f"API {api_name} not found in the dependency graph.")
    
    def get_apis(self, api_names: list[str]) -> list[BaseAPI]:
        """Get the API objects associated with the given API names."""
        return [self.get_api(api_name) for api_name in api_names]
    
    def get_dep(self, u_api_name: str, v_api_name: str) -> BaseDependency:
        """Get the dependency object associated with the given API names."""
        dep: BaseDependency | None = self.deps_dict.get((u_api_name, v_api_name))
        if dep is not None:
            return dep.model_copy(deep=True)
        else:
            raise ValueError(f"Dependency {u_api_name} -> {v_api_name} not found in the dependency graph.")
    
    def get_deps(self, u_v_api_names: list[(str, str)]) -> list[BaseDependency]:
        """Get the dependency objects associated with the given API names."""
        return [self.get_dep(u_api_name, v_api_name) for u_api_name, v_api_name in u_v_api_names]
    
    def retrieve_sub_g(self, sub_g: DiGraph) -> "DependencyGraph":
        """Reteieve the sub DependencyGraph given the sub latent DiGraph
        The latent DiGraph only needs the node set and egde set, where node names are indexed by API names.
        There is no need for any node or edge attributes for latent DiGraph.
        Specifically, this method retrieves sub API and BaseDependency sets.
        In principle, all DiGraph subgraph retrieval operations need to run this method afterwards.
        """
        sub_apis = self.get_apis(sub_g.nodes())
        sub_deps = self.get_deps(sub_g.edges())
        graph = DependencyGraph()
        graph.add_apis_from(sub_apis)
        graph.add_deps_from(sub_deps)
        return graph
    
    def get_zero_indeg_apis(self) -> list[BaseModel]:
        """Get apis with zero indegree in the dependency graph."""
        nodes = [node for node in self.nodes() if self.in_degree(node) == 0]
        return self.get_apis(nodes)
    
    def get_zero_outdeg_apis(self) -> list[BaseModel]:
        """Get apis with zero outdegree in the dependency graph."""
        nodes = [node for node in self.nodes() if self.out_degree(node) == 0]
        return self.get_apis(nodes)
    
class ExecutionGraph(DependencyGraph):
    """A class representing an execution graph for API calls.
    
    Jiahang: It's needs explanation in its and DependencyGraph's docstring why execution graph is a subclass of dependency graph,
    and why the only difference is api._api_name.default -> api._api_name and api.model_copy.

    Jiahang: also note that api type in DependencyGraph is incorrect since api is a ScanpyAPI class not an instance.
    """

    def __init__(self):
        super().__init__()

    def add_api(self, api: BaseAPI):
        super().add_node(api._api_name)
        self.apis_dict[api._api_name] = api

    def update_api(self, api: BaseAPI):
        if api._api_name in self.apis_dict:
            self.apis_dict[api._api_name] = api
        else:
            raise ValueError(f"API {api._api_name} not found in the dependency graph.")
        
    def get_api(self, api_name: str) -> BaseAPI:
        """Get the API object associated with the given API name."""
        api: BaseAPI | None = self.apis_dict.get(api_name)
        if api is not None:
            return api.model_copy(deep=True)
        else:
            raise ValueError(f"API {api_name} not found in the dependency graph.")