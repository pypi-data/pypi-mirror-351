import os
import inspect
import json
import re
from types import MappingProxyType, ModuleType
from typing import Any, Callable
from copy import deepcopy
import argparse
import importlib
from tqdm import tqdm
import subprocess
from dotenv import load_dotenv
load_dotenv()

from docstring_parser import parse
import libcst as cst
from pydantic import Field, create_model, PrivateAttr
from pydantic.fields import FieldInfo
from importlib.metadata import version

from langchain_core.utils.pydantic import create_model as create_model_v1
from langchain_core.pydantic_v1 import Field as FieldV1
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain.chat_models import init_chat_model
from langchain.output_parsers.fix import OutputFixingParser
from langchain.output_parsers import RetryOutputParser

from datamodel_code_generator import DataModelType, PythonVersion
from datamodel_code_generator.model import get_data_model_types
from datamodel_code_generator.parser.jsonschema import JsonSchemaParser

from .base.agent_abc import BaseAPIModel, BaseAPI

# Jiahang: deprecated in the future, replaced by apis_to_data_models
def generate_pydantic_classes(module: ModuleType) -> list[type[BaseAPIModel]]:
    """Generate Pydantic classes for each callable.

    For each callable (apition/method) in a given module. Extracts parameters
    from docstrings using docstring-parser. Each generated class has fields
    corresponding to the parameters of the apition. If a parameter name
    conflicts with BaseModel attributes, it is aliased.

    Params:
    -------
    module : ModuleType
        The Python module from which to extract apitions and generate models.

    Returns
    -------
    list[Type[BaseModel]]
        A list of Pydantic model classes corresponding to each apition found in
            `module`.

    Notes
    -----
    - For now, all parameter types are set to `Any` to avoid complications with
      complex or external classes that are not easily JSON-serializable.
    - Optional parameters (those with a None default) are represented as
      `Optional[Any]`.
    - Required parameters (no default) use `...` to indicate that the field is
      required.

    """
    base_attributes = set(dir(BaseAPIModel))
    classes_list = []

    for name, api in inspect.getmembers(module, inspect.isapition):
        # Skip private/internal apitions (e.g., _something)
        if name.startswith("_"):
            continue

        # Parse docstring for parameter descriptions
        doc = inspect.getdoc(api) or ""
        parsed_doc = parse(doc)
        doc_params = {p.arg_name: p.description or "No description available." for p in parsed_doc.params}

        sig = inspect.signature(api)
        fields = {}

        for param_name, param in sig.parameters.items():
            # Skip *args and **kwargs for now
            if param_name in ("args", "kwargs"):
                continue

            # Fetch docstring description or fallback
            description = doc_params.get(param_name, "No description available.")

            # Determine default value
            # If no default, we use `...` indicating a required field
            if param.default is not inspect.Parameter.empty:
                default_value = param.default

                # Convert MappingProxyType to a dict for JSON compatibility
                if isinstance(default_value, MappingProxyType):
                    default_value = dict(default_value)

                # Handle non-JSON-compliant float values by converting to string
                if default_value in [float("inf"), float("-inf"), float("nan"), float("-nan")]:
                    default_value = str(default_value)
            else:
                default_value = ...  # No default means required

            # For now, all parameter types are Any
            annotation = Any

            # Append the original annotation as a note in the description if
            # available
            if param.annotation is not inspect.Parameter.empty:
                description += f"\nOriginal type annotation: {param.annotation}"

            # If default_value is None, parameter can be Optional
            # If not required, mark as Optional[Any]
            if default_value is None:
                annotation = Any | None

            # Prepare field kwargs
            field_kwargs = {"description": description, "default": default_value}

            # If field name conflicts with BaseModel attributes, alias it
            field_name = param_name
            if param_name in base_attributes:
                alias_name = param_name + "_param"
                field_kwargs["alias"] = param_name
                field_name = alias_name

            fields[field_name] = (annotation, FieldV1(**field_kwargs))

        # Create the Pydantic model

        tl_parameters_model = create_model_v1(
            name,
            **fields,
            __base__=BaseAPIModel,
        )
        classes_list.append(tl_parameters_model)
    return classes_list

