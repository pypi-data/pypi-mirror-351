from jinja2 import Environment, FileSystemLoader
import os
from terraform_it.helpers import *
from typing import Dict, Any
from collections import defaultdict
from terraform_it.generators import *
from terraform_it.helpers import normalize_parameter

resource_vars = {}
refs = {}
env = Environment(loader=FileSystemLoader('templates'))

def generate_inner_schema(properties: Dict[str, Any] | str, shared_models: Dict[str, Any]):
    if type(properties) == str:
        return f"schema.{properties.capitalize()}Attribute{{\n{indent(4)}Required: true,\n{indent(3)}}}"
    else:
        inner_schema = []
        for name, prop in properties.items():
            # print(name, prop)
            if 'type' in prop:
                if type(prop['type']) == list:
                    prop['type'] = prop['type'][0]
                if prop['type'] == 'boolean':
                    var_type = 'bool'
                elif prop['type'] == 'integer':
                    var_type = 'int64'
                else:
                    var_type = prop['type']
            else:
                var_type = prop['$ref'].split('/')[-1]
            if name in 'required':
                required = "Required"
            else:
                required = "Optional"
            
            if var_type not in ['int64', 'string', 'number', 'bool', 'array', 'object']:
                if not 'properties' in shared_models[var_type]:
                    continue
                inner_schema.append(f"{name}: schema.SingleNestedAttribute{{\n{indent(6)}{required}: true,\n{indent(5)}{generate_inner_schema(shared_models[var_type]['properties'], shared_models)}\n{indent(5)}}}")
            elif var_type == 'array':
                inner_schema.append(f"{name}: schema.ListAttribute{{\n{indent(6)}{required}: true,\n{indent(5)}ElementType: types.{var_type.capitalize()}Type,\n{indent(5)}}}")
            elif 'enum' in prop:
                validators = get_validators(prop)
                var_data = {
                    "type": var_type,
                    "required": required,
                    "validators": validators
                }
                inner_schema.append(validator_helpers(name, var_type, var_data, required))
            else:
                inner_schema.append(f"{name}: schema.{var_type.capitalize()}Attribute{{\n{indent(6)}{required}: true,\n{indent(5)}}}")
        return f"Attributes: map[string]schema.Attribute{{\n{indent(5)}{f',\n{indent(5)}'.join(inner_schema)}\n{indent(4)}}}"


