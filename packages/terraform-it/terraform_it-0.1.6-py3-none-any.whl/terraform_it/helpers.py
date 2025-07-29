from typing import Dict, Any, List, Tuple
import re

GET_OPERATION = "read"
CREATE_OPERATION = "create"
UPDATE_OPERATION = "update"
DELETE_OPERATION = "delete"

def get_resources(spec: dict, config: dict) -> dict:
    """
    Generate a dictionary of resources and their CRUD operations.

    Args:
        spec (dict): The OpenAPI specification.
        config (dict): The configuration tagging resources to be generated.

    Raises:
        ValueError: If an unknown CRUD operation is encountered in the config.

    Returns:
        A dictionary containing the specifications of the resources to be generated.
    """
    resources_to_generate = {}

    # Iterate over each resource in the config
    for resource in config.get("resources", []):
        # Iterate over each CRUD operation for the resource
        for crud_operation, value in config["resources"][resource].items():
            if crud_operation == 'resource-path':
                continue
            method = value[
                "method"
            ].lower()  # Extract the HTTP method (GET, POST, etc.)
            path = value["path"]  # Extract the endpoint path
            operation = None
            # print(crud_operation, value)

            # Match the CRUD operation to the corresponding constant
            match crud_operation:
                case "read":
                    operation = GET_OPERATION
                case "create":
                    operation = CREATE_OPERATION
                case "update":
                    operation = UPDATE_OPERATION
                case "delete":
                    operation = DELETE_OPERATION
                case "list":
                    operation = "list"
                case _:
                    raise ValueError(f"Unknown operation {crud_operation}")
            # print(path, method)

            # Add the operation details to the resources_to_generate dictionary
            resources_to_generate.setdefault(resource, {})[operation] = {
                "schema": spec["paths"][path][method],
                "path": path,
            }
            if 'parameters' in spec["paths"][path]:
                resources_to_generate[resource][operation]['schema']['parameters'] = spec["paths"][path]['parameters']

    return resources_to_generate


def get_data_sources(spec: dict, config: dict) -> dict:
    """
    Creates a dictionary of data sources and their singular/plural endpoints.

    Args:
        spec (dict): The OpenAPI specification.
        config (dict): The configuration tagging resources to be generated.

    Returns:
        A dictionary containing the specifications of the data sources to be generated.
    """
    data_source_to_generate = {}

    for data_source in config.get("datasources", []):
        singular_path = config["datasources"][data_source]["read"]
        data_source_to_generate.setdefault(data_source, {})["read"] = {
            "schema": spec["paths"][singular_path]["get"],
            "path": singular_path,
        }
        plural_path = config["datasources"][data_source]["list"]
        data_source_to_generate.setdefault(data_source, {})["list"] = {
            "schema": spec["paths"][plural_path]["get"],
            "path": plural_path,
        }
        if 'parameters' in spec["paths"][plural_path]:
            data_source_to_generate[data_source]["list"]['schema']['parameters'] = spec["paths"][plural_path]['parameters']
    
    return data_source_to_generate

def indent(num):
    return '\t' * num

def add_field(resources, resource_name, var_name, field_data):
    # If the resource (e.g., "Function") is not yet in the dictionary, add it.
    if resource_name not in resources:
        resources[resource_name] = {}
    # If the variable (e.g., "status") is not yet defined, add it.
    if var_name not in resources[resource_name]:
        resources[resource_name][var_name] = field_data
    else:
        # Key exists, so we ignore subsequent occurrences.
        pass

def add_var_type(var_type):
    if var_type == 'boolean':
        return 'bool'
    elif var_type == 'integer':
        return 'int64'
    else:
        return var_type

def get_all_ref_values(data):
    refs = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == '$ref':
                refs.append(value)
            else:
                refs.extend(get_all_ref_values(value))
    elif isinstance(data, list):
        for item in data:
            refs.extend(get_all_ref_values(item))
    return refs

def get_validators(data: Dict[str, Any]):
    validators = {}
    if 'minimum' in data:
        validators['minimum'] = data['minimum']
    if 'maximum' in data:
        validators['maximum'] = data['maximum']
    if 'pattern' in data:
        validators['pattern'] = data['pattern']
    if 'enum' in data:
        validators['enum'] = ["\""+val+"\"" for val in data['enum']]
    if 'minLength' in data:
        validators['min_length'] = data['minLength']
    if 'maxLength' in data:
        validators['max_length'] = data['maxLength']
    return validators

