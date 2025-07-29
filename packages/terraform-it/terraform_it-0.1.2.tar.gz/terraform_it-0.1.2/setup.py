from setuptools import setup, find_packages

setup(
    name="terraform-it",
    version="0.1.2",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pyyaml>=6.0",
        "jinja2>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "tfit=terraform_it.cli:main",
        ],
    },
    python_requires=">=3.6",
    author="Deep Shah",
    author_email="shahdeep855@gmail.com",
    description="A tool to generate Terraform providers from OpenAPI specs and Go SDKs.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Deep070203/terraform-it",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={
        "terraform_it": ["templates/*", "templates/*/*"],
    },
)
