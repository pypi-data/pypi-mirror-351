"""Abstract base classes for API interaction components.

Provides base classes for query builders, fetchers, and interpreters used in
API interactions and result processing.
"""

import os
from dotenv import load_dotenv
from abc import ABC, abstractmethod
import ast
import json
from typing import Any
from copy import deepcopy

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, ConfigDict, Field, create_model, PrivateAttr, field_validator, model_validator
from biochatter.llm_connect import Conversation
from ._python_interpreter import evaluate_python_code

def run_codes(code: str, state: dict[str, object]):
    """
    Run codes

    Parameters
    -----------
    code : str
        A single valid code snippet as a string.
    state: dict[str, object]
        A dictionary of variables to be used in the code snippet. E.g. {'sc': sc, 'adata': adata}
    """
    
    try:
        result = str(evaluate_python_code(code, state=state)[0])
    except Exception as e:
        return f"ERROR: {str(e)}", e
    return result, None

class BaseQueryBuilder(ABC):
    """An abstract base class for query builders."""
    def __init__(self, conversation: Conversation):
        """Initialise the query builder with a conversation object."""
        self.conversation = conversation

        load_dotenv()
        self.conversation.set_api_key(
            os.environ.get("API_KEY")
        )

    @property
    def structured_output_prompt(self) -> ChatPromptTemplate:
        """Define a structured output prompt template.

        This provides a default implementation for an API agent that can be
        overridden by subclasses to return a ChatPromptTemplate-compatible
        object.
        """
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a world class algorithm for extracting information in structured formats.",
                ),
                (
                    "human",
                    "Use the given format to extract information from the following input: {input}",
                ),
                ("human", "Tip: Make sure to answer in the correct format"),
            ],
        )

    
    @abstractmethod
    def build_api_query(
        self,
        question: str,
    ) -> list[BaseModel]:
        """Parameterise a query object.

        Parameterises a Pydantic model with the fields of the API based on the
        given question using a BioChatter conversation instance. Must be
        implemented by subclasses.

        Args:
        ----
            question (str): The question to be answered.

        Returns:
        -------
            A list containing one or more parameterised instance(s) of the query
            object (Pydantic BaseModel).

        """


class BaseFetcher(ABC):
    """Abstract base class for fetchers.

    A fetcher is responsible for submitting queries (in systems where
    submission and fetching are separate) and fetching and saving results of
    queries. It has to implement a `fetch_results()` method, which can wrap a
    multi-step procedure to submit and retrieve. Should implement retry method to
    account for connectivity issues or processing times.
    """

    @abstractmethod
    def fetch_results(
        self,
        query_models: list[BaseModel],
        data: object,
        retries: int | None = 3,
    ):
        """Fetch results by submitting a query.

        Can implement a multi-step procedure if submitting and fetching are
        distinct processes (e.g., in the case of long processing times as in the
        case of BLAST).

        Args:
        ----
            query_models: list of Pydantic models describing the parameterised
                queries

        """


class BaseInterpreter(ABC):
    """Abstract base class for result interpreters.

    The interpreter is aware of the nature and structure of the results and can
    extract and summarise information from them.
    """
    def __init__(self, conversation: Conversation):
        """Initialise the interpreter with a conversation object."""
        self.conversation = conversation

        load_dotenv()
        self.conversation.set_api_key(
            os.environ.get("API_KEY")
        )

    @abstractmethod
    def summarise_results(
        self,
        question: str,
        response: object,
    ) -> str:
        """Summarise an answer based on the given parameters.

        Args:
        ----
            question (str): The question that was asked.

            conversation_factory (Callable): A function that creates a
                BioChatter conversation.

            response (object): The response.text returned from the request.

        Returns:
        -------
            A summary of the answer.

        Todo:
        ----
            Genericise (remove file path and n_lines parameters, and use a
            generic way to get the results). The child classes should manage the
            specifics of the results.

        """


# Jiahang: deprecated, replaced by BaseAPI
class BaseAPIModel(BaseModel):
    """A base class for all API models.

    Includes default fields `uuid` and `api_name`.
    """

    uuid: str | None = Field(
        None,
        description="Unique identifier for the model instance",
    )
    model_config = ConfigDict(arbitrary_types_allowed=True)


class BaseTools:
    """Abstract base class for tools."""

    def make_pydantic_tools(self) -> list[BaseAPIModel]:
        """Uses pydantics create_model to create a list of pydantic tools from a dictionary of parameters"""
        tools = []
        for func_name, tool_params in self.tools_params.items():
            tools.append(create_model(func_name, **tool_params, __base__=BaseAPIModel))
        return tools

