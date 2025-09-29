from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='netbox-maintenance-device',  # Nome com hífen para PyPI
    version='1.2.1',
    description='NetBox plugin for device maintenance management with comprehensive REST API and Portuguese-BR support',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Diego Godoy',
    author_email='diegoalex-gdy@outlook.com',
    url='https://github.com/diegogodoy06/netbox-maintenance-device',
    project_urls={
        'Homepage': 'https://github.com/diegogodoy06/netbox-maintenance-device',
        'Bug Reports': 'https://github.com/diegogodoy06/netbox-maintenance-device/issues',
        'Source': 'https://github.com/diegogodoy06/netbox-maintenance-device',
        'Documentation': 'https://github.com/diegogodoy06/netbox-maintenance-device/blob/main/README.md',
        'Changelog': 'https://github.com/diegogodoy06/netbox-maintenance-device/releases',
    },
    license='Apache-2.0',
    keywords=['netbox', 'plugin', 'maintenance', 'device', 'preventive', 'corrective', 'api', 'rest', 'automation'],
    install_requires=[
        # NetBox já inclui django-filter e django-tables2
        # Adicione apenas dependências específicas do seu plugin se necessário
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
)