def get_api_path(module: ModuleType, api: Callable) -> str:
    """Get the path of an API.

    This apition takes a module and an API, and returns the path of the API.
    """
    return module.__name__ + '.' + api.__name__

def get_class_name(module: ModuleType, api: Callable) -> str:
    """Get the internal name of an API.

    This apition takes a module and an API, and returns the internal name of the
    API.
    """

    module_name = module.__name__
    api_name = api.__name__

    module_name = ''.join(_name.capitalize() for _name in re.findall(r'[a-zA-Z]+', module_name))
    api_name = ''.join(_name.capitalize() for _name in re.findall(r'[a-zA-Z]+', api_name))
    return module_name + api_name

def get_py_version() -> PythonVersion:
    """Get the Python version.
    """
    from sys import version_info
    py_version = version_info.major, version_info.minor, version_info.micro
    assert py_version[0] == 3, "Python version must be 3.x.x"
    if py_version[1] < 9:
        raise ValueError("Python version must be less than 3.14 and larger than or equal to 3.9.")
    if py_version[1] >= 9 and py_version[1] < 10:
        return PythonVersion.PY_39
    if py_version[1] >= 10 and py_version[1] < 11:
        return PythonVersion.PY_310
    if py_version[1] >= 11 and py_version[1] < 12:
        return PythonVersion.PY_311
    if py_version[1] >= 12 and py_version[1] < 13:
        return PythonVersion.PY_312
    if py_version[1] >= 13 and py_version[1] < 14:
        return PythonVersion.PY_313
    if py_version[1] >= 14:
        raise ValueError("Python version must be less than 3.14 and larger than or equal to 3.9.")

def get_info_import_path(package: ModuleType, object_name: str) -> str:
    package_name = package.__name__
    import_path = f"biochatter.api_agent.python.{package_name}.info_hub.{object_name}"
    return import_path
    
def data_model_to_py(data_model: type[BaseAPIModel], additional_imports: list[str], need_import: bool) -> str:
    """Convert a Pydantic model to a Python code.
    """
    json_schema = json.dumps(data_model.model_json_schema())
    data_model_types = get_data_model_types(
        DataModelType.PydanticV2BaseModel,
        target_python_version=get_py_version()
    )
    parser = JsonSchemaParser(
        json_schema,
        data_model_type=data_model_types.data_model,
        data_model_root_type=data_model_types.root_model,
        data_model_field_type=data_model_types.field_model,
        data_type_manager_type=data_model_types.data_type_manager,
        dump_resolve_reference_action=data_model_types.dump_resolve_reference_action,
        base_class="BaseAPI",
        additional_imports=additional_imports
    )
    codes: str = parser.parse()

    # Parse the code into a CST
    module = cst.parse_module(codes)

    class DataModelTransformer(cst.CSTTransformer):
        def __init__(self, data_model: type[BaseAPIModel], need_import: bool):
            self.data_model = data_model
            self.need_import = need_import
            self.doc = inspect.getdoc(data_model)
            self.doc = '\n    '.join(self.doc.strip().splitlines())
            self.doc = self.doc.replace('\\', '\\\\')

        def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign) -> cst.Assign:
            # Remove model_config
            if isinstance(original_node.targets[0].target, cst.Name) and \
                original_node.targets[0].target.value == "model_config":
                return cst.RemovalSentinel.REMOVE
            return updated_node

        def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
            # Add docstring to the class
            docstring = cst.SimpleString(f'"""\n    {self.doc}\n    """')

            # Add private attributes
            private_attrs = []
            keys = ["_api_name", "_products_original", "_data_name"]
            for key in keys:
                call = self.data_model.__private_attributes__[key].__repr__()
                call = cst.parse_expression(call)
                call = call.with_changes(func=cst.Name("PrivateAttr"))

                private_attrs.append(
                    cst.SimpleStatementLine([
                        cst.Assign(
                            targets=[cst.AssignTarget(cst.Name(key))],
                            value=call,
                        )
                    ])
                )

            return updated_node.with_changes(
                body=updated_node.body.with_changes(
                    body=[cst.SimpleStatementLine([cst.Expr(docstring)])] + \
                    list(updated_node.body.body) + private_attrs
                )
            )

        def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import | cst.RemovalSentinel:
            # Remove BaseAPI import
            for name in original_node.names:
                if isinstance(name.name, cst.Name) and name.name.value == "BaseAPI":
                    return cst.RemovalSentinel.REMOVE
            return updated_node

        def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom | cst.RemovalSentinel:
            # Remove imports if not needed
            if not self.need_import:
                return cst.RemovalSentinel.REMOVE
            return updated_node

    # Apply the transformer
    transformer = DataModelTransformer(data_model, need_import)
    modified_module = module.visit(transformer)
    
    return modified_module.code

