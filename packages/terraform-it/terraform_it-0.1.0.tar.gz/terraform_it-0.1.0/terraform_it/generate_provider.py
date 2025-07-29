from jinja2 import Template
import os
from typing import Dict, Any, List


def generate_provider(client: str, servers: List[Dict[str, str]], resources: Dict[str, Any], template: Template):
    context = {
        "client_name": client,
        "description": f"{client} API generated from the OpenAPI specification.",
        "resources": [resource.capitalize() for resource in list(resources.keys())],
        "servers": servers
    }

    output = template.render(**context)
    os.makedirs(f"{client.lower()}/provider", exist_ok=True)
    file_path = f"{client.lower()}/provider/provider.go"
    with open(file_path, 'w') as f:
        f.write(output)
    print("Provider generated successfully!")

# generate_provider(client, servers, get_resources)