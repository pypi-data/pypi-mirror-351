from copy import deepcopy
import ast
from typing import Any

from biochatter.api_agent.base.agent_abc import BaseDependency, BaseAPI, BaseData, BaseKeysInfo, InputAPI, InputDependency   

def _retrieve_data(src_data: Any, src_keys_info: BaseKeysInfo, dst_keys_info: BaseKeysInfo):
    """retrieval: if a src key is not in dst keys, then its corresponding data is deleted"""
    for key, sub_src_keys_info in src_keys_info.keys.items():
        if key not in dst_keys_info.keys:
            if sub_src_keys_info.membership == "item":
                del src_data[key]
            elif sub_src_keys_info.membership == "attr":
                delattr(src_data, key)
            elif sub_src_keys_info.membership == "self":
                # only the first layer can be self
                # which has been passed
                raise Exception("Only the first layer can be self membership")
        else:
            # Recursively handle nested structures
            if sub_src_keys_info.membership == "item":
                sub_src_data = src_data.__getitem__(key)
                sub_dst_keys_info = dst_keys_info.keys[key]
            elif sub_src_keys_info.membership == "attr":
                sub_src_data = src_data.__getattribute__(key)
                sub_dst_keys_info = dst_keys_info.keys[key]
            elif sub_src_keys_info.membership == "self":
                raise Exception("Only the first layer can be self membership")
            else:
                raise Exception(f"Invalid membership: {sub_src_keys_info.membership}")
            
            if sub_src_keys_info.keys: # there are objects being included, not just itself.
                sub_src_data = _retrieve_data(sub_src_data, 
                                                sub_src_keys_info, sub_dst_keys_info)
            
            if sub_dst_keys_info.membership == "item":
                src_data.__setitem__(key, sub_src_data)
            elif sub_dst_keys_info.membership == "attr":
                src_data.__setattr__(key, sub_src_data)
            elif sub_dst_keys_info.membership == "self":
                raise Exception("Only the first layer can be self membership")
            else:
                raise Exception(f"Invalid membership: {sub_dst_keys_info.membership}")
    
    return src_data

def _combine_data(src: BaseData, dst: BaseData) -> BaseData:
    """We combined src.data into dst.data according to src.keys_info and dst.keys_info.
    
    For each key in src.keys_info, if this key not exists in dst.keys_info, we put this key into dst.keys_info
    and put the data of this key into dst.data, and return.
    Otherwise, both src and dst go into the next layer of the same key, and do the same thing as described above,
    until the final layer of src or dst is reached.

    Note that how to put data depends on keys_info.membership. If it is "item", we use __setitem__ to put data.
    If it is "attr", we use __setattr__ to put data. If it is "self", we just raised an error. So as __getitem__ and __getattribute__.

    Note that we say a src key is in dst.keys_info if dst.keys_info.keys[key] is not None and src.keys_info.keys[key]
    has the same membership as dst.keys_info.keys[key].
    """
    src_data = src.data
    dst_data = dst.data
    src_keys_info = src.keys_info
    dst_keys_info = dst.keys_info
    
    for key, sub_src_keys_info in src_keys_info.keys.items():
        if key not in dst_keys_info.keys or dst_keys_info.keys[key].membership != sub_src_keys_info.membership:
            if sub_src_keys_info.membership == "item":
                dst_data.__setitem__(key, src_data.__getitem__(key))
                dst_keys_info.keys[key] = sub_src_keys_info
            elif sub_src_keys_info.membership == "attr":
                dst_data.__setattr__(key, src_data.__getattribute__(key))
                dst_keys_info.keys[key] = sub_src_keys_info
            elif sub_src_keys_info.membership == "self":
                raise Exception("Only the first layer can be self membership")
            else:
                raise Exception(f"Invalid membership: {sub_src_keys_info.membership}")
        
        else:
            if sub_src_keys_info.membership == "item":
                sub_src_data = src_data.__getitem__(key)
                sub_dst_data = dst_data.__getitem__(key)
            elif sub_src_keys_info.membership == "attr":
                sub_src_data = src_data.__getattribute__(key)
                sub_dst_data = dst_data.__getattribute__(key)
            elif sub_src_keys_info.membership == "self":
                raise Exception("Only the first layer can be self membership")
            else:
                raise Exception(f"Invalid membership: {sub_src_keys_info.membership}")
                
            sub_dst_keys_info = dst_keys_info.keys[key]
            sub_dst = _combine_data(
                BaseData(data=sub_src_data, keys_info=sub_src_keys_info), 
                BaseData(data=sub_dst_data, keys_info=sub_dst_keys_info)
            )
            if sub_dst_keys_info.membership == "item":
                dst_data.__setitem__(key, sub_dst.data)
            elif sub_dst_keys_info.membership == "attr":
                dst_data.__setattr__(key, sub_dst.data)
            dst_keys_info.keys[key] = sub_dst.keys_info
    
    return BaseData(data=dst_data, keys_info=dst_keys_info)
    