def simplify_desc(
    fields: dict[str, tuple[type, FieldInfo] | str], 
    llm: BaseChatModel,
) -> dict[str, tuple[Any, Field]]:
    """Summarize the descriptions of multiple fields.
    """
    _fields = {field_name: str for field_name in fields.keys()}
    output_format = create_model(
        "OutputFormat", **_fields,
    )
    desc = {}
    for key, value in fields.items():
        if isinstance(list(fields.values())[0], tuple):
            desc[key] = value[1].description
        else:
            desc[key] = value

    parser = PydanticOutputParser(pydantic_object=output_format)
    prompt = ChatPromptTemplate([
        ("system", "Summarize descriptions of each term into one or two sentences. The response format follows these instructions:\n{format}"),
        ("user", "{desc}"),
    ])

    prompt = prompt.invoke({"desc": desc, "format": parser.get_format_instructions()})
    response = llm.invoke(prompt)

    except_tag = True
    if except_tag:
        try:
            result: dict = parser.invoke(response).model_dump()
            except_tag = False
        except OutputParserException as e:
            except_tag = True
    if except_tag:
        try:
            correct_parser = OutputFixingParser.from_llm(parser=parser, llm=llm)
            result: dict = correct_parser.invoke(response).model_dump()
            except_tag = False
        except OutputParserException as e:
            except_tag = True
    if except_tag:
        try:
            correct_parser = RetryOutputParser.from_llm(parser=parser, llm=llm, max_retries=3)
            result: dict = correct_parser.parse_with_prompt(response.content, prompt)
        except OutputParserException as e:
            raise e
        
    for key, value in result.items():
        if isinstance(list(fields.values())[0], tuple):
            annotation, field_info = fields[key]
            field_info.description = value
            fields[key] = (annotation, field_info)
        else:
            fields[key] = value

    return fields

def add_tools_dict(codes: str, data_models: list[type[BaseAPIModel]]) -> str:
    """Add TOOLS_DICT to the end of the code using libcst.
    
    Args:
        codes: The source code as a string
        data_models: List of data model classes to include in TOOLS_DICT
        
    Returns:
        Modified source code with TOOLS_DICT added
    """
    # Parse the source code into a CST
    module = cst.parse_module(codes)
    
    # Create a transformer to add the TOOLS dictionary
    class AddToolsTransformer(cst.CSTTransformer):
        def __init__(self, data_models: list[type[BaseAPIModel]]):
            self.data_models = data_models
            
        def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
            # Create dictionary elements with proper indentation
            elements = []
            for data_model in self.data_models:
                key = cst.SimpleString(f'"{data_model._api_name.default}"')
                value = cst.Name(data_model.__name__)
                elements.append(cst.DictElement(
                    key=key, 
                    value=value,
                ))
            
            # Create the TOOLS_DICT assignment with two newlines before it
            tools_dict = cst.SimpleStatementLine([
                cst.Assign(
                    targets=[cst.AssignTarget(cst.Name("TOOLS_DICT"))],
                    value=cst.Dict(elements=elements)
                )
            ])
            
            # Add two newlines and the assignment to the end of the module
            return updated_node.with_changes(
                body=list(updated_node.body) + [
                    tools_dict
                ]
            )
    
    # Apply the transformer
    modified_module = module.visit(AddToolsTransformer(data_models))
    
    # Convert the modified CST back to source code
    return modified_module.code

