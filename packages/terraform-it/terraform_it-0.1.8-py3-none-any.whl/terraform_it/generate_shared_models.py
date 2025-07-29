import os
from typing import Dict, Any, Tuple, List
from jinja2 import Environment, FileSystemLoader
from terraform_it.helpers import map_to_go_type, create_var_names, check_if_primitive

env = Environment(loader=FileSystemLoader('templates'))

# print(shared_models)

def generate_shared_models(models: Dict[str, Any], client: str, templates: Dict[str, Any]):
    """
    Generate Go files for shared models with structs and getter methods.
    
    Args:
        models: List of dictionaries where each dict has a single key (model name)
                mapping to a dict of fields with their types or $ref.
    """

    enums_template = templates['enums']
    main_template = templates['main']
    getters_template = templates['getters']
    shared_enum_model_template = templates['enum_model']

    # Convert list of dicts to a simpler mapping for easier processing
    model_map = models
    # print(model_map)

    # Function to check if a schema contains any $ref
    def contains_key(data, key):
        if isinstance(data, dict):
            if key in data:
                return True
            # Recursively check in each value
            return any(contains_key(v, key) for v in data.values())
        elif isinstance(data, list):
            # If the data is a list, check each element
            return any(contains_key(item, key) for item in data)
        return False

    # Sort models: those without $ref first, then those with $ref
    sorted_models = sorted(model_map.items(), key=lambda x: contains_key(x[1], '$ref'))
    # print(sorted_models)

    for name, schema in sorted_models:
        # print(name, schema)
        # Generate struct fields
        fields = []
        getters = []
        extra_types = []
        if 'properties' not in schema:
            if 'type' in schema:
                go_type = name
                if 'enum' in schema:
                    go_type = name
                    enum_consts = [f"{go_type}{create_var_names(val)} {go_type} = \"{val}\"" for val in schema['enum']]
                    enum_context = {
                        "go_type": go_type,
                        "enum_consts": enum_consts,
                        "enum_values": schema['enum']
                    }
                    content = shared_enum_model_template.render(**enum_context)
                    file_path = f"{client.lower()}/sdk/models/{name.lower()}.go"
                    with open(file_path, 'w') as f:
                        f.write(content)
            continue
        for field_name, field_info in schema['properties'].items():
            go_type, enums = map_to_go_type(field_name, field_info, model_map)
            go_type = create_var_names(go_type)
            if check_if_primitive(go_type):
                if 'required' in schema and field_name not in schema['required']:
                    go_type = f"*types.{go_type}"  # Pointer for required fields
                else:
                    go_type = f"types.{go_type}"
                fields.append(f"    {field_name.capitalize()} {go_type} `json:\"{field_name}\"`")
            else:
                if 'required' in schema and field_name not in schema['required']:
                    go_type = f"*models.{go_type}"  # Pointer for required fields
                else:
                    go_type = f"models.{go_type}"
                fields.append(f"    {field_name.capitalize()} {go_type} `json:\"{field_name}\"`")
            
            # Generate getter method
            getters_context = {
                "name": name,
                "field_name": field_name,
                "go_type": go_type
            }
            getters.append(getters_template.render(**getters_context))

            if enums:
                if go_type.startswith('[]'):
                    go_type = go_type[2:]
                elif go_type.startswith('*'):
                    go_type = go_type[1:]
                if go_type == 'type':
                    go_type = name + 'Type'
                if go_type.startswith('models.'):
                    go_type = go_type[7:]
                enum_consts = [f"{go_type}{create_var_names(val)} {go_type} = \"{val}\"" for val in enums]
                enum_context = {
                    "go_type": go_type,
                    "enum_consts": enum_consts,
                    "enum_values": enums
                }
                extra_types.append(enums_template.render(**enum_context))

        # Construct the Go file content
        main_context = {
            "name": name,
            "fields": fields,
            "getters": getters,
            "extra_types": extra_types
        }
        content = main_template.render(**main_context)
        # Write to file
        file_path = f"{client.lower()}/sdk/models/{name.lower()}.go"
        with open(file_path, 'w') as f:
            f.write(content)

# Example usage
if __name__ == "__main__":
    
    # Ensure directory exists
    os.makedirs(f"{client.lower()}/sdk/models", exist_ok=True)
    
    # Generate the shared models
    # generate_shared_models(models)
    print("Shared models generated successfully!")