def retrieve_products(src_api: BaseAPI, dep: BaseDependency) -> BaseDependency:
    """Retrieve products from the src_api._products according to deps.keys_info,
    and assign the retrieved products to self.deps
    
    Note that the deps.keys_info must be a subset of src_api._products.keys_info.
    (Jiahang: this should be asserted in the future)

    For now the retrieval is conducted by removing unneeded objects from src_api._products.data.
    However, I (Jiahang) personally think it's a bit tricky and unsafe.
    We should find a better way to do this.
    """
    
    
    src_data = deepcopy(src_api._products.data)
    src_keys_info = src_api._products.keys_info
    dst_keys_info = dep.deps.keys_info
    
    # Start recursive copy
    dst_data = _retrieve_data(src_data, 
                              src_keys_info, dst_keys_info)
    
    dst_data = BaseData(
        data=dst_data,
        keys_info=dst_keys_info
    )

    dep.deps = dst_data

    return dep

def aggregate_deps(deps: list[BaseDependency], dst_api: BaseAPI) -> BaseAPI:
    """Aggregate dependencies from the data of deps, and assign the aggregated dependencies to dst_api._deps.

    Each dependency in deps has a dependency.deps, which is a BaseData object, of which data is the actual
    data object, keys_info describe the data structure and how to access the data. 
    Now given a list of dependencies, 1) we need to aggregate the data of each dependency into a single data object,
    and 2) we need to combine the keys_info of each dependency into a single keys_info object.
    """
    dst_data = deps[0].deps.model_copy(deep=True)
    for dep in deps:
        src_data = dep.deps.model_copy(deep=True)
        dst_data = _combine_data(src_data, dst_data)
    dst_api._deps = dst_data
    return dst_api

def is_active_dep(dep: BaseDependency, api: BaseAPI) -> bool:
    """Check if the dependency is active by the target api."""
    dep_args = dep.args
    e_arg_name = list(dep_args.keys())[0] # Jiahang: only one edge required arg being considered for now
    e_arg_val = dep_args[e_arg_name]
    if e_arg_name in api.model_fields.keys() and getattr(api, e_arg_name) == e_arg_val:
        return True
    return False

def read_apis_from_graph_dict(api_names: list[str], tools_dict: dict) -> dict[str, BaseAPI]:
    """Jiahang: this function is pretty complicated. Documents need to be carefully revised with
    sufficient examples."""

    apis = {}
    for api_name in api_names:
        internal_api: BaseAPI = tools_dict[api_name]
        apis[api_name] = internal_api

    return apis

def read_deps_from_graph_dict(dependencies: list[(str, str)], dep_class: BaseDependency) -> dict[str, BaseDependency]:

    """Jiahang: this function is pretty complicated. Documents need to be carefully revised with
    sufficient examples."""

    deps = {}
    for u_api_name, v_api_name in dependencies:
        internal_dep: BaseDependency = dep_class.create(
            u_api_name = u_api_name,
            v_api_name = v_api_name,
        )
        deps[(u_api_name, v_api_name)] = internal_dep

    return deps