def remove_tools_dict(codes: str) -> str:
    # Parse the source code into a CST
    module = cst.parse_module(codes)
    
    # Create a transformer to remove the TOOLS dictionary assignment
    class RemoveToolsTransformer(cst.CSTTransformer):
        def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign) -> cst.Assign | cst.RemovalSentinel:
            # Check if this is a TOOLS assignment
            for target in original_node.targets:
                if isinstance(target.target, cst.Name) and target.target.value == 'TOOLS_DICT':
                    return cst.RemovalSentinel.REMOVE
            return updated_node
    
    # Apply the transformer
    modified_module = module.visit(RemoveToolsTransformer())
    
    # Convert the modified CST back to source code
    return modified_module.code

def apis_to_data_models(
        api_dict: str, 
        need_import: bool = True,
        ) -> list[type[BaseAPIModel]]:
    """
    Although we have many string operations like hack in this implementation, all these hacks are bound to
    specific version of datamodel_code_generator and pydantic. They are not bound to any specific package, module
    or API, meaning that they are still generic to any API.
    """
    assert version("datamodel_code_generator") == "0.30.1", \
        "datamodel-code-generator version must be 0.30.1 since some fine-grained operations " \
        "are based on the outputs of this package. Different versions may lead to different outputs " \
        "and thus invalidate those fine-grained operations."
    
    base_attributes = set(dir(BaseAPIModel))
    classes_list = []
    codes_list = []
    api_list = api_dict['api_list']
    module = api_dict['meta']['module']

    llm = init_chat_model(os.environ.get("MODEL"), model_provider="openai", temperature=0.7)

    for _api in tqdm(api_list):
        if "_deprecated" in _api and _api['_deprecated']:
            continue
        api = _api['api']
        assert 'products' in _api and 'data_name' in _api, \
            "configs should contain 'products' and 'data_name'."
        name = api.__name__
        if name.startswith("_"):
            raise Warning(f"apition {name} is private/internal and should not be included in the data model.")

        # Parse docstring for parameter descriptions
        doc = inspect.getdoc(api) or ""
        parsed_doc = parse(doc)
        doc_params = {p.arg_name: p.description or "No description available." for p in parsed_doc.params}

        sig = inspect.signature(api)
        fields = {}

        for param_name, param in sig.parameters.items():
            # Skip *args and **kwargs for now
            if param_name in ("args", "kwargs"):
                continue

            # Fetch docstring description or fallback
            description = doc_params.get(param_name, "No description available.")

            # Determine default value
            # If no default, we use `...` indicating a required field
            if param.default is not inspect.Parameter.empty:
                default_value = param.default

                # Convert MappingProxyType to a dict for JSON compatibility
                if isinstance(default_value, MappingProxyType):
                    default_value = dict(default_value)

                # Handle non-JSON-compliant float values by converting to string
                if default_value in [float("inf"), float("-inf"), float("nan"), float("-nan")]:
                    default_value = str(default_value)
            else:
                default_value = ...  # No default means required

            # For now, all parameter types are Any
            annotation = Any

            # Append the original annotation as a note in the description if
            # available
            if param.annotation is not inspect.Parameter.empty:
                # Jiahang(TODO): this is not needed, since all predicted types should be
                # basic types.
                description += f"\nOriginal type annotation: {param.annotation}"

            # If default_value is None, parameter can be Optional
            # If not required, mark as Optional[Any]
            if default_value is None:
                annotation = Any | None

            # Prepare field kwargs
            field_kwargs = {"description": description, "default": default_value}

            # If field name conflicts with BaseModel attributes, alias it
            field_name = param_name
            if param_name in base_attributes:
                alias_name = param_name + "_param"
                field_kwargs["alias"] = param_name
                field_name = alias_name

            fields[field_name] = (annotation, Field(**field_kwargs))

        try:
            fields = simplify_desc(fields, llm)
            doc = simplify_desc({"doc": parsed_doc.description}, llm)['doc']
        except OutputParserException as e:
            doc = parsed_doc.description
            print(f"The descriptions of API or arguments of {name} are not summarized correctly. Please summarize them manually.")

        # Create the Pydantic model
        fields['_api_name'] = (str, PrivateAttr(default=get_api_path(module, api)))
        fields['_products_original'] = (str, PrivateAttr(default=_api['products']))
        fields['_data_name'] = (str, PrivateAttr(default=_api['data_name']))

        data_model = create_model(
            get_class_name(module, api),
            __doc__ = doc, 
            __base__ = BaseAPI,
            **fields,
        )
        classes_list.append(data_model)

        additional_imports = [
            "biochatter.api_agent.base.agent_abc.BaseAPI",
            "pydantic.PrivateAttr",
        ]
        codes = data_model_to_py(data_model, additional_imports, need_import)
        codes_list.append(codes)

        # hack. Subsequent codes need no repeated imports. This is important
        # to avoid erros like __future__ import not at the top of the file.
        need_import = False

    # hack. Add TOOLS_DICT to the end of the file.
    codes = "\n\n".join(codes_list)
    return classes_list, codes