def generate_data_source(data_sources: Dict[str, Any], client: str, shared_models: Dict[str, Any], templates: Dict[str, Any], components: Dict[str, Any], information: Dict[str, Any]):
    # print(data_sources)
    datasource_template = templates['datasource']
    data_source_all_template = templates['data_source_all']
    list_method_template = templates['list']
    requestBody_template = templates['request']
    responsemethod_template = templates['response']
    schema_template = templates['schema.j2']
    schema_helpers_template = templates['schema_helper']
    testing_template = templates['testing']
    for resource, value in data_sources.items():
        # print(resource, "\n", value)
        struct_vars = []
        check = set()
        schema_method = []
        read_vars = []
        list_vars = []
        read_operation = ""
        list_operation = ""
        read_responseBody = ""
        list_responseBody = ""
        read_properties = []
        list_properties = []
        read_parameters = []
        list_parameters = []
        read_method_name = information['methods'][resource]['read']
        list_method_name = information['methods'][resource]['list']
        sdk_client_path = information['sdk_client_path']
        resource_path = information['resource_path'][resource]

        for method, schema in value.items():
            response_refs = get_all_ref_values(schema['responses'])
            request_refs = get_all_ref_values(schema['requestBody']) if 'requestBody' in schema else []
            refs['responses'] = response_refs[0].split('/')[-1] if len(response_refs) > 0 else schema['responses']
            refs['requestBody'] = request_refs[0].split('/')[-1] if len(request_refs) > 0 else []
            if resource not in resource_vars:
                resource_vars[resource] = {}
            data_sources[resource][method]['responses'] = refs['responses']
            if 'requestBody' in schema:
                data_sources[resource][method]['requestBody'] = refs['requestBody']
            if 'parameters' in schema:
                for parameter in schema['parameters']:
                    if '$ref' in parameter:
                        parameter = normalize_parameter(parameter, components)
                    var_name = parameter['name']
                    if 'type' not in parameter['schema']:
                        var_type = parameter['schema']['$ref'].split('/')[-1]
                    elif parameter['schema']['type'] == 'boolean':
                        var_type = 'bool'
                    elif parameter['schema']['type'] == 'integer':
                        var_type = 'int64'
                    else:
                        var_type = parameter['schema']['type']
                    field_data = {
                        "type": var_type,
                        "required": parameter['required'],
                        "validators": get_validators(parameter['schema'])
                    }
                    add_field(resource_vars, resource, parameter['name'], field_data)
                    if parameter['required']:
                        required = "Required"
                    else:
                        required = "Optional"
                    if var_type not in ['int64', 'string', 'number', 'bool', 'array']:
                        if var_name not in check:
                            check.add(var_name)
                            struct_vars.append(f"{to_camel_case(var_name)}  models.{var_type.lower()}  `tfsdk:\"{var_name}\"`")
                            schema_method.append(f"\"{var_name}\": schema.SingleNestedAttribute{{\n{indent(4)}{required}: true,\n{indent(4)}{generate_inner_schema(shared_models[var_type].get('properties', 'type'), shared_models)}\n{indent(3)}}}")
                    else:
                        if field_data['validators'] != {}:
                            if var_name not in check:
                                schema_method.append(validator_helpers(var_name, var_type, field_data, required))
                        else:
                            if var_name not in check:
                                schema_method.append(f"\"{var_name}\": schema.{var_type.capitalize()}Attribute{{\n{indent(4)}{required}: true,\n{indent(3)}}}")
                        if var_name not in check:
                            struct_vars.append(f"{to_camel_case(var_name)}  types.{var_type.capitalize()}  `tfsdk:\"{var_name}\"`")
                            check.add(var_name)
            if refs['responses'] != []:
                for var in shared_models[refs['responses']]['properties']:
                    if 'type' in shared_models[refs['responses']]['properties'][var]:
                        if shared_models[refs['responses']]['properties'][var]['type'] == 'boolean':
                            var_type = 'bool'
                        elif shared_models[refs['responses']]['properties'][var]['type'] == 'integer':
                            var_type = 'int64'
                        else:
                            var_type = shared_models[refs['responses']]['properties'][var]['type']
                    else:
                        var_type = shared_models[refs['responses']]['properties'][var]['$ref'].split('/')[-1]
                    if 'required' not in shared_models[refs['responses']] or var not in shared_models[refs['responses']]['required']:
                        required = "Optional"
                    else: 
                        required = "Required"
                    field_data = {
                        "type": var_type,
                        "required": required,
                        "validators": get_validators(shared_models[refs['responses']]['properties'][var])
                    }
                    add_field(resource_vars, resource, var, field_data)
                    if var_type not in ['int64', 'string', 'number', 'bool', 'array']:
                        if var not in check:
                            check.add(var)
                            struct_vars.append(f"{to_camel_case(var)}  models.{var_type.lower()}  `tfsdk:\"{var}\"`")
                            schema_method.append(f"\"{var}\": schema.SingleNestedAttribute{{\n{indent(4)}{required}: true,\n{indent(4)}{generate_inner_schema(shared_models[var_type].get('properties', 'type'), shared_models)}\n{indent(3)}}}")
                    else:
                        if field_data['validators'] != {}:
                            if var not in check:
                                schema_method.append(validator_helpers(var, var_type, field_data, required))
                        else:
                            if var not in check:
                                schema_method.append(f"\"{var}\": schema.{var_type.capitalize()}Attribute{{\n{indent(4)}{required}: true,\n{indent(3)}}}")
                        if var not in check:
                            check.add(var)
                            struct_vars.append(f"{to_camel_case(var)}  types.{var_type.capitalize()}  `tfsdk:\"{var}\"`")
            if 'requestBody' in schema:
                for var in shared_models[refs['requestBody']]['properties']:
                    if shared_models[refs['requestBody']]['properties'][var] == {}:
                        var_type = 'interface{}'
                    elif 'type' in shared_models[refs['requestBody']]['properties'][var]:
                        if shared_models[refs['requestBody']]['properties'][var]['type'] == 'boolean':
                            var_type = 'bool' 
                        elif shared_models[refs['requestBody']]['properties'][var]['type'] == 'integer':
                            var_type = 'int64'
                        else:
                            var_type = shared_models[refs['requestBody']]['properties'][var]['type']
                    else:
                        var_type = shared_models[refs['requestBody']]['properties'][var]['$ref'].split('/')[-1]
                    if 'required' not in shared_models[refs['requestBody']] or var not in shared_models[refs['requestBody']]['required']:
                        required = "Optional"
                    else: 
                        required = "Required"
                    field_data = {
                        "type": var_type,
                        "required": required,
                        "validators": get_validators(shared_models[refs['requestBody']]['properties'][var])
                    }
                    add_field(resource_vars, resource, var, field_data)
                    if var_type not in ['int64', 'string', 'number', 'bool', 'array']:
                        if var not in check:
                            check.add(var)
                            if var_type == 'interface{}':
                                struct_vars.append(f"{to_camel_case(var)}  {var_type}  `tfsdk:\"{var}\"`")
                                schema_method.append(f"\"{var}\": schema.SingleNestedAttribute{{\n{indent(4)}{required}: true,\n{indent(4)}interface{{}}\n{indent(3)}}}")
                            else:
                                struct_vars.append(f"{to_camel_case(var)}  models.{var_type.lower()}  `tfsdk:\"{var}\"`")
                                schema_method.append(f"\"{var}\": schema.SingleNestedAttribute{{\n{indent(4)}{required}: true,\n{indent(4)}{generate_inner_schema(shared_models[var_type].get('properties', 'type'), shared_models)}\n{indent(3)}}}")
                    else:
                        if field_data['validators'] != {}:
                            if var not in check:
                                schema_method.append(validator_helpers(var, var_type, field_data, required))
                        else:
                            if var not in check:
                                schema_method.append(f"\"{var}\": schema.{var_type.capitalize()}Attribute{{\n{indent(4)}{required}: true,\n{indent(3)}}}")
                        if var not in check:
                            check.add(var)
                            struct_vars.append(f"{to_camel_case(var)}  types.{var_type.capitalize()}  `tfsdk:\"{var}\"`")
            requestMethod_vars= []
            if method == 'read':
                read_operation = to_camel_case(schema['operationId'])
                if 'parameters' in schema:
                    for parameter in schema['parameters']:
                        if '$ref' in parameter:
                            parameter = normalize_parameter(parameter, components)
                        if 'type' not in parameter['schema']:
                            continue
                        var_type = parameter['schema']['type']
                        if parameter['required'] or 'required' in parameter['schema']:
                            read_vars.append(f"{parameter['name']} := data.{parameter['name'].capitalize()}.Value{var_type.capitalize()}()")
                        else:
                            read_vars.append(f"{parameter['name']} := new({var_type})\n{indent(1)}if !data.{parameter['name'].capitalize()}.IsUnknown() && !data.{parameter['name'].capitalize()}.IsNull() {{\n{indent(2)}*{parameter['name']} = data.{parameter['name'].capitalize()}.Value{var_type.capitalize()}()\n{indent(1)}}} else {{\n{indent(2)}{parameter['name']} = nil\n{indent(1)}}}")
                        read_parameters.append(parameter['name'])
                read_responseBody = refs['responses']
                read_properties = [[key, add_var_type(shared_models[refs['responses']]['properties'][key]['type']) if 'type' in shared_models[refs['responses']]['properties'][key] else shared_models[refs['responses']]['properties'][key]['$ref'].split('/')[-1]] for key in shared_models[refs['responses']]['properties'].keys()]
            
            elif method == 'list':
                list_operation = to_camel_case(schema['operationId'])
                if 'parameters' in schema:
                    for parameter in schema['parameters']:
                        if '$ref' in parameter:
                            parameter = normalize_parameter(parameter, components)
                        if 'type' not in parameter['schema']:
                            continue
                        var_type = parameter['schema']['type']
                        if parameter['required'] or 'required' in parameter['schema']:
                            list_vars.append(f"{parameter['name']} := data.{parameter['name'].capitalize()}.Value{var_type.capitalize()}()")
                        else:
                            list_vars.append(f"{parameter['name']} := new({var_type})\n{indent(1)}if !data.{parameter['name'].capitalize()}.IsUnknown() && !data.{parameter['name'].capitalize()}.IsNull() {{\n{indent(2)}*{parameter['name']} = data.{parameter['name'].capitalize()}.Value{var_type.capitalize()}()\n{indent(1)}}} else {{\n{indent(2)}{parameter['name']} = nil\n{indent(1)}}}")
                        list_parameters.append(parameter['name'])
                list_responseBody = refs['responses']
                list_properties = [[key, add_var_type(shared_models[refs['responses']]['properties'][key]['type']) if 'type' in shared_models[refs['responses']]['properties'][key] else shared_models[refs['responses']]['properties'][key]['$ref'].split('/')[-1]] for key in shared_models[refs['responses']]['properties'].keys()]


                
        context = {
            "resource_name": resource,
            "struct_vars": struct_vars,
            "schema_method": schema_method,
            "read_parameters": read_parameters,
            "list_parameters": list_parameters,
            "read_responseBody": read_responseBody,
            "list_responseBody": list_responseBody,
            "read_properties": read_properties,
            "list_properties": list_properties,
            "read_operation": read_operation,
            "list_operation": list_operation,
            "status_code": list(schema['responses'].keys())[0] if isinstance(schema['responses'], dict) else "",
            "read_vars": read_vars,
            "list_vars": list_vars,
            "client_name": client,
            "read_method_name": read_method_name,
            "list_method_name": list_method_name,
            "sdk_client_path": sdk_client_path,
            "resource_path": resource_path
        } 
        os.makedirs(f"{client.lower()}/provider", exist_ok=True)

        datasource_output = datasource_template.render(**context)
        file_path = f"{client.lower()}/provider/{'data_source_'+resource.lower()}.go"
        with open(file_path, 'w') as f:
            f.write(datasource_output)
        
        testing_output = testing_template.render(**context)
        file_path = f"{client.lower()}/provider/{'data_source_'+resource.lower()+'_acctest.go'}"
        with open(file_path, 'w') as f:
            f.write(testing_output)
        
        datasource_all_output = data_source_all_template.render(**context)
        file_path = f"{client.lower()}/provider/{'data_source_all_'+resource.lower()}.go"
        with open(file_path, 'w') as f:
            f.write(datasource_all_output)
        
        testing_all_output = testing_template.render(**context)
        file_path = f"{client.lower()}/provider/{'data_source_all_'+resource.lower()+'_acctest.go'}"
        with open(file_path, 'w') as f:
            f.write(testing_all_output)


# generate_data_source(data_sources, shared_models)

