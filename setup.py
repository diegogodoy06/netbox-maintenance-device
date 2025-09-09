from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='netbox-maintenance-device',
    version='1.0.0',
    description='NetBox plugin for device maintenance management',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Diego Godoy',
    license='Apache 2.0',
    install_requires=[
        # NetBox já inclui django-filter e django-tables2
        # Adicione apenas dependências específicas do seu plugin se necessário
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
)