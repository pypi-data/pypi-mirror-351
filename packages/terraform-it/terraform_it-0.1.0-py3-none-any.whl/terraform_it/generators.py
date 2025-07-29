import os
import re
import yaml
from typing import Dict, Any
from collections import defaultdict
import openapi
from jinja2 import Environment, FileSystemLoader, Template
from helpers import to_camel_case, get_resources, get_data_sources, get_all_ref_values

env = Environment(loader=FileSystemLoader('templates'))


# Load the OpenAPI YAML file
def load_openapi_file(file_path: str) -> Dict[str, Any]:
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def resources_to_generate(resources: Dict[str, Any]) -> list:
    resources_to_generate = defaultdict(lambda: defaultdict(dict))
    for resource, value in resources.items():
        for method, schema in value.items():
            resources_to_generate[resource.capitalize()][method] = schema['schema']
    return resources_to_generate

def data_sources_to_generate(data_sources: Dict[str, Any]) -> list:
    data_sources_to_generate = defaultdict(lambda: defaultdict(dict))
    for resource, value in data_sources.items():
        for method, schema in value.items():
            data_sources_to_generate[resource.capitalize()][method] = schema['schema']
    return data_sources_to_generate

def schemas_to_generate(resources: Dict[str, Any], shared_models: Dict[str, Any]) -> list:
    schemas = []
    generate_schemas = defaultdict(lambda: defaultdict(dict))
    for resource, value in resources.items():
        for method, schema in value.items():
            if 'responses' in schema['schema']:
                schemas.extend(get_all_ref_values(schema['schema']['responses']))
            if 'requestBody' in schema['schema']:
                schemas.extend(get_all_ref_values(schema['schema']['requestBody']))
            if 'parameters' not in schema['schema']:
                continue
            for parameter in schema['schema']['parameters']:
                # print(parameter)
                if 'schema' in parameter and 'type' not in parameter['schema']:
                    schemas.append(parameter['schema']['$ref'])
  
    schemas = list(set(schemas))

    for schema in schemas:
        if schema[0] == '#':
            schema = schema.split('/')[-1]
        if schema in shared_models:
            if schema == "WalletRecurringTransactionRule":
                print(schema, shared_models[schema])
            schemas.extend(get_all_ref_values(shared_models[schema]))
        
    schemas = [ref.split('/')[-1] for ref in schemas]
    schemas = list(set(schemas))

    # print(schemas)
    for schema in schemas:
        if schema in shared_models:
            generate_schemas[schema] = shared_models[schema]
    return generate_schemas

def operations_to_generate(resources: Dict[str, Any]) -> list:
    operations = defaultdict(list)
    for resource, value in resources.items():
        for method, schema in value.items():
            operation = to_camel_case(schema['schema']['operationId'])
            operations[operation].append({'parameters': schema['schema']['parameters']})
            if 'requestBody' in schema['schema']:
                operations[operation].append({'requestBody': schema['schema']['requestBody']})
            operations[operation].append({'responses': schema['schema']['responses']})
    return operations

def tags_to_generate(resources: Dict[str, Any]) -> list:
    tags = defaultdict(list)
    for resource, value in resources.items():
        for method, schema in value.items():
            tags[schema['schema']['tags'][0]].append([schema['path'], method.split('O')[0], to_camel_case(schema['schema']['operationId']), schema['schema']['operationId'], schema['schema']['responses']])
    return tags

def models_to_generate(get_resources: Dict[str, Any], get_data_sources: Dict[str, Any], shared_models: Dict[str, Any]) -> list:
    models = schemas_to_generate(get_resources, shared_models)
    models.update(schemas_to_generate(get_data_sources, shared_models))
    return models