def get_output_path(package_name: str, api_dict_name: str, as_module: bool = False) -> str:
    if as_module:
        return f"biochatter.api_agent.python.{package_name}.{api_dict_name}"
    else:
        return f"biochatter/api_agent/python/{package_name}/{api_dict_name}.py"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--package_name", type=str, required=True)
    parser.add_argument("--api_dict_name", type=str, required=True)
    parser.add_argument("--rerun_whole_file", action="store_true")
    args = parser.parse_args()

    package_name = args.package_name
    api_dict_name = args.api_dict_name
    output_path = get_output_path(package_name, api_dict_name)

    api_dict = importlib.import_module(f"biochatter.api_agent.python.{package_name}.api_dict")
    api_dict = getattr(api_dict, api_dict_name)

    if os.path.exists(output_path) and not args.rerun_whole_file:
        output_module_path = get_output_path(package_name, api_dict_name, as_module=True)
        output_module = importlib.import_module(output_module_path)
        TOOLS_DICT = deepcopy(output_module.TOOLS_DICT)

        # extract api in api_dict that is not in TOOLS_DICT
        additional_apis = []
        for api in api_dict['api_list']:
            if get_api_path(api_dict['meta']['module'], api['api']) not in TOOLS_DICT.keys():
                additional_apis.append(api)

        with open(output_path, "r") as f:
            codes = f.read()
        codes = remove_tools_dict(codes)

        _api_dict = {
            "meta": api_dict['meta'],
            "api_list": additional_apis,
        }

        data_models, new_codes = apis_to_data_models(_api_dict, need_import=False)
        tools_list = list(TOOLS_DICT.values()) + data_models
        new_codes = add_tools_dict(new_codes, tools_list)

        codes = codes + "\n\n" + new_codes
        
    else:
        data_models, codes = apis_to_data_models(api_dict)
        codes = add_tools_dict(codes, data_models)

    
    with open(output_path, "w") as f:
        f.write(codes)

    # Jiahang: use subprocess is a bad practice. but there is no public api
    # released by black. the so-called internal API is unstable, and this
    # subprocess usage is recommended.

    # code formatting by black.

    subprocess.run(["black", output_path])

    print(f"Data models and codes have been generated and saved to {output_path}.")