def validator_helpers(var_name, var_type, var_data, required):
    # print(var_data)
    if 'pattern' in var_data['validators']:
        return f"\"{var_name}\": schema.{var_type.capitalize()}Attribute{{\n{indent(4)}{required}: true,\n{indent(4)}validators: []validator.{var_type.capitalize()}{{\n{indent(5)}stringvalidator.RegexMatches(regexp.MustCompile(\"{var_data['validators']['pattern']}\")),\n{indent(4)}}},\n{indent(3)}}}"
    elif 'enum' in var_data['validators']:
        return f"\"{var_name}\": schema.{var_type.capitalize()}Attribute{{\n{indent(4)}{required}: true,\n{indent(4)}validators: []validator.{var_type.capitalize()}{{\n{indent(5)}stringvalidator.OneOf({", ".join(var_data['validators']['enum'])}),\n{indent(4)}}},\n{indent(3)}}}"
    elif 'min_length' in var_data['validators'] and 'max_length' in var_data['validators']:
        return f"\"{var_name}\": schema.{var_type.capitalize()}Attribute{{\n{indent(4)}{required}: true,\n{indent(4)}validators: []validator.{var_type.capitalize()}{{\n{indent(5)}stringvalidator.UTF8LengthBetween({var_data['validators']['min_length']}, {var_data['validators']['max_length']}),\n{indent(4)}}},\n{indent(3)}}}"
    elif 'min_length' in var_data['validators']:
        return f"\"{var_name}\": schema.{var_type.capitalize()}Attribute{{\n{indent(4)}{required}: true,\n{indent(4)}validators: []validator.{var_type.capitalize()}{{\n{indent(5)}stringvalidator.UTF8LengthAtLeast({var_data['validators']['min_length']}),\n{indent(4)}}},\n{indent(3)}}}"
    elif 'max_length' in var_data['validators']:
        return f"\"{var_name}\": schema.{var_type.capitalize()}Attribute{{\n{indent(4)}{required}: true,\n{indent(4)}validators: []validator.{var_type.capitalize()}{{\n{indent(5)}stringvalidator.UTF8LengthAtMost({var_data['validators']['max_length']}),\n{indent(4)}}},\n{indent(3)}}}"
    elif 'minimum' in var_data['validators']:
        return f"\"{var_name}\": schema.{var_type.capitalize()}Attribute{{\n{indent(4)}{required}: true,\n{indent(4)}tvalidators: []validator.{var_type.capitalize()}{{\n{indent(5)}numbervalidator.AtLeast({var_data['validators']['minimum']}),\n{indent(4)}}},\n{indent(3)}}}"
    elif 'maximum' in var_data['validators']:
        return f"\"{var_name}\": schema.{var_type.capitalize()}Attribute{{\n{indent(4)}{required}: true,\n{indent(4)}tvalidators: []validator.{var_type.capitalize()}{{\n{indent(5)}numbervalidator.AtMost({var_data['validators']['maximum']}),\n{indent(4)}}},\n{indent(3)}}}"

def map_to_go_type(field_name: str, field_info: Dict[str, Any], model_map: Dict[str, Any]) -> Tuple[str, List[str]]:
    """
    Map OpenAPI field type to Go type, handling $ref and arrays.
    
    Args:
        field_info: Dictionary containing type or $ref for a field.
        model_map: Mapping of model names to their schemas for $ref resolution.
    
    Returns:
        Corresponding Go type as a string.
    """
    if '$ref' in field_info:
        ref_name = field_info['$ref'].split('/')[-1]
        return f"{ref_name}", []  # Pointer to referenced struct
    elif field_info.get('type') == 'array':
        items = field_info.get('items', {})
        if '$ref' in items:
            ref_name = items['$ref'].split('/')[-1]
            return f"[]{ref_name}", []  # Slice of pointers to referenced structs
        else:
            item_type, enums = map_to_go_type(field_name, items, model_map)
            return f"[]{item_type}", enums  # Slice of basic type
    elif field_info.get('type') == 'string':
        if 'enum' in field_info:
            return f"{field_name}", field_info['enum']  # Enum type
        return 'string', []
    elif field_info.get('type') == 'integer':
        return 'int64', []  # Default to int64 for integers
    elif field_info.get('type') == 'boolean':
        return 'bool', []
    elif field_info.get('type') == 'object':
        return f'{field_name}', []  # Generic object type
    else:
        return 'interface{}', []  # Fallback for unknown types

def create_var_names(go_type: str) -> str:
    """
    Create variable names from Go types by capitalizing each part and joining them.
    
    Args:
        go_type: Go type as a string.
    
    Returns:
        Variable name as a string.
    """
    if go_type not in ['string', 'int64', 'bool', 'interface{}', 'number'] and '_' in go_type:
        # print(go_type)
        parts = go_type.split('_')
        return ''.join(part.capitalize() for part in parts)
    return go_type

def check_if_primitive(go_type: str) -> bool:
    return go_type in ['string', 'int64', 'bool', 'interface{}', 'number']

def to_camel_case(s):
    parts = re.split(r'[^a-zA-Z0-9]', s)
    return ''.join(p.capitalize() for p in parts if p)

def normalize_parameter(parameter, components):
    name = parameter['$ref'].split('/')[-1]
    parameter = components['parameters'][name]
    return parameter

def get_information(spec: dict, config: dict) -> dict:
    methods = {}
    resource_path = {}
    for resource, value in config['resources'].items():
        # print(value['resource-path'])
        resource_path[resource] = value['resource-path']
        methods[resource] = {}
        for method, schema in value.items():
            if method == 'read':
                methods[resource]['read'] = schema['name']
            elif method == 'create':
                methods[resource]['create'] = schema['name']
            elif method == 'update':
                methods[resource]['update'] = schema['name']
            elif method == 'delete':
                methods[resource]['delete'] = schema['name']
    for data_source, value in config['datasources'].items():
        methods[data_source]['list'] = value['list-name']
    return {
        "sdk_client_path": config.get('sdk-client-path', ''),
        "methods": methods,
        "resource_path": resource_path
    }
