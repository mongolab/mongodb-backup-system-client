from setuptools import setup, find_packages

setup(
    name='mbs_client',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'httplib2==0.7.2',
        "maker_py==0.1.2"
    ],
    dependency_links=[
        "https://github.com/objectlabs/maker-py/archive/master.zip#egg=maker_py-0.1.2"
    ]


)

