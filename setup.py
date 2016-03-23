from setuptools import setup, find_packages

setup(
    name='mbs_client',
    version='0.3.0',
    packages=find_packages(),
    install_requires=[
        'httplib2>=0.9',
        "makerpy>=0.3.1",
        "robustify>=0.1.0"
    ],
    dependency_links=[
        "https://github.com/objectlabs/maker-py/archive/0.3.1.zip#egg=makerpy-0.3.1",
        "https://github.com/objectlabs/robustify/archive/0.1.0.zip#egg=robustify-0.1.0"
    ]


)

