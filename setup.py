from setuptools import setup, find_packages

setup(
    name='mbs_client',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'httplib2==0.7.2',
        "makerpy>=0.1.3"
    ],
    dependency_links=[
        "https://github.com/objectlabs/maker-py/archive/0.1.3.zip#egg=makerpy-0.1.3"
    ]


)

