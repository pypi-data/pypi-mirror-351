# Terraform Provider Generator

This tool generates a Terraform provider from an OpenAPI specification and a configuration file.

## Prerequisites

- Python 3.6+
- Go 1.16+
- Terraform 1.0+
- GoReleaser (optional, for building and releasing the provider)
- jinja2 (Python package)
- pyyaml (Python package)

## Installation

2. Install required Python package:

```bash
pip install terraform-it
```

## Usage

```bash
tfit openapi-spec.yaml config.yaml --output-dir ./terraform-provider-rivet
```

### Arguments

- `openapi_spec.yml`: Path to the OpenAPI specification YAML file
- `config.yml`: Path to the configuration YAML file that defines resources and data sources
- `--output-dir`: (Optional) Output directory for generated files (default: current directory)

## Configuration File Format

The configuration file (`config.yml`) should define resources and data sources in the following format:

```yaml
sdk-client-path: SDKClientPath
resources:
  ResourceName:
    resource-path: ResourcePath in SDK
    read:
      method: get
      name: FunctionName in SDK
      path: /path/to/resource/{id}
    create:
      method: post
      name: FunctionName in SDK
      path: /path/to/resource
    update:
      method: put
      name: FunctionName in SDK
      path: /path/to/resource/{id}
    delete:
      method: delete
      name: FunctionName in SDK
      path: /path/to/resource/{id}

datasources:
  DatasourceName:
    read: /path/to/resource/{id}
    list: /path/to/resources
    list-name: FunctionName in SDK
```

## Building the Provider

After generating the provider code, check the `CHECK.md` file for any manual changes or additions required. 
Then you can build it with:

```bash
cd <output_directory>
go build -o terraform-provider-<provider_name>
```

## Using the Provider

To use the provider in Terraform:

1. Copy the built provider to your Terraform plugins directory
2. Create a Terraform configuration file that uses the provider
3. Run `terraform init` to initialize the provider
4. Run `terraform plan` and `terraform apply` to use the provider