from setuptools import setup, find_packages

setup(
    name='mbs_client',
    version='0.2.5',
    packages=find_packages(),
    install_requires=[
        'httplib2>=0.9',
        "makerpy>=0.1.8",
        "robustify>=0.1.0"
    ],
    dependency_links=[
        "https://github.com/objectlabs/maker-py/archive/0.1.8.zip#egg=makerpy-0.1.8",
        "https://github.com/objectlabs/robustify/archive/0.1.0.zip#egg=robustify-0.1.0"
    ]


)

