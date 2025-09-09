from setuptools import find_packages, setup

setup(
    name='netbox-maintenance-device',
    version='1.0.0',
    description='NetBox plugin for device maintenance management',
    author='Diego Godoy',
    license='Apache 2.0',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)