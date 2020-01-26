from setuptools import find_packages, setup

setup(
    name='service_discovery',
    version='1.0.0',
    packges=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ]
)