class BaseObject(BaseModel):
    """A class representing an object, such as an API, dependency, data, keys_info, etc."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True, 
        extra="forbid", 
        validate_assignment=True
    )
    def __hash__(self):
        members = self._hash_members()
        members = json.dumps(members, sort_keys=True, ensure_ascii=True)
        return hash(members)
    
    def _hash_members(self) -> dict:
        """A dict of members to be hased = {member_name: member_value}"""
        return self.model_dump()
    
    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

class BaseKeysInfo(BaseObject):
    """A class representing a keys info object."""
    membership: str = Field(
        default="self", 
        choices=["item", "attr", "self"],
        description="The membership method to get the data of the key"
    )
    keys: dict[str, "BaseKeysInfo"] = Field(
        default={},
        description="A dictionary of keys and their keys info"
    )

class BaseData(BaseObject):
    """A class representing a data object.

    Data example: # dict form of keys_info
    keys_info: {
        "membership": "self",
        "keys": {
            "layer1": {
                "membership": "item",
                "keys": {
                    "key1": {"membership": "item", "keys": None},
                    "key2": {"membership": "attr", "keys": None}
                }
            },
            "layer2": {
                "membership": "item", 
                "keys": {
                    "key3": {"membership": "item", "keys": None},
                    "key4": {"membership": "attr", "keys": None}
                }
            }
        }
    }
    layer1, layer2, keys1, keys2, ... are keys of data object
    membership is the membership method to get the data of the key
    
    for instance, given the keys_info as above:
    Then to access object of "key1", we use data[layer1][key1] or data.__getitem__(layer1).__getitem__(key1);
    To access object of "key2", we use data[layer1].key2 or data.__getitem__(layer1).__getattribute__("key2").
    For flexibility, we use membership to specify the membership method to get the data of the key rather than using 
    [] and . to access the data.

    Jiahang (severe and random note): directly change member of a data model instance may result in the change of
    members of other data model instances, meaning that class variables being changed.
    this is weird since it does not always happen. this note indicates that we should be careful with
    data model initialization, avoiding inplace member change and try to replace member changes with 
    new instance initialization.
    """
    data: Any = None
    keys_info: BaseKeysInfo = Field(default=BaseKeysInfo(), description="The keys of the data object")

    def _hash_members(self) -> dict:
        members = self.model_dump()
        members.pop('data') # Jiahang: data can be complex structure not hashable, so we don't consider it for now.
        return members


def _ast_to_keys_info(
            product: ast.AST, 
            child_name: str | None,
            child_keys_info: BaseKeysInfo | None) -> BaseKeysInfo:
    """
    The core logic is to convert the products keys info of InputAPI 
    to _products keys info of BaseAPI,
    where the data representations is converted from:
    product = ast.parse("data['d'].e")
    to
    keys_info = BaseKeysInfo(
        membership = "self",
        keys = {
                "d": BaseKeysInfo(
                    membership = "item",
                    keys = {
                        "e": BaseKeysInfo(
                            membership = "attr",
                        )
                    }
                )
            }
        )
    
    Jiahang: this function is pretty complicated. Documents need to be carefully revised with
    sufficient examples.
    """
    if child_name is None or child_keys_info is None:
        keys = {}
    else:
        keys = {child_name: child_keys_info}

    if isinstance(product, ast.Name):
        # Base case: just a variable name
        return BaseKeysInfo(
            membership="self",
            keys = keys
        )
    else:
        if isinstance(product, ast.Attribute):
            # Handle attribute access (e.g., .attribute)
            name = product.attr
            keys_info: BaseKeysInfo = BaseKeysInfo(
                membership="attr",
                keys = keys
            )
            
        elif isinstance(product, ast.Subscript):
            # Handle subscript access (e.g., ['key'])
            # Jiahang: this assert should be put in field validator of InputAPI
            assert isinstance(product.slice, ast.Constant), "Only constant subscript is supported for now."
            name = product.slice.value
            keys_info: BaseKeysInfo = BaseKeysInfo(
                membership="item",
                keys = keys
            )
        else:
            raise Exception(f"Invalid product access: {product}. Only [] and . access are supported.")
        
        parent_product = product.value
        full_keys_info: BaseKeysInfo = \
            _ast_to_keys_info(
                parent_product,
                name,
                keys_info
                )
        return full_keys_info

def _combine_keys_info(src: BaseKeysInfo, dst: BaseKeysInfo) -> BaseKeysInfo:
    """Combine a list of keys info into a single keys info.
    
    An example of keys_info_list:
    keys_info_list[0] = BaseKeysInfo(
        membership = "self",
        keys = {
                "d": BaseKeysInfo(
                    membership = "item",
                    keys = {
                        "e": BaseKeysInfo(
                            membership = "attr",
                        )
                    }
                )
            }
        )
    
    keys_info_list[1] = BaseKeysInfo(
        membership = "self",
        keys = {
                "d": BaseKeysInfo(
                    membership = "item",
                    keys = {
                        "c": BaseKeysInfo(
                            membership = "attr",
                        )
                    }
                )
            }
        )

    After combining two keys_info, we obtain:
    keys_info = BaseKeysInfo(
        membership = "self",
        keys = {
            "d": BaseKeysInfo(
                membership = "item",
                keys = {
                    "c": BaseKeysInfo(
                        membership = "attr",
                    ),
                    "e": BaseKeysInfo(
                        membership = "attr",
                    )
                }
            }
        )

    Jiahang: this function is pretty complicated. Documents need to be carefully revised with
    sufficient examples.
    """ 
    dst_keys = deepcopy(dst.keys)
    # Recursively merge any overlapping keys
    for key, value in src.keys.items():
        if key in dst_keys.keys() and dst_keys[key].membership == value.membership:
            dst_keys[key] = _combine_keys_info(value, dst_keys[key])
        else:
            dst_keys[key] = value
    _dst = BaseKeysInfo(
        membership=dst.membership,
        keys=dst_keys
    )
    return _dst

def _str_list_to_keys_info(str_list: list[str]) -> BaseKeysInfo:
    """Convert a string representation of a keys info to a keys info object.
    
    The string representation is a string of the form:
    [
        "data['d'].e",
        "data['d'].f"
    ]

    The keys info is a keys info object of the form:

    BaseKeysInfo(
        membership = "self",
        keys = {
            "d": BaseKeysInfo(
                membership = "item",
                keys = {
                    "e": BaseKeysInfo(
                        membership = "attr",
                    ),
                    "f": BaseKeysInfo(
                        membership = "attr",
                    )
                }
            )
        }
    )

    Jiahang: this function is pretty complicated. Documents need to be carefully revised with
    sufficient examples.
    """
    keys_info_list = []

    for p in str_list:
        p = ast.parse(p).body[0].value
        keys_info: BaseKeysInfo = \
            _ast_to_keys_info(p, None, None)
        keys_info_list.append(keys_info)

    if len(keys_info_list) == 0:
        result = BaseKeysInfo()
    elif len(keys_info_list) == 1:
        result = keys_info_list[0]
    else:
        result = keys_info_list[0]
        for keys_info in keys_info_list[1:]:
            result = _combine_keys_info(keys_info, result)
    
    return result

# Jiahang: BaseAPI and BaseDependency should have all members as required.
class BaseAPI(BaseObject):
    """Base class for all API models.
    
    We use PrivateAttr to store api_name and products to avoid them being
    included in the argument prediction of LLM through langchain.

    Jiahang: in these classes, some data members should not be set in initialization.
    Instead, they should only be set dynamically during forward pass over execution graph,
    which is conducted internally. Please implement relevant validator to ensure this.

    Jiahang: we predefine the data name to be "data" for all APIs. This is because we assume
    all input data should be stored in one data object. Even if there are multiple data objects, they
    can all be stored in the same data object through ways like dict or list. This also means that 
    the variable name "data" should not be overlapped. This is one of the standards.
    """

    # Jiahang: revise below
    # these members should be set in class definition.
    _api_name: str = PrivateAttr(default="")
    _products_original: list[str] = PrivateAttr(default=[])
    _data_name: str = PrivateAttr(default="")

    # these members can only be set during execution graph forward pass.
    # _products.data and _deps.data are created in forward pass.
    # _products.keys_info is created in post parametrize stage.
    # _deps.keys_info in created in forward pass.
    _products: BaseData = PrivateAttr(default=BaseData())
    _deps: BaseData = PrivateAttr(default=BaseData())
    

    def _hash_members(self):
        members = self.model_dump()
        members['_api_name'] = self._api_name
        members['_products'] = self._products._hash_members()
        members['_deps'] = self._deps._hash_members()
        return members
    
    def _arg_repr(self, key, val) -> str:
        if type(val) == str and key != self._data_name:
            return f"{key}='{val}'"
        return f"{key}={val}"
    
    def to_api_calling(self) -> str:
        """Convert a BaseAPI object to a string of api calling."""
        params = []
        for name in self.model_fields.keys():
            arg = self._arg_repr(name, self.__getattribute__(name))
            params.append(arg)
        return f"{self._api_name}({', '.join(params)})"

    def execute(self, state: dict[str, object]):
        """Execute the API call with the given arguments."""
        api_calling = self.to_api_calling()
        state["data"] = deepcopy(self._deps.data)
        results, error = run_codes(api_calling, state)
        if error:# Jiahang: error handling and multiple retry are not implemented yet.
            raise ValueError(error)
        else:
            self._products.data = state["data"]
            return results, api_calling
        
    def post_parametrise(self):
        """Post parametrise the API.
        
        Assuming the API is instantiated and parametrised, this method is to complete the API
        with other information, such as _products.keys_info.

        Jiahang: not employed yet.
        """
        self._products = BaseData(
            keys_info=_str_list_to_keys_info(self._products_original)
        )
        
class ROOT(BaseAPI):
    """This API does nothing but just returning the input. This API has no arguments and dependencies."""
    _api_name: str = PrivateAttr(default="root")

    def execute(self, *args, **kwargs):
        self._products.data = deepcopy(self._deps.data)
        return None, "ROOT()"

# Jiahang: we should elaborate in doc why BaseAPI use private attr but BaseDependency use field.
class BaseDependency(BaseObject):
    """A class representing an edge in the dependency graph.

    This class is used to represent the dependencies between API calls in the
    dependency graph.
    """
    u_api_name: str = Field(default="", description="The name of the source API")
    v_api_name: str = Field(default="", description="The name of the target API")
    args: dict[str, str] = Field(default={}, description="The arguments of the dependency")
    arg_types: dict[str, str] = Field(default={}, description="The argument types of the dependency")
    deps: BaseData = Field(default=BaseData(), description="The data of the dependency")
    _dep_graph_dict: dict = PrivateAttr(default={})

    def _hash_members(self):
        members = self.model_dump()
        members['deps'] = self.deps._hash_members()
        return members
    
    @classmethod
    def create(cls, u_api_name: str, v_api_name: str):
        if cls._dep_graph_dict.default:
            dep_graph_dict = cls._dep_graph_dict.default
            edge_idx = dep_graph_dict['edge_index'][f"{u_api_name}:{v_api_name}"]
            edge = dep_graph_dict['edges'][edge_idx]
            input_dep = InputDependency.model_validate(edge)
            internal_dep = cls(
                u_api_name=u_api_name, 
                v_api_name=v_api_name, 
                args=input_dep.args,
                arg_types=input_dep.arg_types,
                deps=BaseData(
                    keys_info=_str_list_to_keys_info(input_dep.dependencies)
                )
            )
            return internal_dep
        else:
            raise ValueError("Dependency graph dict is not set.")


class InputAPI(BaseObject):
    """A class representing an input API.
    
    InputAPI is input from dependency graph JSON structure,
    and will be converted to BaseAPI for internal use.

    This class is created to ease users' efforts to manually create dependency graph.
    But this class is not internally friendly, so will be converted to BaseAPI.
    """
    api: str = Field(..., description="The name of the API")
    products: list[str] = Field(..., description="The products of the API")
    id: str = Field(..., description="The id of the API")

    @field_validator("products", mode="after")
    @classmethod
    def _check_product(cls, products: list[str]) -> list[str]:
        for product in products:
            product = ast.parse(product)
            assert len(product.body) == 1, "Each product should be a single data object."

            # Jiahang: this assert needs to be carefully considered
            assert isinstance(product.body[0], ast.Expr) and \
                not isinstance(product.body[0].value, ast.Constant), \
                "Each product should be an variable. " \
                "Functions, classes, assignment, constants, etc. are not supported."
        return products
    
    @model_validator(mode="after")
    def _check_id(self) -> "InputAPI":
        assert self.id == self.api, "The id of the API should be the same as the api name."
        return self

class InputDependency(BaseObject):
    """A class representing an input dependency.
    
    InputDependency is input from dependency graph JSON structure,
    and will be converted to BaseDependency for internal use.

    This class is created to ease users' efforts to manually create dependency graph.
    But this class is not internally friendly, so will be converted to BaseDependency.
    """
    dependencies: list[str] = Field(..., description="The dependencies of the dependency")
    source: str = Field(..., description="The source of the dependency")
    target: str = Field(..., description="The target of the dependency")
    args: dict = Field(..., description="The arguments of the dependency")
    arg_types: dict = Field(..., description="The argument types of the dependency")

    @model_validator(mode="after")
    def _check_args(self) -> "InputDependency":
        assert len(self.args) == 1 and len(self.arg_types) == 1, "Only one activation arg is permitted for the dependency."
        return self
    
    