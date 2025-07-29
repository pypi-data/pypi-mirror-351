from biochatter.api_agent.base.agent_abc import BaseAPI, BaseDependency
# Jiahang: info_hub should be a global stuff, not a module inside each package.
from .info_hub import dep_graph_dict
from pydantic import PrivateAttr
from copy import deepcopy

class ScanpyDependency(BaseDependency):
    _dep_graph_dict: dict = PrivateAttr(default=dep_graph_dict)