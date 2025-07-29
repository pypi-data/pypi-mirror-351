#!/usr/bin/env python3
import argparse
import os
import sys
import yaml
import subprocess
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, List

def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a YAML file."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading YAML file {file_path}: {e}")
        sys.exit(1)

def setup_directories(client_name: str):
    """Create necessary directories for the provider."""
    directories = [
        f"{client_name.lower()}/provider",
        f"{client_name.lower()}/sdk/models/",
        "examples/resources",
        "examples/data-sources",
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def generate_provider(openapi_spec: Dict[str, Any], config: Dict[str, Any]):
    """Generate all provider files from templates."""
    # Extract client name from OpenAPI spec
    client_name = openapi_spec['info']['title'].split(' ')[0]
    servers = openapi_spec.get('servers', [])
    
    # Import modules directly - they should be available since they're part of the package
    try:
        from terraform_it.generate_provider import generate_provider as gen_provider
        from terraform_it.generate_resource import generate_resource as gen_resource
        from terraform_it.generate_shared_models import generate_shared_models as gen_shared_models
        from terraform_it.generate_data_source import generate_data_source as gen_data_source
        import terraform_it.generators as generators
        from terraform_it.helpers import get_information, get_resources, get_data_sources
    except ImportError as e:
        # Print the detailed error message
        print(f"Error importing required modules: {e}")
        sys.exit(1)
    
    # Setup Jinja environment - fix the template path
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # Get resources from OpenAPI spec and config
    information = get_information(openapi_spec, config)
    resources = get_resources(openapi_spec, config)
    data_sources = get_data_sources(openapi_spec, config)
    
    shared_models = openapi_spec['components']['schemas']
    components = openapi_spec['components']
    models = generators.models_to_generate(resources, data_sources, shared_models)
    tags = generators.tags_to_generate(resources)
    resources = generators.resources_to_generate(resources)
    gen_data_sources = generators.data_sources_to_generate(data_sources)
    
    # Generate provider files
    print(f"Generating provider for {client_name}...")
    
    # Generate provider.go
    provider_template = env.get_template('provider.j2')
    gen_provider(client_name, servers, resources, provider_template)
    
    # Generate resources
    print("Generating resources...")
    template = env.get_template('resource_model.j2')
    requestBody_template = env.get_template('requestBody.j2')
    responsemethod_template = env.get_template('responsemethod.j2')
    create_method_template = env.get_template('create_method.j2')
    read_method_template = env.get_template('read_method.j2')
    update_method_template = env.get_template('update_method.j2')
    delete_method_template = env.get_template('delete_method.j2')
    schema_template = env.get_template('schema.j2')
    schema_helpers_template = env.get_template('utils/schema_helper.j2')
    testing_template = env.get_template('testing_resource.j2')
    templates = {
        'resource': template,
        'request': requestBody_template,
        'response': responsemethod_template,
        'create': create_method_template,
        'read': read_method_template,
        'update': update_method_template,
        'delete': delete_method_template,
        'schema.j2': schema_template,
        'schema_helper': schema_helpers_template,
        'testing': testing_template
    }
    gen_resource(resources, client_name, shared_models, templates, components, information)
    
    # Generate data sources
    print("Generating data sources...")
    datasource_template = env.get_template('data_source_model.j2')
    data_source_all_template = env.get_template('data_source_model_p.j2')
    list_method_template = env.get_template('list_method.j2')
    data_source_testing_template = env.get_template('testing_data_source.j2')
    templates = {
        'datasource': datasource_template,
        'data_source_all': data_source_all_template,
        'list': list_method_template,
        'request': requestBody_template,
        'response': responsemethod_template,
        'schema.j2': schema_template,
        'schema_helper': schema_helpers_template,
        'testing': data_source_testing_template
    }
    gen_data_source(gen_data_sources, client_name, shared_models, templates, components, information)
    
    # Generate shared models
    print("Generating shared models...")
    enums_template = env.get_template('shared_schema/shared_enums.j2')
    main_template = env.get_template('shared_schema/shared_main.j2')
    getters_template = env.get_template('shared_schema/shared_getters.j2')
    shared_enum_model_template = env.get_template('shared_schema/shared_enum_model.j2')
    templates = {
        'enums': enums_template,
        'main': main_template,
        'getters': getters_template,
        'enum_model': shared_enum_model_template
    }
    gen_shared_models(models, client_name, templates)
    
    # Generate main.go
    main_template = env.get_template('main.go.j2')
    main_context = {
        "client_name": client_name,
    }
    main_output = main_template.render(**main_context)
    main_file_path = f"main.go"
    with open(main_file_path, 'w') as f:
        f.write(main_output)
    print(f"Generated {main_file_path}")
    
    # Generate tools.go
    tools_template = env.get_template('tools.j2')
    tools_output = tools_template.render()
    os.makedirs("tools", exist_ok=True)
    tools_file_path = f"tools/tools.go"
    with open(tools_file_path, 'w') as f:
        f.write(tools_output)
    print(f"Generated {tools_file_path}")

    # Generate CHECK.md
    check_template = env.get_template('CHECK.md.j2')
    check_output = check_template.render(client_name=client_name)
    check_file_path = f"CHECK.md"
    with open(check_file_path, 'w') as f:
        f.write(check_output)
    print(f"Generated {check_file_path}")

    # Generate go.mod
    go_mod_template = env.get_template('go.mod.j2')
    go_mod_output = go_mod_template.render()
    go_mod_file_path = f"go.mod"
    with open(go_mod_file_path, 'w') as f:
        f.write(go_mod_output)
    print(f"Generated {go_mod_file_path}")
    
    print("Provider generation completed successfully!")

def main():
    parser = argparse.ArgumentParser(description='Generate Terraform provider from OpenAPI spec')
    parser.add_argument('openapi_spec', help='Path to the OpenAPI specification YAML file')
    parser.add_argument('config', help='Path to the configuration YAML file')
    parser.add_argument('--output-dir', default='.', help='Output directory for generated files')
    
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load YAML files
    openapi_spec = load_yaml_file(args.openapi_spec)
    config = load_yaml_file(args.config)

    # Copy openapi spec file and config file to output directory
    subprocess.run(["cp", args.openapi_spec, args.output_dir])
    subprocess.run(["cp", args.config, args.output_dir])

    # Change to output directory
    os.chdir(args.output_dir)
    
    # Extract client name and setup directories
    client_name = openapi_spec['info']['title'].split(' ')[0]
    setup_directories(client_name)
    
    # Generate provider files
    generate_provider(openapi_spec, config)
    
    print(f"\nProvider generation complete. Files are in {os.path.abspath(args.output_dir)}")
    print(f"To build the provider, run: cd {args.output_dir} && go build -o terraform-provider-{client_name.lower()}")

if __name__ == "__main__":
    main()
