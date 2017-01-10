from setuptools import setup, find_packages

setup(
    name='mbs_client',
    version='0.3.5',
    packages=find_packages(),
    install_requires=[
        "makerpy>=0.3.4",
        "robustify>=0.1.0",
        "carbonio_client==0.2.2"
    ],
    dependency_links=[
        "https://github.com/objectlabs/maker-py/archive/0.3.4.zip#egg=makerpy-0.3.4",
        "https://github.com/objectlabs/robustify/archive/0.1.0.zip#egg=robustify-0.1.0",
        "git+ssh://git@github.com/carbon-io/carbon-client-py.git@0.2.2#egg=carbonio_client-0.2.2"

    ]


)

